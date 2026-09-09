import os
import requests
import json

TOKEN = os.getenv("BOT_TOKEN")

url = f"https://botapi.rubika.ir/v3/{TOKEN}/getUpdates"
response = requests.post(url, json={"limit": 20}, timeout=30)
print(json.dumps(response.json(), ensure_ascii=False, indent=2))
