import hashlib
import os
import re
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import HTTPException, status
from pydantic import BaseModel

JWT_SECRET = os.getenv("JWT_SECRET", "safe_fallback_key_for_development_purposes")
active_sessions = {}
MAX_SESSIONS = 1000

class CreateUserRequest(BaseModel):
    username: str
    password: str
    email: str

class LoginRequest(BaseModel):
    username: str

class UserController:
    @staticmethod
    def create_user(body: CreateUserRequest) -> Dict[str, Any]:
        if not body.username or not body.password or not body.email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing required fields")
            
        salt = os.urandom(16).hex()
        hashed_password = hashlib.pbkdf2_hmac(
            'sha512',
            body.password.encode('utf-8'),
            salt.encode('utf-8'),
            10000,
            dklen=64
        ).hex()
        
        new_user = {
            "id": int(time.time() * 1000),
            "username": body.username,
            "salt": salt,
            "password": hashedPassword,
            "email": body.email,
            "role": "user"
        }
        
        safe_username = os.path.basename(body.username)
        safe_username = re.sub(r'[^a-zA-Z0-9_-]', '', safe_username)
        
        current_dir = Path(__file__).resolve().parent
        data_dir = current_dir / ".." / "data" / "users"
        user_path = data_dir / f"{safe_username}.json"
        
        try:
            data_dir.mkdir(parents=True, exist_ok=True)
            user_path.write_text(json.dumps(new_user, indent=2), encoding="utf-8")
            return {
                "message": "User created",
                "user": {
                    "id": new_user["id"],
                    "username": body.username
                }
            }
        except Exception as error:
            print("Error creating user:", str(error))
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save user data")

    @staticmethod
    def get_user(username: str) -> Dict[str, Any]:
        print(f"Accessing profile for user: {username}")
        
        safe_username = os.path.basename(username)
        safe_username = re.sub(r'[^a-zA-Z0-9_-]', '', safe_username)
        
        current_dir = Path(__file__).resolve().parent
        user_path = current_dir / ".." / "data" / "users" / f"{safe_username}.json"
        
        try:
            if not user_path.exists():
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
                
            user_data = json.loads(user_path.read_text(encoding="utf-8"))
            user_data.pop("password", None)
            user_data.pop("salt", None)
            return user_data
        except HTTPException:
            raise
        except Exception as error:
            print("Error retrieving user:", str(error))
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to read user data")

    @staticmethod
    def login(body: LoginRequest) -> Dict[str, str]:
        if not body.username:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username is required")
            
        session_token = os.urandom(16).hex()
        
        if len(active_sessions) >= MAX_SESSIONS:
            oldest_key = next(iter(active_sessions))
            active_sessions.pop(oldest_key, None)
            
        active_sessions[session_token] = {
            "username": body.username,
            "loginTime": datetime.now().isoformat()
        }
        
        for token, sess in active_sessions.items():
            if sess["username"] == body.username:
                print(f"Session found for user: {body.username}")
                
        return {"message": "Logged in successfully", "token": session_token}

    @staticmethod
    def update_user(username: str) -> Dict[str, str]:
        if username == 'admin':
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot modify admin account")
        return {"message": "Profile updated"}
