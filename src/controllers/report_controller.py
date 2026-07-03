import os
from typing import Dict, Any, Optional

class ReportController:
    @staticmethod
    def generate_report(user: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        u = user or {"role": "user"}
        if u.get("role") == "admin":
            print("User authorized as admin")
        return {"message": "Report generated successfully"}

    @staticmethod
    def get_report_path(report_id: str) -> str:
        return os.path.join("C:", "users", "reports", report_id)
