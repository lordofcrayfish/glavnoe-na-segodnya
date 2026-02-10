import feedparser
import requests
import random
from datetime import datetime

import os
BOT_TOKEN = os.getenv("")
CHAT_ID = os.getenv("C1003897211686D")

RSS_FEEDS = [
    "https://www.reuters.com/rssFeed/worldNews",
    "https://www.bbc.com/news/rss.xml",
    "https://www.rbc.ru/rss/news",
    "https://tass.ru/rss/v2.xml",
    "https://techcrunch.com/feed/"
]

def get_news():
    feed = feedparser.parse(RSS_URL)

    if not feed.entries:
        print("❌ RSS пустой")
        return None

    entry = random.choice(feed.entries)

    title = entry.title
    link = entry.link

    image = None
    if "media_content" in entry:
        image = entry.media_content[0].get("url")

    text = f"📰 {title}\n\n{link}"
    return text, image

def send_post(text, image_url=None):
    if image_url:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        data = {
            "chat_id": CHAT_ID,
            "caption": text
        }
        files = {"photo": image_url}
        requests.post(url, data=data, files=files)
    else:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": CHAT_ID,
            "text": text
        }
        requests.post(url, data=data)

if __name__ == "__main__":
    result = get_news()
if result is None:
    print("⏭ Нет новостей")
    exit(0)

text, image = result
    send_post(text, image)
