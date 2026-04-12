import feedparser
import requests
import os
import json
from collections import Counter

# ===== 設定 =====

JP_FEEDS = [
    "https://www.itmedia.co.jp/rss/2.0/enterprise.xml",
    "https://www.publickey1.jp/atom.xml",
    "https://ledge.ai/feed/",
    "https://codezine.jp/rss/new/20/index.xml",
    "https://dev.classmethod.jp/feed/",
    "https://qiita.com/popular-items/feed"
]

TECH_FEEDS = [
    "https://techcrunch.com/feed/",
    "https://www.wired.com/feed/rss",
    "https://feeds.arstechnica.com/arstechnica/index",
    "https://www.theverge.com/rss/index.xml",
    "https://hnrss.org/frontpage"
]

REDDIT_FEEDS = [
    "https://www.reddit.com/r/artificial/.rss",
    "https://www.reddit.com/r/ChatGPT/.rss",
    "https://www.reddit.com/r/technology/.rss"
]

WEBHOOK_TOP3 = os.getenv("DISCORD_WEBHOOK_REDDIT")
WEBHOOK_AI = os.getenv("DISCORD_WEBHOOK_AI")
WEBHOOK_TECH = os.getenv("DISCORD_WEBHOOK_TECH")

SEEN_FILE = "seen.json"

# ===== 既読 =====
if os.path.exists(SEEN_FILE):
    with open(SEEN_FILE, "r") as f:
        seen_urls = set(json.load(f))
else:
    seen_urls = set()

new_seen_urls = set(seen_urls)

# ===== 投稿 =====
def post_to_discord(webhook, message):
    try:
        res = requests.post(webhook, json={"content": message})
        return res.status_code
    except Exception as e:
        print(e)
        return None

# ===== 個別投稿 =====
def post_individual(title, link, webhook, label):
    message = f"""【{label}】
{title}
{link}
"""
    post_to_discord(webhook, message)

# ===== データ収集 =====
all_articles = []

def fetch_rss(feeds, source):
    for url in feeds:
        feed = feedparser.parse(url)

        for entry in feed.entries[:3]:  # 投稿数制限
            if entry.link in seen_urls:
                continue

            title = entry.title
            link = entry.link

            # 👇 個別投稿（追加部分）
            if source == "jp":
                post_individual(title, link, WEBHOOK_AI, "AI・IT（教養）")

            elif source == "tech":
                post_individual(title, link, WEBHOOK_TECH, "海外ITニュース")

            # TOP3用
            all_articles.append({
                "title": title,
                "link": link,
                "source": source,
                "score": 1
            })

def fetch_reddit(feeds):
    for url in feeds:
        feed = feedparser.parse(url)

        for entry in feed.entries[:3]:
            if entry.link in seen_urls:
                continue

            score = entry.get("score", 1)

            all_articles.append({
                "title": entry.title,
                "link": entry.link,
                "source": "reddit",
                "score": score if score else 1
            })

# ===== 実行 =====
fetch_rss(JP_FEEDS, "jp")
fetch_rss(TECH_FEEDS, "tech")
fetch_reddit(REDDIT_FEEDS)

# ===== スコアリング =====
titles = [a["title"] for a in all_articles]

counter = Counter()
for t in titles:
    counter.update(t.lower().split())

for a in all_articles:
    words = a["title"].lower().split()
    trend = sum(counter[w] for w in words)

    if a["source"] == "reddit":
        a["score"] += 5

    a["score"] += trend

# ===== TOP3抽出 =====
top3 = sorted(all_articles, key=lambda x: x["score"], reverse=True)[:3]

# ===== 投稿（TOP3） =====
message = "🔥【AI・ITトレンド TOP3】\n\n"

for i, a in enumerate(top3, 1):
    label = "（Reddit🔥）" if a["source"] == "reddit" else ""

    message += f"""■{i}. {a['title']} {label}
{a['link']}

----------------------

"""

# Discord制限
message = message[:1900]

status = post_to_discord(WEBHOOK_TOP3, message)
print("TOP3投稿:", status)

# ===== 保存 =====
for a in top3:
    new_seen_urls.add(a["link"])

with open(SEEN_FILE, "w") as f:
    json.dump(list(new_seen_urls), f)
