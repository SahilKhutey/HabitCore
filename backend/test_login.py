import requests
import json

url = "http://localhost:8000/auth/login"
data = {"email": "test@example.com", "password": "password"}

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
