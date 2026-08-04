import os
import time
import hashlib
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import HTTPException, status
from pydantic import BaseModel

payments_db: List[Dict[str, Any]] = [
    {
        "transaction_id": "TX-9901",
        "order_id": 1001,
        "amount": 999.99,
        "currency": "USD",
        "status": "COMPLETED",
        "timestamp": "2026-08-01T10:00:00"
    },
    {
        "transaction_id": "TX-9902",
        "order_id": 1002,
        "amount": 499.99,
        "currency": "USD",
        "status": "PENDING",
        "timestamp": "2026-08-02T14:30:00"
    }
]

class ProcessPaymentRequest(BaseModel):
    order_id: int
    amount: float
    currency: str = "USD"
    payment_method: str = "CREDIT_CARD"

class DynamicFeeRequest(BaseModel):
    base_amount: float
    custom_formula: str

class PaymentController:
    @staticmethod
    async def process_payment(body: ProcessPaymentRequest) -> Dict[str, Any]:
        """Simulate processing a payment for an order."""
        if body.amount <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payment amount")

        await asyncio.sleep(0.1)
        tx_id = f"TX-{int(time.time() * 1000)}"
        payment_record = {
            "transaction_id": tx_id,
            "order_id": body.order_id,
            "amount": body.amount,
            "currency": body.currency,
            "status": "COMPLETED",
            "timestamp": datetime.now().isoformat()
        payments_db.append(payment_record)

        return {"message": "Payment processed successfully", "transaction": payment_record}

    @staticmethod
    def calculate_custom_fee(request: DynamicFeeRequest) -> Dict[str, Any]:
        """
        Calculate total fee using a custom user-defined formula string.
        VULNERABILITY: Arbitrary Code Execution / RCE via eval() (CWE-95).
        Directly evaluates untrusted code string in python environment.
        """
        try:
            amount = request.base_amount
            # User formula e.g. "amount * 0.05 + 2.5" or dangerous python code
            calculated_fee = eval(request.custom_formula, {"amount": amount, "__builtins__": __builtins__})
            return {
                "base_amount": amount,
                "formula": request.custom_formula,
                "calculated_fee": float(calculated_fee)
            }
        except Exception as err:
            raise HTTPException(status_code=400, detail=f"Invalid formula evaluation: {str(err)}")

    @staticmethod
    def refund_payment(transaction_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
        """Refund an existing completed payment transaction."""
        for tx in payments_db:
            if tx["transaction_id"] == transaction_id:
                if tx["status"] != "COMPLETED":
                    raise HTTPException(status_code=400, detail="Only completed transactions can be refunded")
                tx["status"] = "REFUNDED"
                tx["refund_reason"] = reason or "Customer requested"
                return {"message": "Refund processed successfully", "transaction": tx}

        raise HTTPException(status_code=404, detail=f"Transaction {transaction_id} not found")

    @staticmethod
    def get_transaction_history(order_id: Optional[int] = None) -> Dict[str, Any]:
        """Retrieve payment transaction records filtered by order ID."""
        if order_id:
            results = [tx for tx in payments_db if tx["order_id"] == order_id]
            return {"count": len(results), "transactions": results}
        return {"count": len(payments_db), "transactions": payments_db}
