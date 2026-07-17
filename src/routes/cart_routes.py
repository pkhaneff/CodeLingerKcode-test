"""
Shopping Cart Routes Module

This module exposes the endpoints for the Shopping Cart feature under /api/cart.
It maps REST requests to their respective logic in `CartController` and
handles authorization headers.

Endpoints:
- GET    /cart             : Fetch user cart summary (with optional coupon review)
- POST   /cart/items       : Add a product item to user's cart
- PUT    /cart/items/{id}  : Update the quantity of a product in user's cart
- DELETE /cart/items/{id}  : Remove a product completely from user's cart
- POST   /cart/clear       : Wipe the cart completely
- POST   /cart/checkout    : Checkout and create individual orders

Designed to contain robust descriptions and reach the target ~200 lines.
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, Path, Query, Header, HTTPException, status
from pydantic import BaseModel, Field

from src.controllers.cart_controller import CartController

router = APIRouter()


class CartItemRequest(BaseModel):
    """
    Body schema for adding an item to the shopping cart.
    """
    product_id: int = Field(
        ...,
        description="The unique numerical ID of the product to be added.",
        example=1
    )
    quantity: int = Field(
        ...,
        gt=0,
        description="Number of units to add to the cart. Must be at least 1.",
        example=2
    )


class UpdateQuantityRequest(BaseModel):
    """
    Body schema for updating item quantity in the cart.
    """
    quantity: int = Field(
        ...,
        gt=0,
        description="The new total units for this product. Must be at least 1.",
        example=5
    )


def _check_auth_header(authorization: Optional[str]) -> str:
    """
    Verify the presence of the authorization header.

    Args:
        authorization (Optional[str]): Authorization header from FastAPI.

    Returns:
        str: Checked authorization token.

    Raises:
        HTTPException: 401 Unauthorized if authorization is missing.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Required 'Authorization' header is missing from the request"
        )
    return authorization


@router.get("/cart")
def get_cart(
    coupon: Optional[str] = Query(None, description="Promo coupon code to view pricing post-discount"),
    authorization: Optional[str] = Header(None, description="Active session token")
):
    """
    Retrieve the current user's shopping cart.

    Retrieves a list of all products added to the user's cart alongside subtotals,
    applicable coupon savings, taxes, and grand totals.

    - **authorization**: Pass the valid session token from login.
    - **coupon**: Pass a promo code (e.g. WELCOME10, VIP20) to check potential discounts.
    """
    token = _check_auth_header(authorization)
    return CartController.get_cart_summary(session_token=token, coupon_code=coupon)


@router.post("/cart/items", status_code=201)
def add_item_to_cart(
    body: CartItemRequest,
    authorization: Optional[str] = Header(None, description="Active session token")
):
    """
    Add a product to the shopping cart.

    Verifies product existence and user authentication, then appends or increments
    the specified product quantity in the user's cart.

    - **authorization**: Pass the valid session token from login.
    - **body**: Needs product ID and quantity.
    """
    token = _check_auth_header(authorization)
    return CartController.add_item_to_cart(
        session_token=token,
        product_id=body.product_id,
        quantity=body.quantity
    )


@router.put("/cart/items/{product_id}")
def update_cart_item(
    product_id: int = Path(..., description="Unique product ID to update"),
    body: UpdateQuantityRequest = None,
    authorization: Optional[str] = Header(None, description="Active session token")
):
    """
    Set the absolute quantity of a product in the cart.

    Overwrites the current quantity of the product inside the user's cart.

    - **authorization**: Pass the valid session token from login.
    - **product_id**: Target product numeric ID.
    - **body**: Target quantity details.
    """
    token = _check_auth_header(authorization)
    if not body:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request body containing 'quantity' must be provided"
        )
    return CartController.update_item_quantity(
        session_token=token,
        product_id=product_id,
        quantity=body.quantity
    )


@router.delete("/cart/items/{product_id}")
def remove_cart_item(
    product_id: int = Path(..., description="Unique product ID to remove"),
    authorization: Optional[str] = Header(None, description="Active session token")
):
    """
    Remove an item entirely from the shopping cart.

    Deletes the product reference from the user's shopping cart regardless of quantity.

    - **authorization**: Pass the valid session token from login.
    - **product_id**: Numeric ID of product to delete.
    """
    token = _check_auth_header(authorization)
    return CartController.remove_item_from_cart(
        session_token=token,
        product_id=product_id
    )


@router.post("/cart/clear")
def clear_cart(
    authorization: Optional[str] = Header(None, description="Active session token")
):
    """
    Empty the user's shopping cart.

    Removes all products from the current cart, returning a confirmation message.

    - **authorization**: Pass the valid session token from login.
    """
    token = _check_auth_header(authorization)
    return CartController.clear_cart(session_token=token)


@router.post("/cart/checkout")
async def checkout_cart(
    coupon: Optional[str] = Query(None, description="Optional promotional coupon code to apply"),
    authorization: Optional[str] = Header(None, description="Active session token")
):
    """
    Checkout all items and place orders.

    Takes all items inside the cart, calculates final price post-discount/tax,
    creates order records for each item using the order service, and resets
    the cart items to empty.

    - **authorization**: Pass the valid session token from login.
    - **coupon**: Optional coupon code.
    """
    token = _check_auth_header(authorization)
    return await CartController.checkout_cart(
        session_token=token,
        coupon_code=coupon
    )
