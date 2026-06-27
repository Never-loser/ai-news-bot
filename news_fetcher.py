"""
دریافت اخبار هوش مصنوعی از Google News RSS
"""

import feedparser
import re
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# فیدهای Google News برای موضوعات مختلف AI
RSS_FEEDS = [
    "https://news.google.com/rss/search?q=artificial+intelligence&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=ChatGPT+OR+OpenAI+OR+Gemini+OR+Claude&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=machine+learning+deep+learning&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=LLM+language+model&hl=en-US&gl=US&ceid=US:en",
]

SEEN_URLS = set()   # جلوگیری از تکرار خبر در یک سشن


def clean_text(text: str) -> str:
    """پاک‌سازی HTML و کاراکترهای اضافی"""
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"&[a-zA-Z]+;", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_source(entry) -> str:
    """نام منبع خبر"""
    if hasattr(entry, "source") and entry.source:
        return entry.source.get("title", "")
    # Google News معمولاً منبع رو در عنوان با " - " جدا می‌کنه
    if " - " in entry.get("title", ""):
        return entry.title.rsplit(" - ", 1)[-1]
    return ""


def fetch_ai_news(count: int = 5) -> list[dict]:
    """
    اخبار AI رو از Google News RSS بگیر
    Returns: لیست dict با کلیدهای title, summary, url, source
    """
    articles = []
    seen = set(SEEN_URLS)

    for feed_url in RSS_FEEDS:
        if len(articles) >= count * 2:
            break
        try:
            logger.info(f"📡 Fetching: {feed_url}")
            feed = feedparser.parse(feed_url)

            for entry in feed.entries:
                url = entry.get("link", "")
                if not url or url in seen:
                    continue
                seen.add(url)

                title = clean_text(entry.get("title", ""))
                # حذف نام منبع از آخر عنوان
                if " - " in title:
                    title = title.rsplit(" - ", 1)[0]

                summary = clean_text(entry.get("summary", ""))
                if len(summary) > 300:
                    summary = summary[:300] + "..."

                source = extract_source(entry)

                articles.append({
                    "title":   title,
                    "summary": summary,
                    "url":     url,
                    "source":  source,
                })

        except Exception as e:
            logger.error(f"❌ Error fetching {feed_url}: {e}")

    # به‌روزرسانی SEEN_URLS
    SEEN_URLS.update(seen)

    # برگردوندن count تا خبر اول
    selected = articles[:count]
    logger.info(f"✅ Fetched {len(selected)} articles")
    return selected


if __name__ == "__main__":
    # تست مستقل
    logging.basicConfig(level=logging.INFO)
    news = fetch_ai_news(3)
    for i, n in enumerate(news, 1):
        print(f"\n--- {i} ---")
        print(f"Title:   {n['title']}")
        print(f"Summary: {n['summary'][:100]}...")
        print(f"Source:  {n['source']}")
        print(f"URL:     {n['url']}")
