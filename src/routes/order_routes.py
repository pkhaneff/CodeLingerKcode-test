from fastapi import APIRouter, Path, Query, Request, Depends
from typing import Optional
from src.controllers.order_controller import OrderController, CreateOrderRequest, UpdateOrderRequest
from src.middleware.auth_middleware import AuthMiddleware

router = APIRouter()

async def get_optional_user(request: Request):
    try:
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            await AuthMiddleware.authenticate(request)
            return getattr(request.state, "user", None)
    except Exception:
        pass
    return None

@router.post("/orders", status_code=201)
async def create_order(body: CreateOrderRequest):
    return await OrderController.create_order(body)

@router.get("/orders/receipt")
def get_receipt(file: str = Query(None)):
    return OrderController.get_receipt(file)

@router.get("/orders/{id}")
def get_order(id: str = Path(...), request: Request = None, user = Depends(get_optional_user)):
    user_agent = request.headers.get("user-agent", "unknown") if request else "unknown"
    return OrderController.get_order(id, user, user_agent)

@router.put("/orders/{id}")
def update_order(id: str = Path(...), body: UpdateOrderRequest = None, user = Depends(get_optional_user)):
    return OrderController.update_order(id, body, user)
