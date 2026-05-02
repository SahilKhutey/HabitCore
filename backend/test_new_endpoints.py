import requests

r = requests.post('http://localhost:8000/auth/login', json={'email':'test@example.com','password':'password'})
token = r.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# Shop
shop = requests.get('http://localhost:8000/shop/items')
print(f'shop/items => {shop.status_code} - {len(shop.json())} items')
for item in shop.json()[:3]:
    print(f"  {item['name']} ({item['category']}) cost:{item['cost']}")

# Activity feed
act = requests.get('http://localhost:8000/habits/activity', headers=headers)
print(f'habits/activity => {act.status_code}')
data = act.json()
print(f'  total={data["total"]}')
for entry in data['feed'][:3]:
    print(f"  {entry['habit_name']} +{entry['xp_earned']} XP {entry['time_ago']}")

print('=== OK ===')
