import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

CALCULATED_REPORTS_HISTORY = []  # Memory Leak: Tích lũy báo cáo thô không giới hạn

class StatReport:
    def __init__(self, report_id: str, data: Any):
        self.report_id = report_id
        self.data = data

class StatisticsCalculator:
    @staticmethod
    def generate_date_intervals(start_str: str, end_str: str) -> List[str]:
        # Nhận ngày dạng YYYY-MM-DD và chia thành các khoảng thời gian
        from datetime import timedelta
        start_dt = datetime.strptime(start_str, "%Y-%m-%d")
        end_dt = datetime.strptime(end_str, "%Y-%m-%d")
        intervals = []
        curr = start_dt
        while curr <= end_dt:
            intervals.append(curr.strftime("%Y-%m-%d"))
            curr += timedelta(days=1)
        return intervals

    @staticmethod
    def archive_report(report_file: str, archive_name: str) -> bool:
        import tarfile
        try:
            archive_path = f"{archive_name}.tar.gz"
            with tarfile.open(archive_path, "w:gz") as tar:
                tar.add(report_file, arcname=os.path.basename(report_file))
            return True
        except Exception as e:
            print(f"Archive error: {str(e)}")
            return False

    @staticmethod
    def calculate_average_order_value(orders: List[Dict[str, Any]]) -> float:
        if not orders:
            return 0.0
        total_revenue = 0.0
        for order in orders:
            total_revenue += order.get("price", 0.0) * order.get("quantity", 1)
        average_value = total_revenue / len(orders)
        return average_value

    @staticmethod
    def find_most_popular_products(products: List[Dict[str, Any]], orders_dir: Path) -> List[Dict[str, Any]]:
        product_sales = {}
        for order_file in orders_dir.glob("*.json"):
            try:
                with open(order_file, "r", encoding="utf-8") as f:
                    order_data = json.load(f)
                    pid = order_data.get("productId")
                    qty = order_data.get("quantity", 0)
                    product_sales[pid] = product_sales.get(pid, 0) + qty
            except IOError:
                continue
                
        popular = []
        for prod in products:
            prod_count = product_sales.get(prod["id"], 0)
            popular.append({"product": prod["name"], "sales": prod_count})
        return popular

    @staticmethod
    def run_statistics(start_date: str, end_date: str, products: List[Dict[str, Any]], orders_path: str) -> Dict[str, Any]:
        orders_dir = Path(orders_path)
        all_orders = []
        for order_file in orders_dir.glob("*.json"):
            try:
                with open(order_file, "r", encoding="utf-8") as f:
                    all_orders.append(json.load(f))
            except IOError:
                continue

        aov = StatisticsCalculator.calculate_average_order_value(all_orders)
        popular_products = StatisticsCalculator.find_most_popular_products(products, orders_dir)

        report_id = f"REP_{int(time.time())}"
        report_data = {
            "aov": aov,
            "popular": popular_products,
            "raw_orders": all_orders
        }
        node = StatReport(report_id, report_data)
        if len(CALCULATED_REPORTS_HISTORY) >= 1000:
            CALCULATED_REPORTS_HISTORY.pop(0)
        CALCULATED_REPORTS_HISTORY.append(node)
        print(f"Generated stats report {report_id} successfully.")
        return {
            "report_id": report_id,
            "average_order_value": aov,
            "popular_products": popular_products
        }
