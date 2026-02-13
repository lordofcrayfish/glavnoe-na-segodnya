import feedparser
import requests
import random
import os
import re
import json
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

DB_FILE = "posted.json"

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
    "войн","санкц","президент","закон","кризис","обвал",
    "рост","падение","доллар","эконом","конфликт","нато",
    "ai","искусствен","рынок","скандал","запрет",
    "breaking","urgent","major","crisis","war"
]

ANALYSIS_PHRASES = [
    "Событие может повлиять на расстановку сил.",
    "Эксперты ожидают последствия в ближайшее время.",
    "Ситуация способна изменить текущую повестку.",
    "Это может отразиться на рынках и политике.",
    "Развитие событий может оказаться ключевым."
]


def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return []


def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)


def clean(text):
    return re.sub("<.*?>", "", text).strip()


def important_score(text):
    score = 0
    t = text.lower()

    strong = [
        "войн","санкц","президент","кризис","обвал","чп",
        "теракт","конфликт","нато","мобилизац","закон",
        "breaking","urgent","major","war","crash","collapse"
    ]

    medium = [
        "рынок","эконом","доллар","рост","падение",
        "ai","искусствен","технолог","компания"
    ]

    for w in strong:
        if w in t:
            score += 5

    for w in medium:
        if w in t:
            score += 2

    score += len(t)//300

    return score

    for word in IMPORTANT_WORDS:
        if word in text:
            score += 2

    score += len(text) // 200
    return score


def get_news():
    posted = load_db()
    random.shuffle(RSS_FEEDS)

    best = None
    best_score = 0

    for url in RSS_FEEDS:
        feed = feedparser.parse(url)

        for entry in feed.entries[:7]:

            title = clean(entry.title)
            summary = clean(entry.summary if "summary" in entry else "")

            if title in posted:
                continue

            text = title + " " + summary
            score = important_score(text)

            if score > best_score:
                best_score = score
                best = entry

    if not best or best_score < 2:
        return None, None

    title = clean(best.title)
    summary = clean(best.summary if "summary" in best else "")

    image = None

    if "media_content" in best:
        image = best.media_content[0].get("url")

    if not image and "links" in best:
        for link in best.links:
            if "image" in link.type:
                image = link.href

    analysis = random.choice(ANALYSIS_PHRASES)

    text = f"""
📰 *{title}*

{summary[:900]}

📊 *Почему это важно:*  
{analysis}
"""

    posted.append(title)
    save_db(posted)

    return text.strip(), image


def send(text, img=None):
    if not text:
        return

    if img:
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

def night_block():
    hour = datetime.utcnow().hour + 3
    return 1 <= hour <= 7

if __name__ == "__main__":
    if not night_block():
        t, i = get_news()
        send(t, i)
