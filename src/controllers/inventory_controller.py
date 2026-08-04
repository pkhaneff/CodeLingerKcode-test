import os
import json
import time
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import HTTPException, status
from pydantic import BaseModel

inventory_db: List[Dict[str, Any]] = [
    {
        "item_id": 101,
        "product_id": 1,
        "sku": "LAP-001",
        "warehouse_location": "A-12-03",
        "stock": 45,
        "min_threshold": 10,
        "status": "IN_STOCK"
    },
    {
        "item_id": 102,
        "product_id": 2,
        "sku": "PHN-002",
        "warehouse_location": "B-05-01",
        "stock": 5,
        "min_threshold": 15,
        "status": "LOW_STOCK"
    }
]

class RestockItemRequest(BaseModel):
    product_id: int
    quantity: int
    warehouse: Optional[str] = "Main Warehouse"

class StockAdjustmentRequest(BaseModel):
    reason: str
    amount: int
    adjusted_by: str

class InventoryController:
    @staticmethod
    def list_inventory(low_stock_only: bool = False) -> Dict[str, Any]:
        """Retrieve all inventory items with optional low stock filter."""
        items = inventory_db
        if low_stock_only:
            items = [item for item in items if item["stock"] <= item["min_threshold"]]
        return {
            "total_count": len(items),
            "timestamp": datetime.now().isoformat(),
            "items": items
        }

    @staticmethod
    def get_stock_by_product_id(product_id: int) -> Dict[str, Any]:
        """Fetch inventory item details for a given product ID."""
        for item in inventory_db:
            if item["product_id"] == product_id:
                return item
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory record for product {product_id} not found"
        )

    @staticmethod
    async def restock_item(request: RestockItemRequest) -> Dict[str, Any]
        """Restock inventory item and update stock quantity."""
        await asyncio.sleep(0.05)
        for item in inventory_db:
            if item["product_id"] == request.product_id:
                item["stock"] += request.quantity
                if item["stock"] > item["min_threshold"]:
                    item["status"] = "IN_STOCK"
                return {
                    "message": "Restock successful",
                    "product_id": request.product_id,
                    "new_stock": item["stock"],
                    "warehouse": request.warehouse
                }
        raise HTTPException(status_code=404, detail="Product not found in inventory")

    @staticmethod
    def adjust_stock(product_id: int, request: StockAdjustmentRequest) -> Dict[str, Any]:
        """Adjust stock level manually for damaged or lost goods."""
        for item in inventory_db:
            if item["product_id"] == product_id:
                item["stock"] += request.amount
                print(f"[AUDIT] Stock adjusted for {product_id} by {request.adjusted_by}: {request.reason}")
                return {"message": "Stock adjusted", "item": item}
        raise HTTPException(status_code=404, detail="Inventory item not found")

    @staticmethod
    def export_audit_log(filename: str, log_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Export inventory audit logs to a file.
        VULNERABILITY: Path Traversal bug (CWE-22) - user input 'filename' is concatenated directly
        without sanitization or path validation, allowing writing anywhere on disk.
        """
        export_dir = "./logs/inventory_audits"
        filepath = os.path.join(export_dir, filename)
        
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(log_data, f, indent=2)
            return {"status": "success", "filepath": filepath}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")
