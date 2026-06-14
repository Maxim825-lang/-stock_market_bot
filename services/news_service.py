"""
Fetches news from NewsAPI.org.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import requests

from utils.config import NEWS_API_KEY, NEWS_API_BASE_URL
from utils.formatters import format_news_item

logger = logging.getLogger(__name__)


@dataclass
class NewsItem:
    title: str
    source: str
    published_at: str
    url: str


def fetch_news(company_name: str, ticker: str, max_articles: int = 5) -> list[NewsItem]:
    """
    Fetch recent news articles from NewsAPI.
    Returns empty list if key is missing or request fails.
    """
    if not NEWS_API_KEY:
        return []

    # Build search query: company name + ticker
    query = f'"{company_name}" OR "{ticker}"'

    params = {
        "q": query,
        "sortBy": "publishedAt",
        "pageSize": max_articles,
        "language": "ru,en",
        "apiKey": NEWS_API_KEY,
    }

    try:
        resp = requests.get(NEWS_API_BASE_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        articles = data.get("articles", [])

        results = []
        for art in articles[:max_articles]:
            results.append(
                NewsItem(
                    title=art.get("title", "Без заголовка"),
                    source=art.get("source", {}).get("name", "Неизвестный источник"),
                    published_at=art.get("publishedAt", ""),
                    url=art.get("url", ""),
                )
            )
        return results

    except requests.exceptions.ConnectionError:
        logger.warning("No internet connection when fetching news.")
        return []
    except Exception as exc:
        logger.error("News fetch error: %s", exc)
        return []


def format_news(news_items: list[NewsItem]) -> str:
    """Format news items into a Telegram-ready string."""
    if not NEWS_API_KEY:
        return "📰 Новости недоступны: не указан <code>NEWS_API_KEY</code> в .env файле."

    if not news_items:
        return "📰 Новостей по данной компании не найдено."

    lines = [format_news_item(n.title, n.source, n.published_at, n.url) for n in news_items]
    return "\n\n".join(lines)
