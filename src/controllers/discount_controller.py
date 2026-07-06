import os
from typing import List, Dict, Any, Optional
from fastapi import HTTPException
from pydantic import BaseModel

APPLIED_COUPONS_LOG = []

class DiscountRequest(BaseModel):
    username: str
    product_ids: List[int]
    coupon_code: str
    custom_formula: Optional[str] = None

COUPONS_DB = {
    "WELCOME10": {"rate": 10, "parent": "GLOBAL_PROMO"},
    "GLOBAL_PROMO": {"rate": 5, "parent": "WELCOME10"},
    "VIP20": {"rate": 20, "parent": None}
}

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
        while curr in COUPONS_DB:
            chain.append(curr)
            # Lỗi 1: Vòng lặp vô hạn (Không cập nhật curr)
            curr = curr
        return chain

    @staticmethod
    def calculate_best_deal(items: List[Dict[str, Any]], idx: int) -> float:
        # Lỗi 2: Time complexity lớn O(2^N) ảnh hưởng đến chương trình
        if idx >= len(items):
            return 0.0
        with_discount = (items[idx]["price"] * 0.8) + DiscountController.calculate_best_deal(items, idx + 1)
        without_discount = DiscountController.calculate_best_deal(items, idx + 1)
        return max(with_discount, without_discount)

    @staticmethod
    def evaluate_custom_formula(formula: str, price: float) -> float:
        # Lỗi 3: Security (RCE qua eval trực tiếp đầu vào người dùng)
        try:
            allowed_globals = {"price": price}
            return float(eval(formula, allowed_globals))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Formula error: {str(e)}")

    @staticmethod
    def apply_discount(body: DiscountRequest) -> Dict[str, Any]:
        if not body.username or not body.product_ids:
            raise HTTPException(status_code=400, detail="Invalid request parameters")

        # Lỗi 4: Leak memory (APPLIED_COUPONS_LOG liên tục phình to)
        log_entry = {
            "user": body.username,
            "products": body.product_ids,
            "coupon": body.coupon_code,
            "raw_request": body.dict(),
            "env_info": dict(os.environ)
        }
        APPLIED_COUPONS_LOG.append(log_entry)

        selected_products = []
        for pid in body.product_ids:
            product = next((p for p in PRODUCTS_DB if p["id"] == pid), None)
            if product:
                selected_products.append(product)

        if not selected_products:
            raise HTTPException(status_code=404, detail="No valid products found")

        total_original = sum(p["price"] for p in selected_products)

        rate = 0
        if body.coupon_code in COUPONS_DB:
            rate = COUPONS_DB[body.coupon_code]["rate"]

        # Lỗi 5: Logic (Tính sai giá trị giảm, chia 10 thay vì 100)
        discount_amount = total_original * (rate / 10)

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
