import requests
import json

import time
BASE_URL = "http://localhost:8000"
email = f"test_{int(time.time())}@example.com"
password = "password"

# 1. Register/Login
try:
    requests.post(f"{BASE_URL}/auth/register", json={"email": email, "password": password})
except:
    pass

response = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
if response.status_code != 200:
    print(f"Login failed: {response.text}")
    exit(1)

auth_data = response.json()
token = auth_data["access_token"]
headers = {"Authorization": f"Bearer {token}"}

print("Login Successful")

# 2. Get Habits
res = requests.get(f"{BASE_URL}/habits/", headers=headers)
print(f"Habits ({res.status_code}): {len(res.json()) if res.status_code == 200 else res.text}")

# 3. Get Pulse
res = requests.get(f"{BASE_URL}/analytics/pulse", headers=headers)
print(f"Pulse ({res.status_code}): {res.text}")

# 4. Admin DAU
res = requests.get(f"{BASE_URL}/admin/analytics/dau", headers=headers)
print(f"Admin DAU ({res.status_code}): {res.text}")

# 5. Admin User Growth
res = requests.get(f"{BASE_URL}/admin/analytics/user-growth", headers=headers)
print(f"Admin User Growth ({res.status_code}): {res.text}")

print("Endpoint Verification Complete")
