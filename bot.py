import feedparser
import requests
import random
import os
import sys

# === ENV ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    print("❌ BOT_TOKEN или CHAT_ID не заданы")
    sys.exit(1)

# === TEST MESSAGE ===
r = requests.post(
    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
    data={
        "chat_id": CHAT_ID,
        "text": "🟢 Бот запустился и может писать в канал"
    }
)

print("Telegram status:", r.status_code)
print("Telegram response:", r.text)

# === RSS источники ===
RSS_FEEDS = [
    "https://www.reuters.com/rssFeed/worldNews",
    "https://www.bbc.com/news/rss.xml",
    "https://www.rbc.ru/rss/news",
    "https://tass.ru/rss/v2.xml",
    "https://techcrunch.com/feed/"
]

def get_news():
    rss_url = random.choice(RSS_FEEDS)
    print(f"📡 Загружаю RSS: {rss_url}")

    feed = feedparser.parse(rss_url)

    if not feed.entries:
        print("❌ RSS пустой или недоступен")
        return None

    entry = random.choice(feed.entries)

    title = entry.get("title", "Без заголовка")
    link = entry.get("link", "")

    image = None
    if "media_content" in entry and entry.media_content:
        image = entry.media_content[0].get("url")

    text = f"📰 {title}\n\n{link}"
    return text, image

def send_post(text, image_url=None):
    if image_url:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        payload = {
            "chat_id": CHAT_ID,
            "caption": text
        }
        response = requests.post(url, data=payload)
    else:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": text
        }
        response = requests.post(url, data=payload)

    if response.status_code != 200:
        print("❌ Ошибка Telegram:", response.text)
    else:
        print("✅ Пост отправлен")

def main():
    result = get_news()

    if result is None:
        print("⏭ Нет новостей — выходим без ошибки")
        return

    text, image = result
    send_post(text, image)

if __name__ == "__main__":
    main()
