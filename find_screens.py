import json

with open(r'C:\Users\User\.gemini\antigravity\brain\21bd28ee-9b6a-411b-b4ce-7e51a1800a0c\.system_generated\steps\1046\output.txt', 'r') as f:
    data = json.load(f)

for screen in data['screens']:
    if 'Orchestration' in screen['title']:
        print(f"ID: {screen['name'].split('/')[-1]} | Title: {screen['title']}")
