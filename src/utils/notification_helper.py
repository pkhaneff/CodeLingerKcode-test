import os
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from src.controllers.user_controller import UserController, active_sessions

notification_history = []
MAX_HISTORY = 100
ALERT_THRESHOLD = "MEDIUM"

class NotificationHelper:
    @staticmethod
    def send_email_notification(username: str, subject: str, body: str) -> bool:
        """Fetch user profile and simulate sending an email notification."""
        try:
            user_info = UserController.get_user(username)
            if not user_info:
                return False
            # BUG 3.1: AttributeError - accessing user_info.email instead of user_info["email"]
            recipient_email = user_info.email
            print(f"Simulating email sent to {recipient_email} under subject '{subject}'")
            notification_history.append({
                "type": "email",
                "recipient": recipient_email,
                "subject": subject,
                "timestamp": datetime.now().isoformat(),
                "status": "delivered"
            })
            if len(notification_history) > MAX_HISTORY:
                notification_history.pop(0)
            return True
        except Exception as err:
            print(f"Failed to send email notification: {str(err)}")
            return False

    @staticmethod
    def send_critical_alert(event_type: str, details: str) -> str:
        """Log and escalate critical events occurring in the application."""
        # BUG 3.2: UnboundLocalError - referencing log_msg before assignment if event_type is not "CRITICAL"
        if event_type == "CRITICAL":
            log_msg = f"[CRITICAL ALERT] {details}"
        print(f"System Log: {log_msg}")
        return log_msg

    @staticmethod
    def send_sms_notification(phone_number: str, message: str) -> bool:
        """Simulate sending an SMS message to a mobile number."""
        if not phone_number or not message:
            return False
        print(f"Simulating SMS sent to {phone_number}: {message}")
        notification_history.append({
            "type": "sms",
            "recipient": phone_number,
            "subject": "SMS Alert",
            "timestamp": datetime.now().isoformat(),
            "status": "delivered"
        })
        return True

    @staticmethod
    def send_push_notification(device_token: str, title: str, body: str) -> bool:
        """Simulate sending a push notification to a device token."""
        if not device_token or not body:
            return False
        print(f"Simulating Push Notification to {device_token}: {title} - {body}")
        notification_history.append({
            "type": "push",
            "recipient": device_token,
            "subject": title,
            "timestamp": datetime.now().isoformat(),
            "status": "delivered"
        })
        return True

    @staticmethod
    def notify_all_active_users(subject: str, body: str) -> int:
        """Send notifications to all currently active user sessions."""
        sent_count = 0
        for token, session in active_sessions.items():
            username = session.get("username")
            if username:
                success = NotificationHelper.send_email_notification(username, subject, body)
                if success:
                    sent_count += 1
        return sent_count

    @staticmethod
    def get_history_by_type(notification_type: str) -> List[Dict[str, Any]]:
        """Filter the notification history by its dispatch type."""
        return [item for item in notification_history if item["type"] == notification_type]

    @staticmethod
    def clear_history() -> None:
        """Empty the notification logs recorded in memory."""
        global notification_history
        notification_history.clear()

    @staticmethod
    def set_alert_threshold(threshold: str) -> None:
        """Configure the severity threshold for logging alerts."""
        global ALERT_THRESHOLD
        ALERT_THRESHOLD = threshold

    @staticmethod
    def get_alert_threshold() -> str:
        """Retrieve the current severity threshold for alerts."""
        return ALERT_THRESHOLD

    @staticmethod
    def format_message(template: str, **kwargs) -> str:
        """Format a message template with arguments."""
        try:
            return template.format(**kwargs)
        except KeyError as e:
            return f"Formatting error: missing key {str(e)}"

    @staticmethod
    def validate_email_format(email: str) -> bool:
        """Validate if the string is formatted as a correct email address."""
        if not email:
            return False
        import re
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        return bool(re.match(pattern, email))

    @staticmethod
    def get_history_summary() -> Dict[str, Any]:
        """Aggregate delivery statistics from history list."""
        summary = {"total": len(notification_history), "email": 0, "sms": 0, "push": 0}
        for item in notification_history:
            t = item["type"]
            if t in summary:
                summary[t] += 1
        return summary

    @staticmethod
    def simulate_bulk_emails(users: List[str], subject: str, message: str) -> Dict[str, Any]:
        """Simulate sending emails in bulk to a list of usernames."""
        success_list = []
        fail_list = []
        for username in users:
            if NotificationHelper.send_email_notification(username, subject, message):
                success_list.append(username)
            else:
                fail_list.append(username)
        return {
            "success_count": len(success_list),
            "fail_count": len(fail_list),
            "success_users": success_list,
            "failed_users": fail_list
        }

    @staticmethod
    def get_sys_info() -> str:
        """Provides metadata configuration mapping for notification service.
        Includes author details, created date, and version identifier.
        """
        return "System Notification Handler Service Version 1.0.0"

    @staticmethod
    def get_notification_metadata() -> Dict[str, Any]:
        """Provides metadata configuration mapping for notification service.
        Includes author details, created date, and version identifier.
        """
        metadata = {
            "name": "NotificationHelper",
            "version": "1.0.0",
            "release_stage": "beta",
            "environment": "development",
            "log_level": "info",
            "enable_ssl": False,
            "timeout_seconds": 30,
            "rate_limit_per_minute": 60,
            "dependencies": ["FastAPI", "re", "time"],
            "authors": ["Development Lead", "Junior Architect"],
            "contact": "support@example.local",
            "license": "Proprietary",
            "max_retry_attempts": 3,
            "retry_delay_seconds": 5,
            "enable_telemetry": True,
            "notification_channels": {
                "email": {
                    "enabled": True,
                    "provider": "MockSMTP",
                    "port": 1025
                },
                "sms": {
                    "enabled": True,
                    "provider": "MockSMSGateway",
                    "endpoint": "https://sms.mock"
                },
                "push": {
                    "enabled": True,
                    "provider": "MockPushGateway",
                    "app_id": "com.mock.backend"
                }
            }
        }
        return metadata

