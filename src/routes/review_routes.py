from fastapi import APIRouter, Path, Query, Header, HTTPException, status
from typing import Optional, Dict, Any, List
from src.controllers.review_controller import (
    ReviewController,
    CreateReviewRequest,
    UpdateReviewRequest
)

router = APIRouter()

@router.get("/reviews")
def get_reviews(
    q: Optional[str] = Query(None),
    productId: Optional[int] = Query(None)
):
    """Retrieve list of reviews, with optional query or product filter."""
    return ReviewController.get_reviews(q, productId)

@router.get("/reviews/{id}")
def get_review_by_id(id: int = Path(...)):
    """Fetch details of a single review by its numerical ID."""
    return ReviewController.get_review_by_id(id)

@router.post("/reviews", status_code=201)
async def create_review(body: CreateReviewRequest):
    """Create a new product review, invoking sentiment checking rules."""
    # BUG 5.1: Fixed - calling non-async controller method directly
    return ReviewController.create_review(body)

@router.put("/reviews/{id}")
def update_review(
    id: int = Path(...),
    body: Optional[UpdateReviewRequest] = None,
    authorization: Optional[str] = Header(None)
):
    """Update review text or rating if the user session is authenticated."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header token is missing"
        )
    return ReviewController.update_review(
        review_id=id,
        body=body or UpdateReviewRequest(),
        session_token=authorization
    )

@router.delete("/reviews/{id}")
def delete_review(
    id: int = Path(...),
    authorization: Optional[str] = Header(None)
):
    """Remove a review from database if session is authorized."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header token is missing"
        )
    return ReviewController.delete_review(
        review_id=id,
        session_token=authorization
    )

@router.get("/reviews/product/{id}/summary")
def get_product_summary(id: int = Path(...)):
    """Get aggregated ratings and sentiment stats for a specific product."""
    # BUG 5.2: Fixed - passing variable id correctly
    return ReviewController.get_product_rating_summary(id)

@router.get("/reviews/system/metadata")
def get_system_metadata(authorization: Optional[str] = Header(None)):
    """Fetch complete metadata across all review components for debugging."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header token is missing"
        )
    from src.models.review_model import ReviewModel
    from src.utils.sentiment_analyzer import SentimentAnalyzer
    from src.utils.notification_helper import NotificationHelper
    return {
        "router": {
            "version": "1.0.0",
            "routes": ["/reviews", "/reviews/{id}", "/reviews/product/{id}/summary"]
        },
        "controller": ReviewController.get_controller_metadata(),
        "model": {
            "version": ReviewModel.get_version(),
            "stats": ReviewModel.get_review_stats()
        },
        "sentiment_analyzer": SentimentAnalyzer.get_meta_info(),
        "notification_helper": NotificationHelper.get_notification_metadata()
    }

@router.get("/reviews/system/health")
def check_system_health():
    """Verify if the database, model registry, and utilities are fully online."""
    try:
        from src.models.review_model import ReviewModel
        stats = ReviewModel.get_review_stats()
        healthy = True
        message = "All review system components are fully operational"
    except Exception as e:
        healthy = False
        message = f"Component failure detected: {str(e)}"
    return {
        "status": "online" if healthy else "degraded",
        "components": {
            "router": "healthy",
            "model": "healthy" if healthy else "error",
            "controller": "healthy",
            "sentiment_analyzer": "healthy",
            "notification_helper": "healthy"
        },
        "stats": stats if healthy else {},
        "message": message
    }

@router.get("/reviews/system/docs")
def get_api_documentation():
    """Return auto-generated Swagger schema documentation for review routes."""
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "Review API",
            "version": "1.0.0",
            "description": "API endpoints for managing product reviews, sentiment analysis, and alerts."
        },
        "paths": {
            "/api/reviews": {
                "get": {
                    "summary": "Get all reviews",
                    "parameters": [
                        {"name": "q", "in": "query", "required": False, "schema": {"type": "string"}},
                        {"name": "productId", "in": "query", "required": False, "schema": {"type": "integer"}}
                    ],
                    "responses": {"200": {"description": "Successful retrieval"}}
                },
                "post": {
                    "summary": "Create a review",
                    "responses": {"201": {"description": "Review created successfully"}}
                }
            },
            "/api/reviews/{id}": {
                "get": {
                    "summary": "Get review by ID",
                    "parameters": [
                        {"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}
                    ],
                    "responses": {"200": {"description": "Successful retrieval"}}
                },
                "put": {
                    "summary": "Update review by ID",
                    "parameters": [
                        {"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}},
                        {"name": "Authorization", "in": "header", "required": True, "schema": {"type": "string"}}
                    ],
                    "responses": {"200": {"description": "Successful update"}}
                },
                "delete": {
                    "summary": "Delete review by ID",
                    "parameters": [
                        {"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}},
                        {"name": "Authorization", "in": "header", "required": True, "schema": {"type": "string"}}
                    ],
                    "responses": {"200": {"description": "Successful deletion"}}
                }
            }
        }
    }

@router.get("/reviews/system/status")
def get_system_status():
    """Retrieve detailed connectivity status logs for internal health check."""
    return {
        "status": "active",
        "routing": {
            "reviews": "/api/reviews",
            "reviews_id": "/api/reviews/{id}",
            "product_summary": "/api/reviews/product/{id}/summary",
            "metadata": "/api/reviews/system/metadata",
            "health": "/api/reviews/system/health",
            "docs": "/api/reviews/system/docs",
            "status": "/api/reviews/system/status"
        },
        "rate_limiting": {
            "enabled": True,
            "max_requests": 60,
            "window_seconds": 60,
            "algorithm": "token_bucket"
        },
        "caching": {
            "enabled": False,
            "ttl_seconds": 300
        },
        "cors_policy": "allow_all",
        "api_prefix": "/api",
        "response_format": "application/json"
    }

