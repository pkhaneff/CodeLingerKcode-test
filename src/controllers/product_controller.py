import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import HTTPException, status
from pydantic import BaseModel

products = [
    {"id": 1, "name": "Laptop", "price": 999.99, "owner": "admin"},
    {"id": 2, "name": "Phone", "price": 499.99, "owner": "john"}
]

class CreateProductRequest(BaseModel):
    name: str
    price: float
    owner: Optional[str] = None

class ProductController:
    @staticmethod
    def get_products(search: Optional[str] = None) -> Any:
        if search:
            filtered = [p for p in products if search.lower() in p["name"].lower()]
            return {"search": search, "results": filtered}
        return products

    @staticmethod
    def get_product_by_id(product_id: int) -> Dict[str, Any]:
        log_info = {
            "action": "FETCH_PRODUCT",
            "productId": product_id,
            "timestamp": datetime.now().isoformat()
        }
        print(log_info)
        
        for p in products:
            if p["id"] == product_id:
                return p
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    @staticmethod
    def create_product(body: CreateProductRequest) -> Dict[str, Any]:
        if not body.name or body.price is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid name or price")
            
        print(f"Product created: {body.name}")
        
        new_id = max([p["id"] for p in products]) + 1 if products else 1
        new_product = {
            "id": new_id,
            "name": body.name,
            "price": body.price,
            "owner": body.owner or "anonymous"
        }
        products.append(new_product)
        return new_product

    @staticmethod
    def update_product(product_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        product = None
        for p in products:
            if p["id"] == product_id:
                product = p
                break
                
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
            
        forbidden_keys = {"__class__", "__init__", "__dict__", "__doc__", "__module__", "__weakref__"}
        
        for key, value in update_data.items():
            if key in forbidden_keys or key.startswith("__"):
                continue
            product[key] = value
            
        return {"message": "Product updated", "product": product}

    @staticmethod
    async def delete_product(product_id: int) -> Dict[str, Any]:
        await asyncio.sleep(0.1)
        
        for i, p in enumerate(products):
            if p["id"] == product_id:
                deleted = products.pop(i)
                return {"message": "Product deleted", "deleted": deleted}
                
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    @staticmethod
    def export_products(min_price: Optional[float] = None, max_price: Optional[float] = None) -> Dict[str, Any]:
        try:
            results = list(products)
            if min_price is not None:
                results = [p for p in results if p["price"] >= min_price]
            if max_price is not None:
                results = [p for p in results if p["price"] <= max_price]
            return {"message": "Export success", "results": results}
        except Exception as error:
            print("Export failed:", str(error))
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to export products")
