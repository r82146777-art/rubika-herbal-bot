import os
import json
import random
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = "c0Cr7CY010ddee1b54438f20491db663"
CHANNEL_LINK = os.getenv("CHANNEL_LINK", "https://rubika.ir/giahanedaroi")

def load_posts():
    with open("posts.json", "r", encoding="utf-8") as f:
        posts = json.load(f)
    return [p.replace("{link}", CHANNEL_LINK) for p in posts]

def is_within_posting_hours():
    """فقط بین ۸ صبح تا ۲۳ شب به وقت تهران پست بفرست"""
    tehran = ZoneInfo("Asia/Tehran")
    now = datetime.now(tehran)
    return 8 <= now.hour <= 23

def send_message(text: str):
    url = f"https://botapi.rubika.ir/v3/{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text
    }
    response = requests.post(url, json=payload, timeout=30)
    return response.json()

def main():
    if not TOKEN:
        print("❌ BOT_TOKEN تنظیم نشده است.")
        return

    if not is_within_posting_hours():
        print("⏰ خارج از ساعت ارسال (۸ صبح تا ۲۳). پیام ارسال نشد.")
        return

    posts = load_posts()
    post = random.choice(posts)
    print(f"تعداد کل محتوا: {len(posts)}")
    print(f"در حال ارسال پست...\n{post[:80]}...")

    result = send_message(post)
    print("نتیجه API:", result)

if __name__ == "__main__":
    main()
