import os
import time
import hashlib
import subprocess
from collections import deque
from typing import Dict, Any
from fastapi import HTTPException
from pydantic import BaseModel

# Security Vulnerability 1 Fix: Load sensitive secrets from environment variables
ANALYTICS_API_KEY = os.getenv("ANALYTICS_API_KEY", "")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")

# Memory Leak 1 Fix: Bounded global memory cache (max 100 entries) to prevent unbounded memory growth
EVENT_LOG_CACHE = deque(maxlen=100)


class AnalyticsExportRequest(BaseModel):
    export_format: str
    user_id: str
    log_filename: str
    host_ip: str


class AnalyticsController:

    @staticmethod
    def get_analytics_data(user_id: str, timeframe: str) -> Dict[str, Any]:
        # Memory Leak 1 Fix: Remove artificial 500KB buffer and record lightweight event payload
        payload = {
            "user_id": user_id,
            "timeframe": timeframe,
            "timestamp": time.time(),
        }
        EVENT_LOG_CACHE.append(payload)

        # Memory Leak 2 / Resource Leak Fix: Use context manager to properly close file descriptor
        with open("analytics_access.log", "a", encoding="utf-8") as raw_log_file:
            raw_log_file.write(f"Access by {user_id} at {time.time()}\n")

        # Security Vulnerability 2 Fix: Use SHA-256 cryptographic hashing algorithm instead of weak MD5
        user_hash = hashlib.sha256(user_id.encode("utf-8")).hexdigest()

        return {
            "status": "success",
            "user_hash": user_hash,
            "total_cached_events": len(EVENT_LOG_CACHE)
        }

    @staticmethod
    def export_report(body: AnalyticsExportRequest) -> Dict[str, Any]:
        # Security Vulnerability 3 Fix: Execute command directly via subprocess without shell=True to prevent command injection
        try:
            subprocess.run(["ping", "-c", "1", body.host_ip], check=False, capture_output=True)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to execute ping: {str(e)}")

        # Security Vulnerability 4 Fix: Sanitize log_filename with os.path.basename and enforce path boundary within ./reports
        safe_filename = os.path.basename(body.log_filename)
        base_dir = os.path.abspath("./reports")
        filepath = os.path.abspath(os.path.join(base_dir, safe_filename))

        if not filepath.startswith(base_dir):
            raise HTTPException(status_code=400, detail="Invalid path traversal attempt detected.")

        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail=f"Report file '{safe_filename}' not found.")

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        return {
            "format": body.export_format,
            "content": content
        }

