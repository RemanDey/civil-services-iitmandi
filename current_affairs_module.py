"""Runtime scraper for UPSC-focused current affairs."""

from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


DRISHTI_CURRENT_AFFAIRS_URL = "https://www.drishtiias.com/current-affairs-news-analysis-editorials"
PIB_RSS_URLS = [
    "https://www.pib.gov.in/RssMain.aspx?reg=48&lang=2",
    "https://pib.gov.in/RSSFeed.aspx?ModId=6&Lang=1&Regid=3",
]
CACHE_TTL = timedelta(hours=6)
MAX_ITEMS = 15

current_affairs = [
    {
        "date": "June 11, 2026",
        "category": "Economy",
        "title": "Understanding the Digital Rupee Expansion Framework",
        "summary": "An in-depth analysis of the Reserve Bank of India's newly rolled out programmable functionalities for CBDC-R and its impact on structural liquidity.",
        "link": "#",
    },
    {
        "date": "June 09, 2026",
        "category": "Environment",
        "title": "Global Biofuel Alliance: Targets vs Achievements",
        "summary": "Evaluating the clean energy transition benchmarks achieved by member countries under the GBA framework, specifically tracking ethanol blending mandates.",
        "link": "#",
    },
    {
        "date": "June 05, 2026",
        "category": "Polity",
        "title": "The Evolution of Cooperative Federalism via Article 263",
        "summary": "Examining recent recommendations by the Inter-State Council secretariat concerning structural consultative machinery during interstate river water conflicts.",
        "link": "#",
    },
]

_cache = {"fetched_at": None, "feeds": []}


def _fetch_html(url):
    response = requests.get(
        url,
        timeout=20,
        headers={"User-Agent": "CivilServicesIITMandi/1.0"},
    )
    response.raise_for_status()
    return response.text


def _clean_text(value):
    return " ".join(value.split())


def _format_date(value):
    if not value:
        return ""

    for fmt in ("%d %B %Y", "%d %b %Y", "%B %d, %Y", "%b %d, %Y"):
        try:
            return datetime.strptime(value.strip(), fmt).strftime("%B %d, %Y")
        except ValueError:
            continue

    try:
        return parsedate_to_datetime(value).strftime("%B %d, %Y")
    except (TypeError, ValueError):
        return _clean_text(value)


def _latest_drishti_daily_url(html):
    soup = BeautifulSoup(html, "html.parser")
    date_pattern = re.compile(r"\b\d{1,2}\s+[A-Za-z]+\s+\d{4}\b")

    for link in soup.find_all("a", href=True):
        text = _clean_text(link.get_text(" ", strip=True))
        href = link["href"]
        if "/current-affairs-news-analysis-editorials/news-analysis/" in href and date_pattern.search(text):
            return urljoin(DRISHTI_CURRENT_AFFAIRS_URL, href)

    for link in soup.find_all("a", href=True):
        href = link["href"]
        if "/current-affairs-news-analysis-editorials/news-analysis/" in href:
            return urljoin(DRISHTI_CURRENT_AFFAIRS_URL, href)

    return None


def _page_date(soup):
    match = re.search(
        r"\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b",
        _clean_text(soup.get_text(" ", strip=True)),
        re.IGNORECASE,
    )
    return _format_date(match.group(0)) if match else ""


def _nearest_previous_text(tag, names):
    for previous in tag.find_all_previous(names):
        text = _clean_text(previous.get_text(" ", strip=True))
        if text and text.lower() not in {"prev", "next"}:
            return text
    return ""


def _summary_after_heading(heading):
    saw_summary = False

    for element in heading.find_all_next(["h1", "h2", "h3", "p", "li"]):
        if element.name == "h1":
            break

        text = _clean_text(element.get_text(" ", strip=True))
        if not text:
            continue

        if element.name in {"h2", "h3"} and text.lower() == "summary":
            saw_summary = True
            continue

        if saw_summary and element.name in {"li", "p"}:
            return text

    for element in heading.find_all_next(["h1", "p", "li"]):
        if element.name == "h1":
            break

        text = _clean_text(element.get_text(" ", strip=True))
        if text and len(text) > 60:
            return text

    return ""


def _parse_drishti_daily(html, page_url):
    soup = BeautifulSoup(html, "html.parser")
    date = _page_date(soup)
    feeds = []
    seen_titles = set()

    for heading in soup.find_all("h1"):
        title = _clean_text(heading.get_text(" ", strip=True))
        if not title or title in seen_titles or len(title) < 8:
            continue

        link = heading.find("a", href=True)
        summary = _summary_after_heading(heading)
        if not summary:
            continue

        category = _nearest_previous_text(heading, ["h6", "h5"]) or "Current Affairs"
        seen_titles.add(title)
        feeds.append(
            {
                "date": date,
                "category": category,
                "title": title,
                "summary": summary,
                "link": urljoin(page_url, link["href"]) if link else page_url,
            }
        )

        if len(feeds) >= MAX_ITEMS:
            break

    return feeds


def _get_drishti_current_affairs():
    listing_html = _fetch_html(DRISHTI_CURRENT_AFFAIRS_URL)
    daily_url = _latest_drishti_daily_url(listing_html)
    if not daily_url:
        raise ValueError("no Drishti daily current-affairs page found")

    return _parse_drishti_daily(_fetch_html(daily_url), daily_url)


def _parse_pib_rss(xml):
    soup = BeautifulSoup(xml, "xml")
    feeds = []

    for item in soup.find_all("item"):
        title = _clean_text(item.title.get_text(" ", strip=True)) if item.title else ""
        link = _clean_text(item.link.get_text(" ", strip=True)) if item.link else "#"
        pub_date = _clean_text(item.pubDate.get_text(" ", strip=True)) if item.pubDate else ""
        summary = _clean_text(item.description.get_text(" ", strip=True)) if item.description else ""

        if title and summary:
            feeds.append(
                {
                    "date": _format_date(pub_date),
                    "category": "PIB",
                    "title": title,
                    "summary": summary,
                    "link": link or "#",
                }
            )

        if len(feeds) >= MAX_ITEMS:
            break

    return feeds


def _get_pib_current_affairs():
    for url in PIB_RSS_URLS:
        try:
            feeds = _parse_pib_rss(_fetch_html(url))
            if feeds:
                return feeds
        except Exception as exc:
            print(f"Warning: could not refresh PIB current affairs from {url}: {exc}")

    return []


def get_current_affairs(force_refresh=False):
    """Return current affairs, using a short-lived in-memory cache."""
    now = datetime.utcnow()
    cache_is_fresh = (
        _cache["fetched_at"] is not None
        and now - _cache["fetched_at"] < CACHE_TTL
        and _cache["feeds"]
    )

    if cache_is_fresh and not force_refresh:
        return _cache["feeds"]

    try:
        try:
            scraped_feeds = _get_drishti_current_affairs()
        except Exception as exc:
            print(f"Warning: could not refresh Drishti current affairs: {exc}")
            scraped_feeds = []

        scraped_feeds = scraped_feeds or _get_pib_current_affairs()
        if not scraped_feeds:
            raise ValueError("no current affairs found from Drishti or PIB")

        _cache["fetched_at"] = now
        _cache["feeds"] = scraped_feeds
        return scraped_feeds
    except Exception as exc:
        print(f"Warning: could not refresh current affairs: {exc}")
        return _cache["feeds"] or current_affairs
