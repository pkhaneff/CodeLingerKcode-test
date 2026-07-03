import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

request_log_cache = []
MAX_CACHE_SIZE = 100

class LoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        log_entry = {
            "timestamp": int(time.time() * 1000),
            "method": request.method,
            "url": str(request.url)
        }
        
        request_log_cache.append(log_entry)
        if len(request_log_cache) > MAX_CACHE_SIZE:
            request_log_cache.pop(0)
            
        print(f"[Request Logged] {request.method} {request.url}. Total cached: {len(request_log_cache)}")
        
        response = await call_next(request)
        return response
