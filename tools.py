import json
import os
import urllib.parse

import feedparser
import requests
import yfinance as yf
from langchain_core.tools import tool

HEADERS = {"User-Agent": "MarketResearcher/1.0"}

@tool
def get_company_profile(company_name: str) -> str:
    """Возвращает профиль компании: сфера деятельности, страна, сотрудники, капитализация.

    Args:
        company_name: Название компании (например, Apple, Tesla, Сбер)
    """
    print(f"[TOOL] Вызываю get_company_profile для {company_name}...")

    # Primary: yfinance
    try:
        ticker = yf.Ticker(company_name)
        info = ticker.info
        if info.get("longBusinessSummary"):
            parts = []
            if info.get("longBusinessSummary"):
                parts.append(info["longBusinessSummary"])
            sector = info.get("sector", "N/A")
            industry = info.get("industry", "N/A")
            country = info.get("country", "N/A")
            employees = info.get("fullTimeEmployees", "N/A")
            market_cap = info.get("marketCap", "N/A")
            website = info.get("website", "N/A")
            parts.append(
                f"\n\n**Сектор:** {sector}\n**Индустрия:** {industry}\n"
                f"**Страна:** {country}\n**Сотрудники:** {employees:,}\n"
                f"**Капитализация:** ${market_cap:,}\n"
                f"**Сайт:** {website}"
                if isinstance(employees, int) and isinstance(market_cap, int)
                else f"\n\n**Сектор:** {sector}\n**Индустрия:** {industry}\n"
                f"**Страна:** {country}\n**Сотрудники:** {employees}\n"
                f"**Капитализация:** {market_cap}\n"
                f"**Сайт:** {website}"
            )
            print(f"[TOOL] Получил ответ от get_company_profile")
            return "\n".join(parts)
    except Exception as e:
        print(f"[TOOL] yfinance error: {e}")

    # Fallback: Wikipedia REST API
    try:
        # Search for the best matching article (company-related)
        encoded_search = urllib.parse.quote(f"{company_name} company")
        search_url = (
            f"https://en.wikipedia.org/w/api.php?action=query&list=search"
            f"&srsearch={encoded_search}&format=json&srlimit=3"
        )
        search_resp = requests.get(search_url, timeout=10, headers=HEADERS)
        if search_resp.status_code == 200:
            results = search_resp.json().get("query", {}).get("search", [])
            # Score results: exact match > partial match > English suffixes
            scored = []
            company_lower = company_name.lower()
            for r in results:
                title = r["title"]
                title_lower = title.lower()
                score = 0
                if title_lower == company_lower:
                    score += 3
                elif company_lower in title_lower or title_lower in company_lower:
                    score += 2
                if "inc." in title_lower or "corp." in title_lower or "company" in title_lower:
                    score += 0.5
                scored.append((score, title))
            scored.sort(key=lambda x: -x[0])
            if scored:
                best_title = scored[0][1]
                encoded_title = urllib.parse.quote(best_title)
                summary_url = (
                    f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded_title}"
                )
                summary_resp = requests.get(summary_url, timeout=10, headers=HEADERS)
                if summary_resp.status_code == 200:
                    data = summary_resp.json()
                    extract = data.get("extract", "")
                    if extract:
                        print(
                            f"[TOOL] Получил ответ от get_company_profile"
                            f" (Wikipedia: {best_title})"
                        )
                        return f"{extract}\n\n*Источник: Wikipedia ({best_title})*"
    except Exception as e:
        print(f"[TOOL] Wikipedia error: {e}")

    print(f"[TOOL] Компания {company_name} не найдена ни в одном источнике")
    return f"ОШИБКА: Компания {company_name} не найдена ни в одном источнике."


@tool
def get_financial_news(company_name: str) -> list[str]:
    """Возвращает последние новости о компании.

    Args:
        company_name: Название компании (например, Apple, Tesla, Сбер)
    """
    print(f"[TOOL] Вызываю get_financial_news для {company_name}...")

    # Primary: Tavily Search API
    tavily_key = os.getenv("TAVILY_API_KEY")
    if tavily_key:
        try:
            from tavily import TavilyClient
            client = TavilyClient(api_key=tavily_key)
            response = client.search(
                query=f"{company_name} financial news",
                max_results=3,
            )
            results = response.get("results", [])
            if results:
                news_items = []
                for r in results:
                    title = r.get("title", "")
                    content = r.get("content", "")
                    news_items.append(f"**{title}**\n{content}")
                print(f"[TOOL] Получил ответ от get_financial_news (Tavily)")
                return news_items
        except Exception as e:
            print(f"[TOOL] Tavily error [{type(e).__name__}]: {e}, switching to RSS fallback")

    # Fallback: Google News RSS
    try:
        encoded_name = urllib.parse.quote(company_name)
        url = f"https://news.google.com/rss/search?q={encoded_name}+stock&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(url)
        entries = feed.entries[:5]
        if entries:
            news_items = []
            for entry in entries:
                title = entry.get("title", "")
                summary = entry.get("summary", "")
                published = entry.get("published", "")
                news_items.append(f"**{title}**\n{published}\n{summary}")
            print(f"[TOOL] Получил ответ от get_financial_news (RSS)")
            return news_items
    except Exception as e:
        print(f"[TOOL] RSS error: {e}")

    print(f"[TOOL] Новостей о компании {company_name} не найдено")
    return [f"Новостей о компании {company_name} не найдено."]
