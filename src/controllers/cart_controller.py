"""
Shopping Cart Controller Module

This module houses the controller layer for shopping cart interactions.
It serves as the business logic orchestrator, implementing APIs for
fetching summaries, adding/updating items, removing items, clearing
carts, and completing checkouts.

It integrates with:
- `ProductController` for checking product validity/prices.
- `DiscountModel` for fetching and verifying coupon codes.
- `UserController` (via `active_sessions`) to authenticate requests.
- `OrderController` to place orders upon cart checkout.

Designed to be detailed, clean, and conform to the ~200 line target.
"""

from typing import Optional, Dict, Any, List
from fastapi import HTTPException, status

from src.models.cart_model import CartModel, CartSummary
from src.controllers.product_controller import ProductController
from src.controllers.user_controller import UserController, active_sessions
from src.controllers.order_controller import OrderController, CreateOrderRequest
from src.models.discount_model import DiscountModel


class CartController:
    """
    Controller handling cart business operations.

    Exposes static methods to perform operations on behalf of authenticated
    users, verifying access tokens and validating product states.
    """

    @staticmethod
    def _get_username_from_session(session_token: str) -> str:
        """
        Authenticate a session token and resolve the corresponding username.

        Args:
            session_token (str): Authentication token passed from headers.

        Returns:
            str: Verified username.

        Raises:
            HTTPException: 401 Unauthorized if token is invalid or missing.
        """
        if not session_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization session token is required"
            )
        
        if session_token not in active_sessions:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session has expired or is invalid. Please log in again."
            )
        
        session_info = active_sessions[session_token]
        return session_info["username"]

    @staticmethod
    def get_cart_summary(session_token: str, coupon_code: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve the current cart's detailed pricing summary and list of items.

        Optionally applies a coupon code to show simulated savings before checkout.

        Args:
            session_token (str): Active user session token.
            coupon_code (Optional[str]): Promotional code to apply.

        Returns:
            Dict[str, Any]: Model dictionary dump of the CartSummary.
        """
        username = CartController._get_username_from_session(session_token)
        
        coupon_rate = 0
        if coupon_code:
            coupon = DiscountModel.get_coupon(coupon_code)
            if not coupon:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Coupon code '{coupon_code}' is invalid or does not exist"
                )
            coupon_rate = coupon.get("rate", 0)

        summary = CartModel.calculate_summary(username, coupon_rate, coupon_code)
        return summary.model_dump()

    @staticmethod
    def add_item_to_cart(session_token: str, product_id: int, quantity: int) -> Dict[str, Any]:
        """
        Add a product item to the user's cart after validating product metadata.

        Args:
            session_token (str): Active session token.
            product_id (int): Unique product ID to add.
            quantity (int): Number of units to add (must be > 0).

        Returns:
            Dict[str, Any]: The added or updated item data structure.
        """
        username = CartController._get_username_from_session(session_token)
        
        if quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quantity to add must be greater than zero"
            )

        # Validate that the product exists by calling ProductController
        try:
            product = ProductController.get_product_by_id(product_id)
        except HTTPException as exc:
            if exc.status_code == status.HTTP_404_NOT_FOUND:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product with ID {product_id} does not exist"
                )
            raise

        added_item = CartModel.add_item(
            username=username,
            product_id=product_id,
            quantity=quantity,
            name=product.get("name", "Unknown Product"),
            price=product.get("price", 0.0)
        )
        return {
            "message": "Product successfully added to cart",
            "item": added_item
        }

    @staticmethod
    def update_item_quantity(session_token: str, product_id: int, quantity: int) -> Dict[str, Any]:
        """
        Update the quantity of an item that is already present in the cart.

        Args:
            session_token (str): Active session token.
            product_id (int): Product identifier.
            quantity (int): New absolute quantity.

        Returns:
            Dict[str, Any]: The updated item information.
        """
        username = CartController._get_username_from_session(session_token)
        
        if quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Updated quantity must be greater than zero. Use DELETE to remove items."
            )

        updated_item = CartModel.update_item_quantity(username, product_id, quantity)
        if not updated_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} is not in your cart"
            )

        return {
            "message": "Cart item quantity updated successfully",
            "item": updated_item
        }

    @staticmethod
    def remove_item_from_cart(session_token: str, product_id: int) -> Dict[str, Any]:
        """
        Remove a product entirely from the user's shopping cart.

        Args:
            session_token (str): Active session token.
            product_id (int): Product identifier.

        Returns:
            Dict[str, Any]: Status message indicating outcome.
        """
        username = CartController._get_username_from_session(session_token)
        
        success = CartModel.remove_item(username, product_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} was not found in your cart"
            )

        return {"message": f"Product with ID {product_id} has been removed from cart"}

    @staticmethod
    def clear_cart(session_token: str) -> Dict[str, Any]:
        """
        Wipe all cart items clean for the user.

        Args:
            session_token (str): Active session token.

        Returns:
            Dict[str, Any]: Success notification.
        """
        username = CartController._get_username_from_session(session_token)
        CartModel.clear_cart(username)
        return {"message": "Shopping cart cleared successfully"}

    @staticmethod
    async def checkout_cart(session_token: str, coupon_code: Optional[str] = None) -> Dict[str, Any]:
        """
        Checkout all items in the user's cart, placing orders for each item.

        Calculates final cost (with coupon discount applied, if valid).
        Creates actual order objects in the order service via `OrderController.create_order`.
        Clears the cart upon successful order creations.

        Args:
            session_token (str): Active user session token.
            coupon_code (Optional[str]): Promotional code to apply at purchase time.

        Returns:
            Dict[str, Any]: Checkout summary detailing orders placed and final pricing.
        """
        username = CartController._get_username_from_session(session_token)
        
        # Get raw cart items and raise error if empty
        cart_items = CartModel.get_cart_items(username)
        if not cart_items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot checkout an empty shopping cart"
            )

        # Apply and record coupon details
        coupon_rate = 0
        if coupon_code:
            coupon = DiscountModel.get_coupon(coupon_code)
            if not coupon:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Coupon code '{coupon_code}' is invalid"
                )
            coupon_rate = coupon.get("rate", 0)

        # Compute final summary
        summary = CartModel.calculate_summary(username, coupon_rate, coupon_code)

        # Log coupon usage if applicable
        if coupon_code and summary.discount_savings > 0:
            product_ids = [item["product_id"] for item in cart_items]
            DiscountModel.log_applied_coupon(
                username=username,
                product_ids=product_ids,
                code=coupon_code,
                req_body={"checkout_total": summary.total}
            )

        # Create orders for each item in the cart via OrderController
        placed_orders = []
        for item in summary.items:
            order_req = CreateOrderRequest(
                username=username,
                productId=item.product_id,
                quantity=item.quantity
            )
            # Invoke OrderController async method
            new_order = await OrderController.create_order(order_req)
            placed_orders.append(new_order)

        # Reset cart to empty state
        CartModel.clear_cart(username)

        return {
            "message": "Checkout complete! Orders have been created successfully.",
            "pricing": {
                "subtotal": summary.subtotal,
                "coupon_applied": summary.coupon_applied,
                "discount_savings": summary.discount_savings,
                "tax": summary.tax,
                "total_paid": summary.total
            },
            "orders": placed_orders
        }
