import feedparser
import requests
import os

RSS_FEEDS = [
    "https://openai.com/blog/rss.xml",
    "https://zenn.dev/feed",
    "https://qiita.com/popular-items/feed",
    "https://feeds.feedburner.com/oreilly/radar"
]

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

for url in RSS_FEEDS:
    feed = feedparser.parse(url)
    
    for entry in feed.entries[:3]:
        title = entry.title
        link = entry.link
        
        message = f"{title}\n{link}"
        
        requests.post(DISCORD_WEBHOOK, json={"content": message})