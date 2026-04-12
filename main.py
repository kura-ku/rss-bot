import feedparser
import requests
import os
import json

# ===== 設定 =====
RSS_FEEDS = [
    "https://openai.com/blog/rss.xml",
    "https://deepmind.google/blog/rss.xml",
    "https://ai.googleblog.com/feeds/posts/default",
    "https://feeds.feedburner.com/kdnuggets-data-mining-analytics",
    "https://towardsdatascience.com/feed",
    "https://aifeed.dev/feed.xml"
]

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
SEEN_FILE = "seen.json"

# ===== 既読データ読み込み =====
if os.path.exists(SEEN_FILE):
    with open(SEEN_FILE, "r") as f:
        seen_urls = set(json.load(f))
else:
    seen_urls = set()

new_seen_urls = set(seen_urls)

# ===== RSS処理 =====
for url in RSS_FEEDS:
    feed = feedparser.parse(url)

    for entry in feed.entries[:5]:
        title = entry.title
        link = entry.link

        # 重複チェック
        if link in seen_urls:
            continue

        message = f"""【新着AIニュース】
{title}
{link}
"""

        try:
            response = requests.post(
                DISCORD_WEBHOOK,
                json={"content": message}
            )

            print(f"送信: {title} | ステータス: {response.status_code}")

            if response.status_code == 204:
                new_seen_urls.add(link)

        except Exception as e:
            print(f"エラー: {e}")

# ===== 保存 =====
with open(SEEN_FILE, "w") as f:
    json.dump(list(new_seen_urls), f)
