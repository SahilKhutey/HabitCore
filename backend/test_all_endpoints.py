import requests, json

r = requests.post('http://localhost:8000/auth/login', json={'email':'test@example.com','password':'password'})
token = r.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

print('=== FULL ENDPOINT TEST ===')

r2 = requests.get('http://localhost:8000/habits/', headers=headers)
habits = r2.json()
habit_names = [h['name'] for h in habits]
print(f'habits/ => {r2.status_code} - {len(habits)} habits: {habit_names}')

r3 = requests.get('http://localhost:8000/habits/state', headers=headers)
state = r3.json()
print(f'habits/state => {r3.status_code} - streak={state["user_state"]["current_streak"]}, xp={state["user_state"]["xp"]}')

habit_id = habits[0]['id']
r4 = requests.post('http://localhost:8000/habits/complete', json={'habit_id': habit_id}, headers=headers)
print(f'habits/complete => {r4.status_code} - {r4.text[:120]}')

r5 = requests.get('http://localhost:8000/habits/state', headers=headers)
state2 = r5.json()
print(f'state post-complete => xp={state2["user_state"]["xp"]}, streak={state2["user_state"]["current_streak"]}')

r6 = requests.post('http://localhost:8000/habits/reset-burnout', headers=headers)
print(f'reset-burnout => {r6.status_code} - {r6.json()}')

r7 = requests.get('http://localhost:8000/api/avatar/', headers=headers)
avatar = r7.json()
print(f'avatar/ => {r7.status_code} - level={avatar["avatar"]["level"]}, coins={avatar["avatar"]["economy"]["coins"]}')

r8 = requests.get('http://localhost:8000/api/avatar/shop', headers=headers)
print(f'avatar/shop => {r8.status_code} - {len(r8.json()["items"])} items')

r9 = requests.post('http://localhost:8000/habits/seed', json={}, headers=headers)
print(f'habits/seed => {r9.status_code} - {r9.json()["status"]}')

print('=== ALL DONE ===')
