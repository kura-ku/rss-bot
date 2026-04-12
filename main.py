import feedparser
import requests
import os
import json

# ===== 設定 =====

# 教養（日本RSS）
AI_FEEDS = [
    "https://www.itmedia.co.jp/rss/2.0/enterprise.xml",
    "https://www.publickey1.jp/atom.xml",
    "https://ledge.ai/feed/",
    "https://codezine.jp/rss/new/20/index.xml",
    "https://dev.classmethod.jp/feed/",
    "https://qiita.com/popular-items/feed"
]

# ITニュース
TECH_FEEDS = [
    "https://techcrunch.com/feed/",
    "https://www.wired.com/feed/rss",
    "https://feeds.arstechnica.com/arstechnica/index",
    "https://www.theverge.com/rss/index.xml",
    "https://hnrss.org/frontpage"
]

# Reddit（バズ用）
REDDIT_FEEDS = [
    "https://www.reddit.com/r/artificial/.rss",
    "https://www.reddit.com/r/ChatGPT/.rss",
    "https://www.reddit.com/r/technology/.rss"
]

# Webhook
WEBHOOK_AI = os.getenv("DISCORD_WEBHOOK_AI")
WEBHOOK_TECH = os.getenv("DISCORD_WEBHOOK_TECH")
WEBHOOK_REDDIT = os.getenv("DISCORD_WEBHOOK_REDDIT")

SEEN_FILE = "seen.json"

# ===== 既読 =====
if os.path.exists(SEEN_FILE):
    with open(SEEN_FILE, "r") as f:
        seen_urls = set(json.load(f))
else:
    seen_urls = set()

new_seen_urls = set(seen_urls)

# ===== 共通 =====
def post_to_discord(webhook, message):
    try:
        res = requests.post(webhook, json={"content": message})
        return res.status_code
    except Exception as e:
        print(f"エラー: {e}")
        return None

# ===== 通常RSS =====
def process_feeds(feeds, webhook, label):
    global new_seen_urls

    for url in feeds:
        feed = feedparser.parse(url)

        for entry in feed.entries[:5]:
            title = entry.title
            link = entry.link

            if link in seen_urls:
                continue

            message = f"""【{label}】
{title}
{link}
"""

            status = post_to_discord(webhook, message)

            print(f"{label}送信: {title} | {status}")

            if status == 204:
                new_seen_urls.add(link)

# ===== Reddit専用（重要）=====
def process_reddit(feeds, webhook):
    global new_seen_urls

    for url in feeds:
        feed = feedparser.parse(url)

        entries = []

        for entry in feed.entries:
            score = entry.get("score", 0)

            entries.append({
                "title": entry.title,
                "link": entry.link,
                "score": score if score else 1
            })

        # 👍 スコア順
        sorted_entries = sorted(entries, key=lambda x: x["score"], reverse=True)

        for e in sorted_entries[:5]:
            title = e["title"]
            link = e["link"]
            score = e["score"]

            if link in seen_urls:
                continue

            message = f"""【Redditトレンド🔥】
👍 {score}
{title}
{link}
"""

            status = post_to_discord(webhook, message)

            print(f"Reddit送信: {title} | {status}")

            if status == 204:
                new_seen_urls.add(link)

# ===== 実行 =====
process_feeds(AI_FEEDS, WEBHOOK_AI, "教養（日本IT）")
process_feeds(TECH_FEEDS, WEBHOOK_TECH, "海外ITニュース")

# 👇ここが今回の本質
process_reddit(REDDIT_FEEDS, WEBHOOK_REDDIT)

# ===== 保存 =====
with open(SEEN_FILE, "w") as f:
    json.dump(list(new_seen_urls), f)
