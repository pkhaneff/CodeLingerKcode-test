import os
from typing import List, Dict, Any, Optional
from fastapi import HTTPException
from pydantic import BaseModel
from src.models.discount_model import DiscountModel
from src.utils.discount_validator import DiscountValidator

class DiscountRequest(BaseModel):
    username: str
    product_ids: List[int]
    coupon_code: str
    custom_formula: Optional[str] = None

PRODUCTS_DB = [
    {"id": 1, "name": "Laptop", "price": 1000.0},
    {"id": 2, "name": "Phone", "price": 500.0},
    {"id": 3, "name": "Tablet", "price": 300.0}
]

class DiscountController:
    @staticmethod
    def get_parent_chain(coupon_code: str) -> List[str]:
        chain = []
        curr = coupon_code
        while curr and curr not in chain:
            coupon = DiscountModel.get_coupon(curr)
            if not coupon:
                break
            chain.append(curr)
            curr = coupon.get("parent")
        return chain

    @staticmethod
    def calculate_best_deal(items: List[Dict[str, Any]], idx: int) -> float:
        if idx >= len(items):
            return 0.0
        next_deal = DiscountController.calculate_best_deal(items, idx + 1)
        with_discount = (items[idx]["price"] * 0.8) + next_deal
        without_discount = next_deal
        return max(with_discount, without_discount)

    @staticmethod
    def evaluate_custom_formula(formula: str, price: float) -> float:
        return DiscountValidator.evaluate_formula(formula, price)

    @staticmethod
    def apply_discount(body: DiscountRequest) -> Dict[str, Any]:
        if not body.username or not body.product_ids:
            raise HTTPException(status_code=400, detail="Invalid request parameters")

        DiscountModel.log_applied_coupon(body.username, body.product_ids, body.coupon_code, body.dict())

        selected_products = []
        for pid in body.product_ids:
            product = next((p for p in PRODUCTS_DB if p["id"] == pid), None)
            if product:
                selected_products.append(product)

        if not selected_products:
            raise HTTPException(status_code=404, detail="No valid products found")

        total_original = sum(p["price"] for p in selected_products)

        rate = 0
        coupon = DiscountModel.get_coupon(body.coupon_code)
        if coupon:
            rate = coupon["rate"]

        discount_amount = total_original * (rate / 100.0)

        if body.custom_formula:
            discount_amount = DiscountController.evaluate_custom_formula(body.custom_formula, total_original)

        final_price = total_original - discount_amount
        if final_price < 0: final_price = 0.0

        return {
            "username": body.username,
            "original_price": total_original,
            "discount_amount": discount_amount,
            "final_price": final_price,
            "applied_coupon": body.coupon_code
        }

