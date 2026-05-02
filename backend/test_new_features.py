import requests, json

r = requests.post('http://localhost:8000/auth/login', json={'email':'test@example.com','password':'password'})
token = r.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

print('=== NEW FEATURES TEST ===')

r1 = requests.get('http://localhost:8000/analytics/heatmap', headers=headers)
hm = r1.json()
active_keys = [k for k,v in hm['heatmap'].items() if v > 0]
total = hm['total_completions']
active = hm['active_days']
print(f'heatmap => {r1.status_code}, total={total}, active_days={active}, sample={active_keys[:3]}')

r2 = requests.get('http://localhost:8000/psychological/daily-challenge', headers=headers)
challenge_data = r2.json().get('challenge', {})
print(f'daily-challenge => {r2.status_code}: {challenge_data}')

r3 = requests.get('http://localhost:8000/psychological/behavior/patterns', headers=headers)
p3 = r3.json()
print(f'behavior/patterns => {r3.status_code}: burnout={p3.get("burnout_score",0)}, patterns={len(p3.get("patterns",[]))}')

r4 = requests.get('http://localhost:8000/analytics/recommendations', headers=headers)
p4 = r4.json()
print(f'recommendations => {r4.status_code}: insights={p4.get("insights",[])}')

r5 = requests.post('http://localhost:8000/psychological/checkin', json={
    'mood': 'happy', 'energy_morning': 'high', 'energy_evening': 'medium', 'sleep_quality': 4
}, headers=headers)
p5 = r5.json()
print(f'checkin => {r5.status_code}: insight_keys={list(p5.get("insights",{}).keys())}')

print('=== ALL DONE ===')
