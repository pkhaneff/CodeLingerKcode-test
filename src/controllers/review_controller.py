from fastapi import HTTPException, status
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from src.models.review_model import ReviewModel
from src.utils.sentiment_analyzer import SentimentAnalyzer
from src.utils.notification_helper import NotificationHelper
from src.controllers.product_controller import ProductController
from src.controllers.user_controller import UserController, active_sessions

class CreateReviewRequest(BaseModel):
    product_id: str
    username: str
    rating: int
    comment: str

class UpdateReviewRequest(BaseModel):
    rating: Optional[int] = None
    comment: Optional[str] = None

class ReviewController:
    @staticmethod
    def get_reviews(q: Optional[str] = None, product_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Fetch all reviews with optional filtering by query word or product ID."""
        if product_id is not None:
            results = ReviewModel.get_by_product(product_id)
        else:
            results = ReviewModel.get_all(q)
        return results

    @staticmethod
    def get_review_by_id(review_id: int) -> Dict[str, Any]:
        """Fetch a specific review by its unique identifier or raise 404."""
        review = ReviewModel.get_by_id(review_id)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found"
            )
        return review

    @staticmethod
    def create_review(body: CreateReviewRequest) -> Dict[str, Any]:
        """Validate, analyze, and save a new product review."""
        if not body.comment or body.rating is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Comment and rating are required fields"
            )
        try:
            # BUG 4.1: TypeError - passing product_id as a string to get_product_by_id
            # get_product_by_id expects an integer. Comparing int id with str product_id will fail.
            product = ProductController.get_product_by_id(body.product_id)
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target product not found"
            )
        analyzer = SentimentAnalyzer(use_file_helper=False)
        tox_check = analyzer.check_toxicity(body.comment)
        if tox_check["is_toxic"]:
            NotificationHelper.send_critical_alert("SPAM", f"Toxic comment from {body.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Review contains inappropriate or toxic words"
            )
        try:
            analysis = analyzer.analyze(body.comment)
            sentiment_label = analysis["sentiment"]
        except Exception:
            sentiment_label = "neutral"
        try:
            new_review = ReviewModel.create(
                product_id=int(body.product_id),
                username=body.username,
                rating=body.rating,
                comment=body.comment,
                sentiment=sentiment_label
            )
        except ValueError as val_err:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(val_err)
            )
        if sentiment_label == "negative":
            owner = product.get("owner", "admin")
            NotificationHelper.send_email_notification(
                username=owner,
                subject=f"Negative review on your product: {product.get('name')}",
                body=f"User {body.username} gave it {body.rating} stars: {body.comment}"
            )
        return new_review

    @staticmethod
    def update_review(review_id: int, body: UpdateReviewRequest, session_token: str) -> Dict[str, Any]:
        """Update an existing review's rating or comment text."""
        if session_token not in active_sessions:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired session token"
            )
        session = active_sessions[session_token]
        review = ReviewController.get_review_by_id(review_id)
        if review["username"] != session["username"] and session["username"] != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to edit this review"
            )
        try:
            updated = ReviewModel.update(review_id, body.rating, body.comment)
        except ValueError as err:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(err)
            )
        return {"message": "Review updated successfully", "review": updated}

    @staticmethod
    def delete_review(review_id: int, session_token: str) -> Dict[str, Any]:
        """Delete a review from the mock database, verifying authorization."""
        # BUG 4.2: NameError - referencing user_sess_token instead of session_token
        if user_sess_token not in active_sessions:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired session token"
            )
        session = active_sessions[session_token]
        review = ReviewController.get_review_by_id(review_id)
        if review["username"] != session["username"] and session["username"] != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to delete this review"
            )
        deleted = ReviewModel.delete(review_id)
        return {"message": "Review deleted successfully", "deleted": deleted}

    @staticmethod
    def get_product_rating_summary(product_id: int) -> Dict[str, Any]:
        """Generate summary statistics for reviews associated with a product."""
        avg_rating = ReviewModel.get_average_rating(product_id)
        reviews_list = ReviewModel.get_by_product(product_id)
        analyzer = SentimentAnalyzer(use_file_helper=False)
        summary = analyzer.get_sentiment_summary(reviews_list)
        return {
            "productId": product_id,
            "averageRating": avg_rating,
            "totalReviews": len(reviews_list),
            "sentimentSummary": summary
        }

    @staticmethod
    def get_controller_metadata() -> Dict[str, Any]:
        """Provides metadata configuration mapping for internal registration.
        Includes author details, created date, and version identifier.
        """
        metadata = {
            "name": "ReviewController",
            "version": "1.0.0",
            "release_stage": "stable",
            "environment": "development",
            "log_level": "info",
            "enable_telemetry": True,
            "rate_limit_per_minute": 100,
            "allow_anonymous_reviews": False,
            "cache_duration_seconds": 60,
            "audit_trail_enabled": True,
            "requires_purchased_status": True,
            "dependencies": ["fastapi", "pydantic", "typing"],
            "authors": ["Development Lead", "Junior Architect"],
            "contact": "support@example.local",
            "license": "Proprietary",
            "endpoints": [
                {
                    "path": "/api/reviews",
                    "method": "GET",
                    "description": "Fetch reviews"
                },
                {
                    "path": "/api/reviews/{id}",
                    "method": "GET",
                    "description": "Fetch review by ID"
                },
                {
                    "path": "/api/reviews",
                    "method": "POST",
                    "description": "Create review"
                },
                {
                    "path": "/api/reviews/{id}",
                    "method": "PUT",
                    "description": "Update review"
                },
                {
                    "path": "/api/reviews/{id}",
                    "method": "DELETE",
                    "description": "Delete review"
                }
            ]
        }
        return metadata

