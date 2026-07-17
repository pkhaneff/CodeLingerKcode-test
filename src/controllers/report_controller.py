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

    @staticmethod
    def validate_report_config(config: Dict[str, Any]) -> bool:
        """
        Validates the configuration dict for generating reports.
        """
        if not config:
            return False
        required_fields = ["title", "author", "metrics"]
        for field in required_fields:
            if field not in config:
                return False
        metrics = config.get("metrics")
        if not isinstance(metrics, list) or len(metrics) == 0:
            return False
        return True

    @staticmethod
    def save_report_to_disk(report_id: str, data: Dict[str, Any], output_dir: str = "data/reports") -> str:
        """
        Saves a generated report to disk in JSON format.
        Creates output directory if it doesn't exist.
        """
        import json
        try:
            os.makedirs(output_dir, exist_ok=True)
            file_path = os.path.join(output_dir, f"{report_id}.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            return file_path
        except Exception as e:
            print(f"Failed to save report: {str(e)}")
            return ""

    @staticmethod
    def list_generated_reports(directory: str = "data/reports") -> list:
        """
        Lists all generated report files in the target directory.
        """
        if not os.path.exists(directory):
            return []
        reports = []
        for file in os.listdir(directory):
            if file.endswith(".json"):
                reports.append(file)
        return reports

    @staticmethod
    def delete_report(report_id: str, directory: str = "data/reports") -> bool:
        """
        Deletes a report by id.
        """
        file_path = os.path.join(directory, f"{report_id}.json")
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                return True
            except OSError as e:
                print(f"Error deleting report: {str(e)}")
                return False
        return False

    @staticmethod
    def export_report_as_csv(report_id: str, data: Dict[str, Any], directory: str = "data/reports") -> str:
        """
        Converts report data to CSV format and saves it.
        """
        os.makedirs(directory, exist_ok=True)
        csv_path = os.path.join(directory, f"{report_id}.csv")
        try:
            with open(csv_path, "w", encoding="utf-8") as f:
                f.write("key,value\n")
                for key, val in data.items():
                    if isinstance(val, dict):
                        for sub_key, sub_val in val.items():
                            f.write(f"{key}.{sub_key},{sub_val}\n")
                    else:
                        f.write(f"{key},{val}\n")
            return csv_path
        except Exception as e:
            print(f"Failed to export CSV: {str(e)}")
            return ""
