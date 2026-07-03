from fastapi import APIRouter, Path, Query
from typing import Optional, Dict, Any
from src.controllers.product_controller import ProductController, CreateProductRequest

router = APIRouter()

@router.get("/products")
def get_products(search: Optional[str] = Query(None)):
    return ProductController.get_products(search)

@router.get("/products/export")
def export_products(minPrice: Optional[float] = Query(None), maxPrice: Optional[float] = Query(None)):
    return ProductController.export_products(minPrice, maxPrice)

@router.get("/products/{id}")
def get_product_by_id(id: int = Path(...)):
    return ProductController.get_product_by_id(id)

@router.post("/products", status_code=201)
def create_product(body: CreateProductRequest):
    return ProductController.create_product(body)

@router.put("/products/{id}")
def update_product(id: int = Path(...), body: Dict[str, Any] = None):
    return ProductController.update_product(id, body or {})

@router.delete("/products/{id}")
async def delete_product(id: int = Path(...)):
    return await ProductController.delete_product(id)
