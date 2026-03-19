#!/usr/bin/env python3
"""PTT scraper for Taiwan market pain point detection."""

import json
import logging
import os
import re
import sys
import time
from datetime import datetime, date
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config" / "keywords_tw.json"
OUTPUT_DIR = BASE_DIR / "data" / "raw"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("scan_ptt")

SESSION = requests.Session()
SESSION.cookies.set("over18", "1")
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) OpportunityRadar/1.0"
})

MAX_RETRIES = 3
RETRY_DELAY = 2
PAGES_PER_BOARD = 30
REQUEST_DELAY = 0.5


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def fetch(url: str) -> requests.Response | None:
    for attempt in range(MAX_RETRIES):
        try:
            resp = SESSION.get(url, timeout=15)
            resp.raise_for_status()
            return resp
        except requests.RequestException as e:
            log.warning("Fetch %s attempt %d failed: %s", url, attempt + 1, e)
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))
    return None


def get_board_max_page(board: str) -> int | None:
    """Get the latest index page number for a board."""
    resp = fetch(f"https://www.ptt.cc/bbs/{board}/index.html")
    if not resp:
        return None
    soup = BeautifulSoup(resp.text, "html.parser")
    # Find the "上頁" (previous page) link to determine max page
    for link in soup.select("div.btn-group-paging a"):
        href = link.get("href", "")
        m = re.search(r"/index(\d+)\.html", href)
        if m and "上頁" in link.text:
            return int(m.group(1)) + 1
    return None


def parse_post_list(html: str, board: str) -> list[dict]:
    """Parse a board index page and return post metadata."""
    soup = BeautifulSoup(html, "html.parser")
    posts = []
    for entry in soup.select("div.r-ent"):
        title_el = entry.select_one("div.title a")
        if not title_el:
            continue
        title = title_el.text.strip()
        href = title_el.get("href", "")
        url = f"https://www.ptt.cc{href}"
        date_el = entry.select_one("div.date")
        date_str = date_el.text.strip() if date_el else ""
        posts.append({"board": board, "title": title, "url": url, "date": date_str})
    return posts


def fetch_post_content(url: str) -> str:
    """Fetch and extract main content from a PTT post."""
    resp = fetch(url)
    if not resp:
        return ""
    soup = BeautifulSoup(resp.text, "html.parser")
    main = soup.select_one("div#main-content")
    if not main:
        return ""
    # Remove metadata lines and push tags
    for tag in main.select("div.article-metaline, div.article-metaline-right, div.push"):
        tag.decompose()
    return main.get_text(strip=True)[:2000]


def detect_pain_keywords(text: str, keywords: list[str]) -> list[str]:
    found = []
    for kw in keywords:
        if kw in text:
            found.append(kw)
    return found


def scan_board(board: str, pain_signals: list[str], pages: int = PAGES_PER_BOARD) -> list[dict]:
    log.info("Scanning board: %s (%d pages)", board, pages)
    max_page = get_board_max_page(board)
    if max_page is None:
        log.error("Cannot determine max page for %s, skipping", board)
        return []

    results = []
    start_page = max(1, max_page - pages + 1)

    for page_num in range(max_page, start_page - 1, -1):
        url = f"https://www.ptt.cc/bbs/{board}/index{page_num}.html"
        resp = fetch(url)
        if not resp:
            continue

        posts = parse_post_list(resp.text, board)
        for post in posts:
            # Check title first
            title_matches = detect_pain_keywords(post["title"], pain_signals)
            if not title_matches:
                continue

            time.sleep(REQUEST_DELAY)
            content = fetch_post_content(post["url"])
            content_matches = detect_pain_keywords(content, pain_signals)
            all_matches = list(set(title_matches + content_matches))

            results.append({
                "board": board,
                "title": post["title"],
                "url": post["url"],
                "date": post["date"],
                "pain_keywords_found": all_matches,
                "content_snippet": content[:500],
                "score": len(all_matches),
            })

        time.sleep(REQUEST_DELAY)

    log.info("Board %s: found %d posts with pain signals", board, len(results))
    return results


def main():
    config = load_config()
    pain_signals = config["pain_signals"]
    boards = config["boards_ptt"]

    all_results = []
    for board in boards:
        try:
            results = scan_board(board, pain_signals)
            all_results.extend(results)
        except Exception as e:
            log.error("Error scanning board %s: %s", board, e)

    today = date.today().strftime("%Y%m%d")
    output_path = OUTPUT_DIR / f"ptt_{today}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    log.info("Saved %d results to %s", len(all_results), output_path)


if __name__ == "__main__":
    main()
