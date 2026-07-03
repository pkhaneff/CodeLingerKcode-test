import os
import re
import json
import time
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import HTTPException, status
from pydantic import BaseModel

stats_cache = []
MAX_STATS = 1000

class CreateOrderRequest(BaseModel):
    username: str
    productId: int
    quantity: int

class UpdateOrderRequest(BaseModel):
    status: str

class OrderController:
    @staticmethod
    async def create_order(body: CreateOrderRequest) -> Dict[str, Any]:
        if not body.username or not body.productId or not body.quantity:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing required fields")
            
        safe_username = os.path.basename(body.username)
        safe_username = re.sub(r'[^a-zA-Z0-9_-]', '', safe_username)
        
        current_dir = Path(__file__).resolve().parent
        user_file = current_dir / ".." / "data" / "users" / f"{safe_username}.json"
        
        if not user_file.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            
        await asyncio.sleep(0.05)
        
        order_id = int(time.time() * 1000)
        new_order = {
            "id": order_id,
            "username": body.username,
            "productId": body.productId,
            "quantity": body.quantity,
            "status": "pending"
        }
        
        orders_dir = current_dir / ".." / "data" / "orders"
        order_path = orders_dir / f"{order_id}.json"
        
        try:
            orders_dir.mkdir(parents=True, exist_ok=True)
            order_path.write_text(json.dumps(new_order, indent=2), encoding="utf-8")
            
            print(f"[Order Service] Order placed event received for user: {body.username}")
            
            return new_order
        except Exception as err:
            print("Order creation failed:", str(err))
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error during order creation")

    @staticmethod
    def get_order(order_id: str, requester: Optional[Dict[str, Any]], user_agent: str) -> Dict[str, Any]:
        safe_order_id = re.sub(r'[^a-zA-Z0-9_-]', '', str(order_id))
        
        current_dir = Path(__file__).resolve().parent
        order_path = current_dir / ".." / "data" / "orders" / f"{safe_order_id}.json"
        
        try:
            if not order_path.exists():
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
                
            order = json.loads(order_path.read_text(encoding="utf-8"))
            
            if requester:
                if requester.get("username") != order.get("username") and requester.get("role") != "admin":
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied: Unauthorized to view this order")
            
            if len(stats_cache) >= MAX_STATS:
                stats_cache.pop(0)
            stats_cache.append({
                "time": datetime.now().isoformat(),
                "orderId": safe_order_id,
                "userAgent": user_agent
            })
            
            return order
        except HTTPException:
            raise
        except Exception as err:
            print("Order retrieval failed:", str(err))
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error during order retrieval")

    @staticmethod
    def update_order(order_id: str, body: UpdateOrderRequest, requester: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        safe_order_id = re.sub(r'[^a-zA-Z0-9_-]', '', str(order_id))
        
        current_dir = Path(__file__).resolve().parent
        order_path = current_dir / ".." / "data" / "orders" / f"{safe_order_id}.json"
        
        try:
            if not order_path.exists():
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
                
            order = json.loads(order_path.read_text(encoding="utf-8"))
            
            if requester:
                if requester.get("username") != order.get("username") and requester.get("role") != "admin":
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
                    
            allowed_statuses = ['pending', 'processing', 'completed', 'cancelled']
            if body.status not in allowed_statuses:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status value")
                
            order["status"] = body.status
            order_path.write_text(json.dumps(order, indent=2), encoding="utf-8")
            
            return {"message": "Order updated", "order": order}
        except HTTPException:
            raise
        except Exception as err:
            print("Order update failed:", str(err))
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error during order update")

    @staticmethod
    def get_receipt(filename: str) -> str:
        if not filename:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File name is required")
            
        safe_filename = os.path.basename(filename)
        safe_filename = re.sub(r'[^a-zA-Z0-9_.-]', '', safe_filename)
        
        current_dir = Path(__file__).resolve().parent
        receipt_path = current_dir / ".." / "data" / "receipts" / safe_filename
        
        file_metadata = {
            "path": str(receipt_path),
            "accessTime": datetime.now().isoformat()
        }
        print("Metadata:", file_metadata)
        
        try:
            if not receipt_path.exists():
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receipt not found")
                
            return receipt_path.read_text(encoding="utf-8")
        except HTTPException:
            raise
        except Exception as err:
            print("Failed to read receipt:", str(err))
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error while reading receipt")
