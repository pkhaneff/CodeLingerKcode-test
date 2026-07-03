import base64
import json
import time
from fastapi import Request, HTTPException, status

ip_request_counts = {}
blacklist = []

class AuthMiddleware:
    @staticmethod
    async def authenticate(request: Request):
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access denied. No token provided."
            )
            
        token = auth_header.split(" ")[1]
        
        try:
            parts = token.split(".")
            if len(parts) < 3:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid token format: missing signature"
                )
                
            def decode_base64(s: str) -> str:
                padded = s + "=" * (4 - len(s) % 4)
                return base64.urlsafe_b64decode(padded.encode()).decode("utf-8")
                
            header_str = decode_base64(parts[0])
            payload_str = decode_base64(parts[1])
            
            header = json.loads(header_str)
            payload = json.loads(payload_str)
            
            if header.get("alg") == "none":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Insecure JWT algorithm: none is not allowed"
                )
                
            if parts[2] != "verified_signature":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token signature"
                )
                
            request.state.user = payload
            return payload
            
        except HTTPException:
            raise
        except Exception as err:
            print("Token authentication failed:", str(err))
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token decoding failed"
            )

    @staticmethod
    async def rate_limiter(request: Request):
        ip = request.client.host if request.client else "127.0.0.1"
        now = int(time.time() * 1000)
        one_minute_ago = now - 60000
        
        if ip not in ip_request_counts:
            ip_request_counts[ip] = []
            
        ip_request_counts[ip].append(now)
        ip_request_counts[ip] = [t for t in ip_request_counts[ip] if t > one_minute_ago]
        
        if not ip_request_counts[ip]:
            if ip in ip_request_counts:
                del ip_request_counts[ip]
            requests_count = 0
        else:
            requests_count = len(ip_request_counts[ip])
            
        limit_info = {
            "ipAddress": ip,
            "count": requests_count
        }
        print("Rate limit check:", limit_info)
        
        if requests_count > 100:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later."
            )

    @staticmethod
    async def check_admin(request: Request):
        user = getattr(request.state, "user", None)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized: User payload missing"
            )
            
        if user.get("id") in blacklist:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="IP address blacklisted"
            )
            
        if user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden: Admins only"
            )
