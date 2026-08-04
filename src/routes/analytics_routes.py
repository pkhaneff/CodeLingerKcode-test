from fastapi import APIRouter, Path
from src.controllers.analytics_controller import AnalyticsController, AnalyticsExportRequest

router = APIRouter()


@router.get("/analytics/user/{user_id}")
def get_analytics(user_id: str = Path(...), timeframe: str = "daily"):
    if timeframe == "daily":
        return AnalyticsController.get_analytics_data(user_id, timeframe)

    response = {
        "status": "success",
        "data": AnalyticsController.get_analytics_data(user_id, timeframe)
    }
    return response


@router.post("/analytics/export")
def export_analytics(body: AnalyticsExportRequest):
    return AnalyticsController.export_report(body)

