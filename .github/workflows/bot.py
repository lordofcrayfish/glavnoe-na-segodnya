import feedparser
import requests
import random
from datetime import datetime

import os
BOT_TOKEN = os.getenv("B8337666957:AAHsewVFCkroOm6kvOPPeJZQump4flReuZs")
CHAT_ID = os.getenv("C1003897211686D")

RSS_FEEDS = [
    "https://www.reuters.com/rssFeed/worldNews",
    "https://www.bbc.com/news/rss.xml",
    "https://www.rbc.ru/rss/news",
    "https://tass.ru/rss/v2.xml",
    "https://techcrunch.com/feed/"
]

def get_news():
    feed_url = random.choice(RSS_FEEDS)
    feed = feedparser.parse(feed_url)
    entry = random.choice(feed.entries)

    title = entry.title
    summary = entry.summary if 'summary' in entry else ''
    image = None

    if 'media_content' in entry:
        image = entry.media_content[0].get('url')

    text = (
        f"📰 Коротко:\n{title}\n\n"
        f"Почему это важно:\n{summary[:200]}..."
    )

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
    text, image = get_news()
    send_post(text, image)
