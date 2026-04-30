import firebase_admin
from firebase_admin import credentials, messaging
import os

# Initialize only if firebase.json exists
firebase_config = "firebase.json"
if os.path.exists(firebase_config):
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)

def send_push(token, title, body):
    if not firebase_admin._apps:
        print("Firebase not initialized. Skipping push notification.")
        return None
        
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body
        ),
        token=token
    )
    return messaging.send(message)
