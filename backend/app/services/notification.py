import os
try:
    import firebase_admin
    from firebase_admin import credentials, messaging
except ImportError:
    firebase_admin = None

# Initialize only if firebase.json exists
firebase_config = "firebase.json"
if firebase_admin and os.path.exists(firebase_config):
    if not firebase_admin._apps:
        cred = credentials.Certificate(firebase_config)
        firebase_admin.initialize_app(cred)

class NotificationService:
    @staticmethod
    def send_push(token: str, title: str, body: str):
        """Send push notification via Firebase FCM"""
        if not firebase_admin or not firebase_admin._apps:
            print(f"DEBUG: [Push Not Sent] Title: {title} | Body: {body}")
            return None
            
        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            token=token
        )
        return messaging.send(message)

    @staticmethod
    def send_streak_warning(user_id: str, habit_title: str):
        """High-level behavioral trigger for streak risk"""
        print(f"Notification: Sending streak warning to {user_id} for {habit_title}")

    @staticmethod
    def send_daily_reminder(user_id: str, habit_title: str):
        """High-level behavioral trigger for daily habit reminders"""
        print(f"Notification: Sending daily reminder to {user_id} for {habit_title}")

# Singleton instance
notification_service = NotificationService()
