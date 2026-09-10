import os
import json
import hashlib
import random
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = "c0Cr7CY010ddee1b54438f20491db663"
CHANNEL_LINK = os.getenv("CHANNEL_LINK", "https://rubika.ir/giahanedaroi")
STATE_FILE = Path("state.json")

INTROS = [
    "در طب سنتی و گیاهی این گیاه جایگاه ویژه‌ای دارد.",
    "یکی از گیاهان پرکاربرد برای حفظ سلامت روزمره است.",
    "اگر به درمان‌های طبیعی علاقه دارید، این گیاه را بشناسید.",
    "مصرف هوشمندانه گیاهان دارویی می‌تواند مکمل سبک زندگی سالم باشد.",
    "قبل از مصرف مداوم در بیماری‌های خاص با متخصص مشورت کنید.",
    "شناخت درست گیاهان دارویی به استفاده ایمن‌تر از آن‌ها کمک می‌کند.",
    "این گیاه در خانه‌های ایرانی از دیرباز شناخته شده است.",
    "با رعایت تعادل می‌توان از خواص طبیعی آن بهره برد.",
]

CONTEXTS = [
    "برای استفاده روزمره",
    "به‌ویژه در فصل سرما",
    "بعد از غذاهای سنگین",
    "در برنامه آرامش شبانه",
    "همراه با سبک زندگی سالم",
]

def load_herbs():
    with open("herbs.json", "r", encoding="utf-8") as f:
        return json.load(f)

def build_all_posts():
    """بیش از ۱۲۰۰۰ پست یکتا — حدود ۲ سال با ۱۵ پست در روز بدون تکرار"""
    HERBS = load_herbs()
    footer = f"\n\n🔗 کانال گیاهان دارویی ارسباران:\n{CHANNEL_LINK}"
    posts = []
    for herb in HERBS:
        for fact in herb["f"]:
            for how in herb["h"]:
                for intro in INTROS:
                    for ctx in CONTEXTS:
                        text = (
                            f"{herb['e']} {herb['n']}\n\n"
                            f"{intro}\n\n"
                            f"{ctx}: {herb['n']} {fact}\n\n"
                            f"✅ {how}"
                            f"{footer}"
                        )
                        posts.append(text)
    pairs = [
        (0, 1), (0, 11), (1, 11), (2, 3), (3, 14), (6, 14), (7, 1),
        (9, 40), (10, 2), (12, 13), (15, 3), (19, 0), (25, 1), (26, 3),
        (4, 19), (27, 0), (29, 11), (31, 7), (33, 19), (38, 2),
    ]
    for i, j in pairs:
        if i < len(HERBS) and j < len(HERBS):
            a, b = HERBS[i], HERBS[j]
            text = (
                f"{a['e']} ترکیب {a['n']} و {b['n']}\n\n"
                f"این دو گیاه در کنار هم اثر مکمل دارند.\n\n"
                f"{a['n']}: {a['f'][0]}\n"
                f"{b['n']}: {b['f'][0]}\n\n"
                f"✅ دم‌کرده ترکیبی رقیق آن‌ها را می‌توانید میل کنید."
                f"{footer}"
            )
            posts.append(text)
    posts = list(dict.fromkeys(posts))
    posts.sort(key=lambda t: hashlib.md5(t.encode("utf-8")).hexdigest())
    return posts

def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"used": [], "cycle": 1}

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def pick_post(posts, state):
    used = set(state.get("used", []))
    available = []
    for p in posts:
        key = hashlib.md5(p.encode("utf-8")).hexdigest()[:16]
        if key not in used:
            available.append((key, p))
    if not available:
        state["used"] = []
        state["cycle"] = state.get("cycle", 1) + 1
        available = [(hashlib.md5(p.encode("utf-8")).hexdigest()[:16], p) for p in posts]
        print(f"♻️ دوره جدید شروع شد: cycle={state['cycle']}")
    key, post = random.choice(available)
    return key, post, state

def is_within_posting_hours():
    tehran = ZoneInfo("Asia/Tehran")
    now = datetime.now(tehran)
    return 8 <= now.hour <= 23

def send_message(text: str):
    url = f"https://botapi.rubika.ir/v3/{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    response = requests.post(url, json=payload, timeout=30)
    return response.json()

def main():
    if not TOKEN:
        print("❌ BOT_TOKEN تنظیم نشده است.")
        return
    if not is_within_posting_hours():
        print("⏰ خارج از ساعت ارسال (۸ صبح تا ۲۳). پیام ارسال نشد.")
        return
    posts = build_all_posts()
    state = load_state()
    key, post, state = pick_post(posts, state)
    print(f"کل پست‌های قابل تولید: {len(posts)}")
    print(f"ارسال‌شده در این دوره: {len(state.get('used', []))}")
    print(f"دوره: {state.get('cycle', 1)}")
    print(f"در حال ارسال...\n{post[:100]}...")
    result = send_message(post)
    print("نتیجه API:", result)
    if isinstance(result, dict) and result.get("status") == "OK":
        state.setdefault("used", []).append(key)
        save_state(state)
        print(f"✅ ذخیره شد. باقی‌مانده تقریبی این دوره: {len(posts) - len(state['used'])}")
    else:
        print("⚠️ ارسال ناموفق بود؛ state به‌روز نشد.")

if __name__ == "__main__":
    main()
