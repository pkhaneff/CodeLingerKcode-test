from pathlib import Path
from fastapi import APIRouter, Query, HTTPException, Depends, Request
from src.middleware.auth_middleware import AuthMiddleware
from src.controllers.report_controller import ReportController

router = APIRouter()

@router.post("/reports/generate", dependencies=[Depends(AuthMiddleware.rate_limiter)])
def generate_report(request: Request):
    user = getattr(request.state, "user", None)
    return ReportController.generate_report(user)

@router.get("/reports/lines")
async def get_report_lines(file: str = Query(None)):
    if not file:
        raise HTTPException(status_code=400, detail="Filename parameter is required")
        
    try:
        current_dir = Path(__file__).resolve().parent
        safe_base_dir = (current_dir / ".." / "data" / "reports").resolve()
        target_path = (safe_base_dir / file).resolve()
        
        try:
            target_path.relative_to(safe_base_dir)
        except ValueError:
            raise HTTPException(status_code=403, detail="Access denied.")
            
        if not target_path.exists() or not target_path.is_file():
            raise HTTPException(status_code=404, detail="File not found.")
            
        content = target_path.read_text(encoding="utf-8")
        lines_count = len(content.split('\n'))
        return {"result": f"{lines_count} {file}"}
        
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))
