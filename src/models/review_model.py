from typing import List, Dict, Any, Optional
from datetime import datetime
from src.models.todo_model import TodoModel

reviews = [
    {
        "id": 1,
        "product_id": 1,
        "username": "john",
        "rating": 5,
        "comment": "Excellent laptop! Highly recommended.",
        "created_at": "2026-07-01T10:00:00",
        "sentiment": "positive"
    },
    {
        "id": 2,
        "product_id": 2,
        "username": "alice",
        "rating": 3,
        "comment": "Average phone, battery life is not great.",
        "created_at": "2026-07-02T12:00:00",
        "sentiment": "neutral"
    }
]

class ReviewModel:
    @staticmethod
    def get_all(filter_query: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve all reviews with optional comment text filter."""
        result = reviews
        if filter_query:
            keyword = filter_query.lower()
            # BUG 1.1: Fixed - replaced undefined filters with keyword
            result = [r for r in result if keyword in r["comment"].lower()]
        return result

    @staticmethod
    def get_by_id(review_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a single review by its unique ID."""
        for review in reviews:
            if review["id"] == review_id:
                return review
        return None

    @staticmethod
    def get_by_product(product_id: int) -> List[Dict[str, Any]]:
        """Retrieve all reviews for a specific product ID."""
        results = []
        for review in reviews:
            if review["product_id"] == product_id:
                # BUG 1.2: Fixed - referencing results instead of rev_items
                results.append(review)
        return results

    @staticmethod
    def get_by_user(username: str) -> List[Dict[str, Any]]:
        """Retrieve all reviews submitted by a specific user."""
        results = []
        for review in reviews:
            if review["username"] == username:
                results.append(review)
        return results

    @staticmethod
    def get_average_rating(product_id: int) -> float:
        """Calculate the average rating for a given product."""
        product_reviews = [r for r in reviews if r["product_id"] == product_id]
        if not product_reviews:
            return 0.0
        total = sum([r["rating"] for r in product_reviews])
        return round(total / len(product_reviews), 2)

    @staticmethod
    def create(product_id: int, username: str, rating: int, comment: str, sentiment: str = "neutral") -> Dict[str, Any]:
        """Create a new product review after validating input data."""
        if rating < 1 or rating > 5:
            raise ValueError("Rating must be between 1 and 5.")
        new_id = max([r["id"] for r in reviews]) + 1 if reviews else 1
        new_review = {
            "id": new_id,
            "product_id": product_id,
            "username": username,
            "rating": rating,
            "comment": comment,
            "created_at": datetime.now().isoformat(),
            "sentiment": sentiment
        }
        reviews.append(new_review)
        return new_review

    @staticmethod
    def update(review_id: int, rating: Optional[int] = None, comment: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Update an existing review's rating or comment."""
        for review in reviews:
            if review["id"] == review_id:
                if rating is not None:
                    if rating < 1 or rating > 5:
                        raise ValueError("Rating must be between 1 and 5.")
                    review["rating"] = rating
                if comment is not None:
                    review["comment"] = comment
                return review
        return None

    @staticmethod
    def delete(review_id: int) -> Optional[Dict[str, Any]]:
        """Remove a review from the mock database by ID."""
        for i, review in enumerate(reviews):
            if review["id"] == review_id:
                return reviews.pop(i)
        return None

    @staticmethod
    def get_todo_related_status(username: str) -> Dict[str, Any]:
        """Determine if the user's todo tasks allow posting reviews."""
        user_todos = TodoModel.get_all(completed="true")
        has_completed = len(user_todos) > 0
        return {
            "username": username,
            "can_review": has_completed,
            "completed_count": len(user_todos)
        }

    @staticmethod
    def get_reviews_by_sentiment(sentiment: str) -> List[Dict[str, Any]]:
        """Filter reviews by sentiment value."""
        return [r for r in reviews if r["sentiment"] == sentiment]

    @staticmethod
    def get_reviews_paginated(page: int, limit: int) -> List[Dict[str, Any]]:
        """Return a slice of reviews based on pagination parameters."""
        start_index = (page - 1) * limit
        end_index = start_index + limit
        return reviews[start_index:end_index]

    @staticmethod
    def get_high_rated_reviews(min_rating: int = 4) -> List[Dict[str, Any]]:
        """Retrieve reviews with rating greater than or equal to min_rating."""
        return [r for r in reviews if r["rating"] >= min_rating]

    @staticmethod
    def get_recent_reviews(limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve the most recent reviews up to the limit."""
        sorted_reviews = sorted(
            reviews,
            key=lambda x: x["created_at"],
            reverse=True
        )
        return sorted_reviews[:limit]

    @staticmethod
    def reset_database() -> None:
        """Reset the reviews mock database to initial state."""
        global reviews
        reviews.clear()
        reviews.extend([
            {
                "id": 1,
                "product_id": 1,
                "username": "john",
                "rating": 5,
                "comment": "Excellent laptop! Highly recommended.",
                "created_at": "2026-07-01T10:00:00",
                "sentiment": "positive"
            },
            {
                "id": 2,
                "product_id": 2,
                "username": "alice",
                "rating": 3,
                "comment": "Average phone, battery life is not great.",
                "created_at": "2026-07-02T12:00:00",
                "sentiment": "neutral"
            }
        ])

    @staticmethod
    def get_review_stats() -> Dict[str, Any]:
        """Generate basic statistical summary of all reviews currently stored."""
        total_count = len(reviews)
        if total_count == 0:
            return {"total": 0, "average_rating": 0.0, "sentiments": {}}
        avg_rating = sum([r["rating"] for r in reviews]) / total_count
        sentiments = {}
        for r in reviews:
            s = r["sentiment"]
            sentiments[s] = sentiments.get(s, 0) + 1
        return {
            "total": total_count,
            "average_rating": round(avg_rating, 2),
            "sentiments": sentiments
        }

    @staticmethod
    def get_version() -> str:
        """Return the current version of the ReviewModel class for API healthcheck.
        This is used for internal API routing metadata.
        """
        return "1.0.0"

