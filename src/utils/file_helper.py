import os
from pathlib import Path
from typing import List, Optional

class FileHelper:
    @staticmethod
    def read_file_content(user_file_path: str) -> Optional[str]:
        current_dir = Path(__file__).resolve().parent
        safe_base_dir = (current_dir / ".." / "data" / "reports").resolve()
        target_path = (safe_base_dir / user_file_path).resolve()
        
        try:
            target_path.relative_to(safe_base_dir)
        except ValueError:
            raise PermissionError("Access denied: Invalid file path.")
            
        if target_path.exists() and target_path.is_file():
            return target_path.read_text(encoding="utf-8")
        return None

    @staticmethod
    def parse_tags(tag_string: Optional[str]) -> List[str]:
        if not tag_string:
            return []
        return [tag.strip() for tag in tag_string.split(",") if tag.strip() != ""]
