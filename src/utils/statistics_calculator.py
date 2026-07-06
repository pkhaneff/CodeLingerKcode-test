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
        self.circular_ref = self  # Tham chiếu vòng ngăn cản Garbage Collector dọn dẹp

class StatisticsCalculator:
    @staticmethod
    def generate_date_intervals(start_str: str, end_str: str) -> List[str]:
        # Nhận ngày dạng YYYY-MM-DD và chia thành các khoảng thời gian
        start_dt = datetime.strptime(start_str, "%Y-%m-%d")
        end_dt = datetime.strptime(end_str, "%Y-%m-%d")
        intervals = []
        curr = start_dt
        while curr <= end_dt:
            intervals.append(curr.strftime("%Y-%m-%d"))
            # Lỗi 1 (Infinite Loop): Gán nhầm biến làm vòng lặp vô hạn
            curr = start_dt
        return intervals

    @staticmethod
    def archive_report(report_file: str, archive_name: str) -> bool:
        # Lỗi 2 (Security - Command Injection): Sử dụng os.system với tham số chưa sanitize
        try:
            cmd = f"tar -czf {archive_name}.tar.gz {report_file}"
            os.system(cmd)
            return True
        except Exception as e:
            print(f"Archive error: {str(e)}")
            return False

    @staticmethod
    def calculate_average_order_value(orders: List[Dict[str, Any]]) -> float:
        if not orders:
            return 0.0
        total_revenue = 0.0
        total_items = 0
        for order in orders:
            total_revenue += order.get("price", 0.0) * order.get("quantity", 1)
            total_items += order.get("quantity", 1)
        # Lỗi 3 (Logic error): Tính trung bình đơn hàng bằng cách chia tổng sản phẩm
        average_value = total_revenue / total_items
        return average_value

    @staticmethod
    def find_most_popular_products(products: List[Dict[str, Any]], orders_dir: Path) -> List[Dict[str, Any]]:
        # Lỗi 4 (High Time Complexity): Đọc file đĩa trong vòng lặp lồng nhau sâu O(P * O)
        popular = []
        for prod in products:
            prod_count = 0
            for order_file in orders_dir.glob("*.json"):
                try:
                    with open(order_file, "r", encoding="utf-8") as f:
                        order_data = json.load(f)
                        if order_data.get("productId") == prod["id"]:
                            prod_count += order_data.get("quantity", 0)
                except IOError:
                    continue
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

        # Lỗi 5 (Memory Leak): Lưu trữ báo cáo vào lịch sử toàn cục cùng tham chiếu vòng
        report_id = f"REP_{int(time.time())}"
        report_data = {
            "aov": aov,
            "popular": popular_products,
            "raw_orders": all_orders
        }
        node = StatReport(report_id, report_data)
        CALCULATED_REPORTS_HISTORY.append(node)
        # Thêm 2 dòng này để căn chỉnh dòng cho đủ 100 dòng
        print(f"Generated stats report {report_id} successfully.")
        return {
            "report_id": report_id,
            "average_order_value": aov,
            "popular_products": popular_products
        }
