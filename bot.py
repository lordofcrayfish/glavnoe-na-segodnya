import feedparser
import requests
import random
import os
import re
import json

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

DB = "posted.json"

RSS = [
    "https://www.reuters.com/rssFeed/topNews",
    "https://feeds.bbci.co.uk/news/rss.xml",
    "https://www.theguardian.com/world/rss",
    "https://meduza.io/rss/all",
    "https://lenta.ru/rss/news",
    "https://tass.ru/rss/v2.xml"
]

EMOJIS = ["⚡️","🌍","📊","🚨","💰","📉","📈"]

STRONG = [
    "войн","теракт","кризис","санкц","президент",
    "закон","конфликт","нато","обвал","чп",
    "war","attack","crisis","breaking"
]


def load():
    if os.path.exists(DB):
        return json.load(open(DB))
    return []


def save(d):
    json.dump(d,open(DB,"w"))


def clean(t):
    return re.sub("<.*?>","",t)


def score(text):
    t=text.lower()
    s=0
    for w in STRONG:
        if w in t:
            s+=5
    s+=len(t)//200
    return s


def translate(text):
    try:
        url="https://translate.googleapis.com/translate_a/single"
        params={
            "client":"gtx",
            "sl":"auto",
            "tl":"ru",
            "dt":"t",
            "q":text
        }
        r=requests.get(url,params=params).json()
        return r[0][0][0]
    except:
        return text


def get_image(entry):

    if "media_content" in entry:
        return entry.media_content[0]["url"]

    if "links" in entry:
        for l in entry.links:
            if "image" in l.get("type",""):
                return l["href"]

    return None


def make_post(title,summary):
    emoji=random.choice(EMOJIS)

    return f"""
{emoji} <b>{title}</b>

{summary[:800]}

<b>Почему это важно:</b> событие может повлиять на ситуацию дальше.
""".strip()


def get_news():

    posted=load()
    results=[]

    for url in RSS:
        feed=feedparser.parse(url)

        for e in feed.entries[:7]:

            title=clean(e.title)
            summary=clean(e.summary if "summary" in e else "")

            if title in posted:
                continue

            if score(title+summary)<3:
                continue

            title_ru=translate(title)
            summary_ru=translate(summary)

            img=get_image(e)

            results.append((title,title_ru,summary_ru,img))

    return results[:5]


def send(text,img):

    if img:
        url=f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        requests.post(url,data={
            "chat_id":CHAT_ID,
            "caption":text,
            "parse_mode":"HTML",
            "photo":img
        })
    else:
        url=f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url,data={
            "chat_id":CHAT_ID,
            "text":text,
            "parse_mode":"HTML"
        })


if __name__=="__main__":

    news=get_news()

    posted=load()

    for orig,title,summary,img in news:

        post=make_post(title,summary)
        send(post,img)

        posted.append(orig)

    save(posted)
