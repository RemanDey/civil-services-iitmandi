"""Runtime scraper for UPSC previous year question papers."""

from datetime import datetime, timedelta
import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


UPSC_PYQ_URL = "https://www.upsc.gov.in/examinations/previous-question-papers"
CACHE_TTL = timedelta(hours=6)

pyqs = [
    {"year": 2025, "exam": "UPSC CSE", "paper": "General Studies Paper I", "link": "#"},
    {"year": 2025, "exam": "UPSC CSE", "paper": "General Studies Paper II (CSAT)", "link": "#"},
    {"year": 2024, "exam": "UPSC CSE", "paper": "General Studies Paper I", "link": "#"},
    {"year": 2024, "exam": "UPSC IFoS", "paper": "Forestry Paper I", "link": "#"},
    {"year": 2023, "exam": "UPSC CSE", "paper": "GS Paper IV (Ethics)", "link": "#"},
]

_cache = {"fetched_at": None, "papers": []}


def _fetch_upsc_html():
    response = requests.get(
        UPSC_PYQ_URL,
        timeout=20,
        headers={"User-Agent": "CivilServicesIITMandi/1.0"},
    )
    response.raise_for_status()
    return response.text


def _clean_text(value):
    return " ".join(value.split())


def _paper_title(item):
    link = item.find("a", href=True)
    if link:
        link.extract()

    return _clean_text(item.get_text(" ", strip=True).strip(" ,"))


def _parse_upsc_pyqs(html):
    soup = BeautifulSoup(html, "html.parser")
    content = soup.select_one(".view-content") or soup
    papers = []
    year_pattern = re.compile(r"Year:\s*(\d{4})")

    for group in content.select(".view-grouping"):
        header = group.select_one(".view-grouping-header")
        if not header:
            continue

        year_match = year_pattern.search(_clean_text(header.get_text(" ", strip=True)))
        if not year_match:
            continue

        year = int(year_match.group(1))
        for table in group.select("table"):
            caption = table.find("caption")
            if not caption:
                continue

            exam = _clean_text(caption.get_text(" ", strip=True))
            for item in table.select("li"):
                link = item.find("a", href=True)
                if not link:
                    continue

                paper = _paper_title(item)
                href = urljoin(UPSC_PYQ_URL, link["href"])
                if paper and href.lower().endswith(".pdf"):
                    papers.append(
                        {
                            "year": year,
                            "exam": exam,
                            "paper": paper,
                            "link": href,
                        }
                    )

    if papers:
        return papers

    current_year = None
    for element in content.find_all(["div", "table"]):
        if element.name == "div" and "view-grouping-header" in element.get("class", []):
            year_match = year_pattern.search(_clean_text(element.get_text(" ", strip=True)))
            current_year = int(year_match.group(1)) if year_match else None
            continue

        if element.name != "table" or current_year is None:
            continue

        caption = element.find("caption")
        if not caption:
            continue

        exam = _clean_text(caption.get_text(" ", strip=True))
        for item in element.select("li"):
            link = item.find("a", href=True)
            if not link:
                continue

            paper = _paper_title(item)
            href = urljoin(UPSC_PYQ_URL, link["href"])
            if paper and href.lower().endswith(".pdf"):
                papers.append(
                    {
                        "year": current_year,
                        "exam": exam,
                        "paper": paper,
                        "link": href,
                    }
                )

    return papers


def get_pyqs(force_refresh=False):
    """Return UPSC PYQs, using a short-lived in-memory cache."""
    now = datetime.utcnow()
    cache_is_fresh = (
        _cache["fetched_at"] is not None
        and now - _cache["fetched_at"] < CACHE_TTL
        and _cache["papers"]
    )

    if cache_is_fresh and not force_refresh:
        return _cache["papers"]

    try:
        scraped_papers = _parse_upsc_pyqs(_fetch_upsc_html())
        if not scraped_papers:
            raise ValueError("no question papers found on UPSC page")

        _cache["fetched_at"] = now
        _cache["papers"] = scraped_papers
        return scraped_papers
    except Exception as exc:
        print(f"Warning: could not refresh UPSC PYQs: {exc}")
        return _cache["papers"] or pyqs
