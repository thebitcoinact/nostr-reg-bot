import feedparser
import os
import json
import random
from nostr.key import PrivateKey
from nostr.event import Event
from nostr.relay_manager import RelayManager

# 🧠 Mots-clés crypto
KEYWORDS = ["bitcoin", "btc", "crypto", "cryptocurrency", "digital asset"]

# 📡 Sources officielles
FEEDS = {
    "SEC": "https://www.sec.gov/rss/pressrelease.xml",
    "CFTC": "https://www.cftc.gov/PressRoom/PressReleases/rss.xml",
    "ESMA": "https://www.esma.europa.eu/press-news/esma-news/rss",
    "AMF": "https://www.amf-france.org/en/rss.xml",
    "FINMA": "https://www.finma.ch/en/rss/news.rss",
    "CySEC": "https://www.cysec.gov.cy/en-GB/news/rss/"
}

SEEN_FILE = "seen.json"


# 📦 Charger ce qui a déjà été posté
def load_seen():
    try:
        with open(SEEN_FILE, "r") as f:
            return set(json.load(f))
    except:
        return set()


# 💾 Sauvegarde anti-doublons
def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)


# 🔍 Filtre crypto
def is_crypto(text):
    text = text.lower()
    return any(k in text for k in KEYWORDS)


# ✍️ Templates de posts (IMPORTANT pour crédibilité)
def format_post(source, title, link):

    templates = [
        f"""🚨 {source} regulatory update

{title}

🧠 Impact: increased regulatory scrutiny on crypto markets

🔗 Source: {link}

#Bitcoin #Crypto #Regulation""",

        f"""⚖️ {source}: new crypto-related update

{title}

👉 Market implication: compliance pressure rising

🔗 {link}""",

        f"""📊 Regulatory signal from {source}

{title}

💡 Why it matters: affects crypto asset oversight globally

🔗 {link}"""
    ]

    return random.choice(templates)


# 📡 Publication sur Nostr
def post_to_nostr(message):
    sk = PrivateKey.from_nsec(os.environ["NOSTR_PRIVATE_KEY"])

    event = Event(content=message)
    sk.sign_event(event)

    relay_manager = RelayManager()
    relay_manager.add_relay("wss://relay.damus.io")
    relay_manager.add_relay("wss://relay.nostr.band")
    relay_manager.open_connections()
    relay_manager.publish_event(event)


# 🚀 MAIN LOGIC
def main():
    seen = load_seen()

    for source, url in FEEDS.items():
        feed = feedparser.parse(url)

        for entry in feed.entries:

            uid = entry.link

            if uid in seen:
                continue

            text = entry.title + " " + entry.get("summary", "")

            if is_crypto(text):
                message = format_post(source, entry.title, entry.link)
                post_to_nostr(message)
                print("Posted:", entry.title)

            seen.add(uid)

    save_seen(seen)


if __name__ == "__main__":
    main()
