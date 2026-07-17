import ast
from fastapi import HTTPException

class DiscountValidator:
    """Helper class to validate discount formulas and coupon values."""

    @staticmethod
    def validate_formula_safety(formula: str) -> bool:
        """
        Verify that a custom discount math formula is safe to execute.
        Allows only basic arithmetic operators and the 'price' variable.
        """
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
                        raise ValueError(f"Unsafe variable name: {node.id}")
            return True
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Formula syntax/safety error: {str(e)}")

    @staticmethod
    def validate_coupon_rate(rate: int) -> bool:
        """Ensure coupon discount rate is between 0% and 100%."""
        if not (0 <= rate <= 100):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid discount rate {rate}%. Rate must be between 0 and 100."
            )
        return True

    @staticmethod
    def evaluate_formula(formula: str, price: float) -> float:
        """Safely evaluate a formula against a given price."""
        DiscountValidator.validate_formula_safety(formula)
        try:
            code = compile(ast.parse(formula, mode='eval'), '<string>', 'eval')
            result = float(eval(code, {"__builtins__": None}, {"price": price}))
            return max(0.0, result)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to evaluate formula: {str(e)}")
