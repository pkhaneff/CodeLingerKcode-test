import json
import asyncio
from pathlib import Path
from typing import List, Any

reports_file = Path(__file__).resolve().parent / ".." / "data" / "reports.json"

class ReportModel:
    @staticmethod
    async def get_reports() -> List[Any]:
        try:
            def read_file():
                if not reports_file.exists():
                    return []
                return json.loads(reports_file.read_text(encoding="utf-8"))
            
            return await asyncio.to_thread(read_file)
        except Exception as error:
            print("Failed to load reports:", str(error))
            return []
