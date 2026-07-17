"""
Shopping Cart Model Module

This module implements the model layer for the Shopping Cart feature.
It defines schemas using Pydantic for validation and serialization,
manages a local in-memory storage dictionary representing user carts,
and provides helper routines to compute subtotals, tax rates, and
coupon discounts.

The file is designed to contain detailed docstrings and comments for clarity
and code quality, matching a target of approximately 200 lines.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, field_validator


class CartItem(BaseModel):
    """
    Schema representation of an individual item in a user's shopping cart.

    Attributes:
        product_id (int): The unique identifier of the product.
        quantity (int): Number of units requested. Must be strictly positive.
        name (str): The descriptive name of the product.
        price (float): The unit price of the product (must be non-negative).
        added_at (str): ISO formatted timestamp when the product was added.
    """
    product_id: int = Field(..., description="Unique product ID")
    quantity: int = Field(..., description="Quantity of the product, must be greater than zero")
    name: str = Field(..., description="The name of the product")
    price: float = Field(..., description="The unit price of the product")
    added_at: str = Field(default_factory=lambda: datetime.now().isoformat())

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v: int) -> int:
        """Ensure quantity is strictly positive."""
        if v <= 0:
            raise ValueError("Quantity must be greater than 0")
        return v

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: float) -> float:
        """Ensure unit price is non-negative."""
        if v < 0.0:
            raise ValueError("Price cannot be negative")
        return v


class CartSummary(BaseModel):
    """
    Aggregated response schema for a user's shopping cart.

    Contains full items list, intermediate subtotals, calculated
    taxes, Applied coupon discounts, and overall final total price.
    """
    username: str = Field(..., description="Owner of this shopping cart")
    items: List[CartItem] = Field(default_factory=list, description="List of items in the cart")
    subtotal: float = Field(0.0, description="Sum of all item totals (price * quantity)")
    discount_savings: float = Field(0.0, description="Amount saved using coupon discount")
    coupon_applied: Optional[str] = Field(None, description="Coupon code applied, if any")
    tax: float = Field(0.0, description="Calculated tax (10% standard rate on subtotal post-discount)")
    total: float = Field(0.0, description="Grand total to pay")
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())


# Global In-Memory Cart Repository.
# Format: { username: [dict representation of CartItem] }
_CARTS_DB: Dict[str, List[Dict[str, Any]]] = {}


class CartModel:
    """
    Data Access Object (DAO) for shopping carts.

    Coordinates all data modifications to the in-memory database
    and provides calculations for cart subtotals and discount checks.
    """

    @classmethod
    def get_cart_items(cls, username: str) -> List[Dict[str, Any]]:
        """
        Retrieve all cart items raw dictionaries for a specific user.

        If the user does not have a cart, an empty list is returned.
        """
        if username not in _CARTS_DB:
            _CARTS_DB[username] = []
        return _CARTS_DB[username]

    @classmethod
    def add_item(cls, username: str, product_id: int, quantity: int, name: str, price: float) -> Dict[str, Any]:
        """
        Add a new product or increment the quantity of an existing one in the user's cart.

        Args:
            username (str): The owner of the cart.
            product_id (int): ID of the product.
            quantity (int): Units of the product.
            name (str): Name of the product.
            price (float): Price per unit.

        Returns:
            Dict[str, Any]: The newly added or modified item in the cart.
        """
        items = cls.get_cart_items(username)
        
        # Check if the product already exists in the cart
        for item in items:
            if item["product_id"] == product_id:
                item["quantity"] += quantity
                item["added_at"] = datetime.now().isoformat()
                return item

        # If not present, create a new CartItem
        new_item = {
            "product_id": product_id,
            "quantity": quantity,
            "name": name,
            "price": price,
            "added_at": datetime.now().isoformat()
        }
        
        # Validate using Pydantic to ensure correctness
        validated = CartItem(**new_item)
        items.append(validated.model_dump())
        return validated.model_dump()

    @classmethod
    def update_item_quantity(cls, username: str, product_id: int, quantity: int) -> Optional[Dict[str, Any]]:
        """
        Set the absolute quantity of a specific product in the cart.

        Args:
            username (str): Cart owner.
            product_id (int): Product to update.
            quantity (int): New quantity.

        Returns:
            Optional[Dict[str, Any]]: Updated item dict or None if not in cart.
        """
        items = cls.get_cart_items(username)
        for item in items:
            if item["product_id"] == product_id:
                # Validate using Pydantic validation rules
                validated = CartItem(
                    product_id=product_id,
                    quantity=quantity,
                    name=item["name"],
                    price=item["price"],
                    added_at=datetime.now().isoformat()
                )
                item["quantity"] = validated.quantity
                item["added_at"] = validated.added_at
                return item
        return None

    @classmethod
    def remove_item(cls, username: str, product_id: int) -> bool:
        """
        Remove a specific product entirely from the user's cart.

        Returns:
            bool: True if item was found and removed, False otherwise.
        """
        items = cls.get_cart_items(username)
        for index, item in enumerate(items):
            if item["product_id"] == product_id:
                items.pop(index)
                return True
        return False

    @classmethod
    def clear_cart(cls, username: str) -> None:
        """
        Remove all items from a user's shopping cart.
        """
        _CARTS_DB[username] = []

    @classmethod
    def calculate_summary(cls, username: str, coupon_rate: Optional[int] = 0, coupon_code: Optional[str] = None) -> CartSummary:
        """
        Construct a full CartSummary by calculating prices, taxes, and discounts.

        The tax is calculated as 10% of the subtotal after the coupon is applied.
        All pricing is rounded to two decimal places.

        Args:
            username (str): Cart owner.
            coupon_rate (Optional[int]): Percentage discount to apply (0-100). Defaults to 0.
            coupon_code (Optional[str]): Code string for documentation. Defaults to None.

        Returns:
            CartSummary: Complete summary with pricing and items.
        """
        raw_items = cls.get_cart_items(username)
        items_list = [CartItem(**item) for item in raw_items]
        
        # Calculate subtotal (price * quantity)
        subtotal = sum(item.price * item.quantity for item in items_list)
        subtotal = round(subtotal, 2)

        # Apply coupon rate discount
        discount_savings = 0.0
        if coupon_rate and coupon_rate > 0:
            rate_fraction = min(max(coupon_rate, 0), 100) / 100.0
            discount_savings = subtotal * rate_fraction
            discount_savings = round(discount_savings, 2)

        # Base for tax calculations (cannot be negative)
        post_discount_base = max(subtotal - discount_savings, 0.0)

        # Calculate standard 10% tax rate
        tax = post_discount_base * 0.10
        tax = round(tax, 2)

        # Grand total
        total = post_discount_base + tax
        total = round(total, 2)

        return CartSummary(
            username=username,
            items=items_list,
            subtotal=subtotal,
            discount_savings=discount_savings,
            coupon_applied=coupon_code if discount_savings > 0 else None,
            tax=tax,
            total=total,
            updated_at=datetime.now().isoformat()
        )
