import feedparser
import os
import json
from nostr.key import PrivateKey
from nostr.event import Event
from nostr.relay_manager import RelayManager

KEYWORDS = ["bitcoin", "btc", "crypto", "cryptocurrency", "digital asset"]

FEEDS = {
    "SEC": "https://www.sec.gov/rss/pressrelease.xml",
    "CFTC": "https://www.cftc.gov/PressRoom/PressReleases/rss.xml",
    "ESMA": "https://www.esma.europa.eu/press-news/esma-news/rss",
    "AMF": "https://www.amf-france.org/en/rss.xml",
    "FINMA": "https://www.finma.ch/en/rss/news.rss",
    "CySEC": "https://www.cysec.gov.cy/en-GB/news/rss/"
}

SEEN_FILE = "seen.json"

def load_seen():
    try:
        with open(SEEN_FILE, "r") as f:
            return set(json.load(f))
    except:
        return set()

def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)

def is_crypto(text):
    text = text.lower()
    return any(k in text for k in KEYWORDS)

def format_post(source, title, link):
    return f"""🚨 {source}

{title}

👉 {link}

#Bitcoin #Crypto"""

def post(message):
    sk = PrivateKey.from_nsec(os.environ["NOSTR_PRIVATE_KEY"])
    event = Event(content=message)
    sk.sign_event(event)

    rm = RelayManager()
    rm.add_relay("wss://relay.damus.io")
    rm.open_connections()
    rm.publish_event(event)

def main():
    seen = load_seen()

    for source, url in FEEDS.items():
        feed = feedparser.parse(url)

        for entry in feed.entries:
            uid = entry.link

            if uid in seen:
                continue

            text = entry.title + entry.get("summary", "")

            if is_crypto(text):
                msg = format_post(source, entry.title, entry.link)
                post(msg)
                print("Posted:", entry.title)

            seen.add(uid)

    save_seen(seen)

if __name__ == "__main__":
    main()
