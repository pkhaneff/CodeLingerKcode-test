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
        while curr in COUPONS_DB and curr not in chain:
            chain.append(curr)
            curr = COUPONS_DB[curr]["parent"]
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
        import ast
        try:
            tree = ast.parse(formula, mode='eval')
            allowed_nodes = (
                ast.Expression,
                ast.BinOp,
                ast.UnaryOp,
                ast.Num,
                ast.Constant,
                ast.Name,
                ast.Load,
                ast.Add, ast.Sub, ast.Mult, ast.Div, ast.USub, ast.UAdd
            )
            for node in ast.walk(tree):
                if not isinstance(node, allowed_nodes):
                    raise ValueError(f"Unsafe node type: {type(node).__name__}")
                if isinstance(node, ast.Name):
                    if node.id != "price":
                        raise ValueError(f"Unsafe variable: {node.id}")
            code = compile(tree, '<string>', 'eval')
            return float(eval(code, {"__builtins__": None}, {"price": price}))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Formula error: {str(e)}")

    @staticmethod
    def apply_discount(body: DiscountRequest) -> Dict[str, Any]:
        if not body.username or not body.product_ids:
            raise HTTPException(status_code=400, detail="Invalid request parameters")

        log_entry = {
            "user": body.username,
            "products": body.product_ids,
            "coupon": body.coupon_code,
            "raw_request": body.dict()
        }
        if len(APPLIED_COUPONS_LOG) >= 1000:
            APPLIED_COUPONS_LOG.pop(0)
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
