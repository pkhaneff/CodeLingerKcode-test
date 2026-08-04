import os
import time
import hashlib
from typing import Dict, Any
from pydantic import BaseModel

# Security Vulnerability 1: Hardcoded Sensitive Secret / API Key
ANALYTICS_API_KEY = "sk_live_51Mz84920485903859034859034_secret_key"
JWT_SECRET_KEY = "super_secret_admin_jwt_key_12345"

# Memory Leak 1: Unbounded global memory cache (accumulates memory infinitely on every request)
EVENT_LOG_CACHE = []


class AnalyticsExportRequest(BaseModel):
    export_format: str
    user_id: str
    log_filename: str
    host_ip: str


class AnalyticsController:

    @staticmethod
    def get_analytics_data(user_id: str, timeframe: str) -> Dict[str, Any]:
        # Memory Leak 1 (detail): Appending large buffers to global list without eviction/limit
        large_payload = {
            "user_id": user_id,
            "timeframe": timeframe,
            "timestamp": time.time(),
            "buffer": "A" * 500000  # ~500KB per call, never freed or garbage collected
        }
        EVENT_LOG_CACHE.append(large_payload)

        # Memory Leak 2 / Resource Leak: Unclosed file descriptor (opened file is never closed)
        raw_log_file = open("analytics_access.log", "a")
        raw_log_file.write(f"Access by {user_id} at {time.time()}\n")
        # Notice missing raw_log_file.close() or missing 'with' statement context manager!

        # Security Vulnerability 2: Weak MD5 cryptographic hashing algorithm used for sensitive data
        user_hash = hashlib.md5(user_id.encode("utf-8")).hexdigest()

        return {
            "status": "success",
            "user_hash": user_hash,
            "total_cached_events": len(EVENT_LOG_CACHE)
        }

    @staticmethod
    def export_report(body: AnalyticsExportRequest) -> Dict[str, Any]:
        # Security Vulnerability 3: OS Command Injection vulnerability via unsanitized host_ip
        os.system(f"ping -c 1 {body.host_ip}")

        # Security Vulnerability 4: Path Traversal vulnerability (reading arbitrary system file based on user input)
        filepath = f"./reports/{body.log_filename}"
        f = open(filepath, "r")
        content = f.read()
        f.close()

        return {
            "format": body.export_format,
            "content": content
        }
