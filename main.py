import feedparser
import requests
import os
import json

# ===== 設定 =====

# AI系
AI_FEEDS = [
    "https://www.itmedia.co.jp/rss/2.0/enterprise.xml",
    "https://www.publickey1.jp/atom.xml",
    "https://ledge.ai/feed/",
    "https://codezine.jp/rss/new/20/index.xml",
    "https://dev.classmethod.jp/feed/",
    "https://qiita.com/popular-items/feed"
]

# IT・テックニュース
TECH_FEEDS = [
    "https://techcrunch.com/feed/",
    "https://www.wired.com/feed/rss",
    "https://feeds.arstechnica.com/arstechnica/index",
    "https://www.theverge.com/rss/index.xml",
    "https://hnrss.org/frontpage"
]

# Webhook（2つ用意）
WEBHOOK_AI = os.getenv("DISCORD_WEBHOOK_AI")
WEBHOOK_TECH = os.getenv("DISCORD_WEBHOOK_TECH")

SEEN_FILE = "seen.json"

# ===== 既読データ読み込み =====
if os.path.exists(SEEN_FILE):
    with open(SEEN_FILE, "r") as f:
        seen_urls = set(json.load(f))
else:
    seen_urls = set()

new_seen_urls = set(seen_urls)

# ===== 共通投稿関数 =====
def post_to_discord(webhook, message):
    try:
        response = requests.post(webhook, json={"content": message})
        return response.status_code
    except Exception as e:
        print(f"エラー: {e}")
        return None

# ===== RSS処理関数 =====
def process_feeds(feeds, webhook, label):
    global new_seen_urls

    for url in feeds:
        feed = feedparser.parse(url)

        for entry in feed.entries[:5]:
            title = entry.title
            link = entry.link

            # 重複チェック
            if link in seen_urls:
                continue

            message = f"""【{label}】
{title}
{link}
"""

            status = post_to_discord(webhook, message)

            print(f"{label}送信: {title} | ステータス: {status}")

            if status == 204:
                new_seen_urls.add(link)

# ===== 実行 =====
process_feeds(AI_FEEDS, WEBHOOK_AI, "新着AIニュース")
process_feeds(TECH_FEEDS, WEBHOOK_TECH, "IT・テックニュース")

# ===== 保存 =====
with open(SEEN_FILE, "w") as f:
    json.dump(list(new_seen_urls), f)
