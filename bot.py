import feedparser
import requests
import random
import os
import re
import json
import io
from PIL import Image, ImageDraw, ImageFont

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

DB = "posted.json"

RSS = [
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
    "war","attack","crisis","breaking","urgent"
]


# ---------------- база ----------------
def load():
    if os.path.exists(DB):
        return json.load(open(DB))
    return []

def save(d):
    json.dump(d, open(DB,"w"))

def clean(t):
    return re.sub("<.*?>","",t)


# ---------------- важность ----------------
def score(text):
    t=text.lower()
    s=0
    for w in STRONG:
        if w in t:
            s+=5
    s+=len(t)//200
    return s


# ---------------- перевод ----------------
def translate(text):
    try:
        r=requests.get(
            "https://translate.googleapis.com/translate_a/single",
            params={
                "client":"gtx",
                "sl":"auto",
                "tl":"ru",
                "dt":"t",
                "q":text
            },
            timeout=5
        ).json()
        return r[0][0][0]
    except:
        return text


# ---------------- HD картинка ----------------
def get_full_image(url):
    try:
        html=requests.get(url,timeout=6).text

        og=re.search(r'property="og:image" content="(.*?)"',html)
        if og:
            return og.group(1)

        tw=re.search(r'name="twitter:image" content="(.*?)"',html)
        if tw:
            return tw.group(1)

    except:
        return None

    return None


def get_rss_image(entry):

    if "media_content" in entry:
        return entry.media_content[0]["url"]

    if "links" in entry:
        for l in entry.links:
            if "image" in l.get("type",""):
                return l["href"]

    return None


# ---------------- брендирование изображения ----------------
def brand_image(url):

    try:
        r=requests.get(url,timeout=10)
        img=Image.open(io.BytesIO(r.content)).convert("RGB")

        draw=ImageDraw.Draw(img)
        text="ГЛАВНОЕ СЕГОДНЯ"

        size=int(img.width/18)

        try:
            font=ImageFont.truetype("DejaVuSans-Bold.ttf",size)
        except:
            font=ImageFont.load_default()

        w,h=draw.textsize(text,font=font)

        x=img.width-w-20
        y=img.height-h-20

        draw.rectangle((x-15,y-10,x+w+15,y+h+10),fill=(0,0,0))
        draw.text((x,y),text,font=font,fill=(255,255,255))

        path="temp.jpg"
        img.save(path,quality=95)

        return path

    except:
        return None


# ---------------- пост ----------------
def make_post(title,summary):
    emoji=random.choice(EMOJIS)

    return f"""
{emoji} <b>{title}</b>

{summary[:700]}

<b>Почему это важно:</b> событие может повлиять на ситуацию дальше.
""".strip()


# ---------------- сбор новостей ----------------
def get_news():

    posted=load()
    results=[]

    for url in RSS:

        try:
            feed=feedparser.parse(url)
        except:
            continue

        for e in feed.entries[:8]:

            title=clean(e.title)
            summary=clean(e.summary if "summary" in e else "")

            if title in posted:
                continue

            if score(title+summary)<3:
                continue

            title_ru=translate(title)
            summary_ru=translate(summary)

            img=get_full_image(e.link) or get_rss_image(e)

            results.append((title,title_ru,summary_ru,img))

    return results[:5]


# ---------------- отправка ----------------
def send(text,img):

    try:

        if img:
            img=brand_image(img) or img

            url=f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
            requests.post(url,data={
                "chat_id":CHAT_ID,
                "caption":text,
                "parse_mode":"HTML",
                "photo":img
            },timeout=10)

        else:
            url=f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            requests.post(url,data={
                "chat_id":CHAT_ID,
                "text":text,
                "parse_mode":"HTML"
            },timeout=10)

    except:
        pass


# ---------------- запуск ----------------
if __name__=="__main__":

    news=get_news()
    posted=load()

    for orig,title,summary,img in news:

        post=make_post(title,summary)
        send(post,img)

        posted.append(orig)

    save(posted)
