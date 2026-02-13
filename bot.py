import feedparser
import requests
import random
import os
import re

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

RSS_FEEDS = [
    "https://www.reuters.com/rssFeed/topNews",
    "https://feeds.bbci.co.uk/news/rss.xml",
    "https://www.theguardian.com/world/rss",
    "https://www.ft.com/rss/home",
    "https://www.rbc.ru/rss/news",
    "https://tass.ru/rss/v2.xml",
    "https://meduza.io/rss/all",
    "https://techcrunch.com/feed/",
    "https://www.theverge.com/rss/index.xml"
]

IMPORTANT_WORDS = [
    "war","санкц","президент","crisis","запрет","закон",
    "войн","конфликт","обвал","рост","падение",
    "AI","искусствен","рынок","доллар","эконом",
    "breaking","urgent","срочно","главное"
]


def clean(text):
    text = re.sub("<.*?>", "", text)
    return text.strip()


def is_important(text):
    text = text.lower()
    return any(word in text for word in IMPORTANT_WORDS)


def get_news():
    random.shuffle(RSS_FEEDS)

    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)

        for entry in feed.entries[:5]:

            title = clean(entry.title)
            summary = clean(entry.summary if "summary" in entry else "")

            combined = title + " " + summary

            if not is_important(combined):
                continue

            image = None

            if "media_content" in entry:
                image = entry.media_content[0].get("url")

            if not image and "links" in entry:
                for link in entry.links:
                    if "image" in link.type:
                        image = link.href

            text = f"""
📰 *{title}*

{summary[:700]}

📊 *Почему это важно:*  
Новость влияет на текущую ситуацию и может иметь последствия. Следим за развитием.
"""

            return text.strip(), image

    return None, None


def send_post(text, image_url=None):
    if not text:
        return

    if image_url:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        data = {
            "chat_id": CHAT_ID,
            "caption": text,
            "parse_mode": "Markdown"
        }
        requests.post(url, data=data)
    else:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "Markdown"
        }
        requests.post(url, data=data)


if __name__ == "__main__":
    text, image = get_news()
    send_post(text, image)
