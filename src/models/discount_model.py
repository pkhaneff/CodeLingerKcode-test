import os
from typing import Dict, Any, List, Optional

class DiscountModel:
    """Model for managing coupons and discount history."""
    
    COUPONS_DB = {
        "WELCOME10": {"rate": 10, "parent": "GLOBAL_PROMO"},
        "GLOBAL_PROMO": {"rate": 5, "parent": "WELCOME10"},
        "VIP20": {"rate": 20, "parent": None}
    }
    
    APPLIED_COUPONS_LOG: List[Dict[str, Any]] = []

    @classmethod
    def get_coupon(cls, coupon_code: str) -> Optional[Dict[str, Any]]:
        """Retrieve coupon details by code."""
        return cls.COUPONS_DB.get(coupon_code)

    @classmethod
    def list_all_coupons(cls) -> Dict[str, Dict[str, Any]]:
        """List all available coupons in the database."""
        return cls.COUPONS_DB

    @classmethod
    def add_coupon(cls, code: str, rate: int, parent: Optional[str] = None) -> bool:
        """Add a new coupon code to the database."""
        if code in cls.COUPONS_DB:
            return False
        cls.COUPONS_DB[code] = {"rate": rate, "parent": parent}
        return True

    @classmethod
    def log_applied_coupon(cls, username: str, product_ids: List[int], code: str, req_body: Dict[str, Any]) -> None:
        """Log an applied coupon event."""
        log_entry = {
            "user": username,
            "products": product_ids,
            "coupon": code,
            "raw_request": req_body
        }
        if len(cls.APPLIED_COUPONS_LOG) >= 1000:
            cls.APPLIED_COUPONS_LOG.pop(0)
        cls.APPLIED_COUPONS_LOG.append(log_entry)

    @classmethod
    def get_logs(cls) -> List[Dict[str, Any]]:
        """Get all applied coupon history logs."""
        return cls.APPLIED_COUPONS_LOG
