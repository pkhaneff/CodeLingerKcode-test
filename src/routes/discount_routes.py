from fastapi import APIRouter, HTTPException, Query, Body
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from src.controllers.discount_controller import DiscountController, DiscountRequest
from src.models.discount_model import DiscountModel
from src.utils.discount_validator import DiscountValidator

router = APIRouter()

class AddCouponRequest(BaseModel):
    code: str
    rate: int
    parent: Optional[str] = None

@router.post("/discounts/apply")
def apply_discount(body: DiscountRequest):
    """Apply a coupon code or a custom formula to a list of products."""
    return DiscountController.apply_discount(body)

@router.get("/discounts/coupons")
def list_coupons():
    """List all registered discount coupons."""
    return DiscountModel.list_all_coupons()

@router.post("/discounts/coupons", status_code=201)
def add_new_coupon(body: AddCouponRequest):
    """Create a new discount coupon with custom rate and optional parent."""
    DiscountValidator.validate_coupon_rate(body.rate)
    success = DiscountModel.add_coupon(body.code, body.rate, body.parent)
    if not success:
        raise HTTPException(status_code=400, detail=f"Coupon {body.code} already exists")
    return {"message": f"Coupon {body.code} successfully added"}

@router.get("/discounts/parent-chain/{code}")
def get_parent_chain(code: str):
    """Get the inheritance hierarchy/chain of a given coupon code."""
    chain = DiscountController.get_parent_chain(code)
    if not chain:
        raise HTTPException(status_code=404, detail=f"Coupon {code} not found in database")
    return {"coupon": code, "chain": chain}

@router.get("/discounts/logs")
def get_discount_logs():
    """Retrieve history of all applied discount logs."""
    return DiscountModel.get_logs()
