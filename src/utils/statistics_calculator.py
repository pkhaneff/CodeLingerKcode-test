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

    @staticmethod
    def calculate_median_order_value(orders: List[Dict[str, Any]]) -> float:
        """
        Calculates the median value of a list of orders.
        """
        if not orders:
            return 0.0
        values = []
        for order in orders:
            val = order.get("price", 0.0) * order.get("quantity", 1)
            values.append(val)
        values.sort()
        n = len(values)
        if n % 2 == 1:
            return float(values[n // 2])
        else:
            return (values[n // 2 - 1] + values[n // 2]) / 2.0

    @staticmethod
    def calculate_sales_variance(orders: List[Dict[str, Any]]) -> float:
        """
        Calculates the variance of order values.
        """
        if not orders or len(orders) < 2:
            return 0.0
        values = [order.get("price", 0.0) * order.get("quantity", 1) for order in orders]
        mean = sum(values) / len(values)
        squared_diffs = [(val - mean) ** 2 for val in values]
        return sum(squared_diffs) / (len(values) - 1)

    @staticmethod
    def calculate_sales_standard_deviation(orders: List[Dict[str, Any]]) -> float:
        """
        Calculates the standard deviation of order values.
        """
        import math
        variance = StatisticsCalculator.calculate_sales_variance(orders)
        return math.sqrt(variance)

    @staticmethod
    def get_daily_sales_trend(orders: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Aggregates sales total by date (YYYY-MM-DD format).
        """
        trend = {}
        for order in orders:
            date_str = order.get("date") or order.get("created_at")
            if not date_str:
                date_str = "unknown_date"
            else:
                date_str = date_str.split("T")[0]
            val = order.get("price", 0.0) * order.get("quantity", 1)
            trend[date_str] = trend.get(date_str, 0.0) + val
        return trend

    @staticmethod
    def summarize_sales_metrics(orders: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Provides a comprehensive summary of sales metrics.
        """
        if not orders:
            return {
                "total_orders": 0,
                "total_revenue": 0.0,
                "average_value": 0.0,
                "median_value": 0.0,
                "variance": 0.0,
                "std_dev": 0.0,
                "daily_trend": {}
            }

        total_revenue = sum(o.get("price", 0.0) * o.get("quantity", 1) for o in orders)
        avg = StatisticsCalculator.calculate_average_order_value(orders)
        median = StatisticsCalculator.calculate_median_order_value(orders)
        variance = StatisticsCalculator.calculate_sales_variance(orders)
        std_dev = StatisticsCalculator.calculate_sales_standard_deviation(orders)
        daily_trend = StatisticsCalculator.get_daily_sales_trend(orders)

        return {
            "total_orders": len(orders),
            "total_revenue": total_revenue,
            "average_value": avg,
            "median_value": median,
            "variance": variance,
            "std_dev": std_dev,
            "daily_trend": daily_trend
        }
