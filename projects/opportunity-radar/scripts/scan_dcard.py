#!/usr/bin/env python3
"""Dcard scraper for Taiwan market pain point detection."""

import json
import logging
import time
from datetime import date
from pathlib import Path

import requests

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config" / "keywords_tw.json"
OUTPUT_DIR = BASE_DIR / "data" / "raw"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("scan_dcard")

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) OpportunityRadar/1.0",
})

MAX_RETRIES = 3
RETRY_DELAY = 2
POSTS_PER_FORUM = 150  # 5 pages of 30
REQUEST_DELAY = 1.0


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def fetch_json(url: str) -> list | dict | None:
    for attempt in range(MAX_RETRIES):
        try:
            resp = SESSION.get(url, timeout=15)
            if resp.status_code == 429:
                wait = int(resp.headers.get("Retry-After", RETRY_DELAY * (attempt + 2)))
                log.warning("Rate limited, waiting %ds", wait)
                time.sleep(wait)
                continue
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            log.warning("Fetch %s attempt %d failed: %s", url, attempt + 1, e)
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))
    return None


def detect_pain_keywords(text: str, keywords: list[str]) -> list[str]:
    return [kw for kw in keywords if kw in text]


def scan_forum(forum: str, pain_signals: list[str]) -> list[dict]:
    log.info("Scanning Dcard forum: %s", forum)
    results = []
    before = None

    for page in range(5):
        url = f"https://www.dcard.tw/service/api/v2/forums/{forum}/posts?popular=false&limit=30"
        if before:
            url += f"&before={before}"

        posts = fetch_json(url)
        if not posts or not isinstance(posts, list):
            break

        for post in posts:
            title = post.get("title", "")
            excerpt = post.get("excerpt", "")
            text = f"{title} {excerpt}"
            matches = detect_pain_keywords(text, pain_signals)

            if matches:
                results.append({
                    "forum": forum,
                    "title": title,
                    "url": f"https://www.dcard.tw/f/{forum}/p/{post.get('id', '')}",
                    "date": post.get("createdAt", ""),
                    "pain_keywords_found": matches,
                    "content_snippet": excerpt[:500],
                    "score": len(matches),
                    "like_count": post.get("likeCount", 0),
                    "comment_count": post.get("commentCount", 0),
                })

        if posts:
            before = posts[-1].get("id")

        time.sleep(REQUEST_DELAY)

    log.info("Forum %s: found %d posts with pain signals", forum, len(results))
    return results


def main():
    config = load_config()
    pain_signals = config["pain_signals"]
    forums = config["boards_dcard"]

    all_results = []
    for forum in forums:
        try:
            results = scan_forum(forum, pain_signals)
            all_results.extend(results)
        except Exception as e:
            log.error("Error scanning forum %s: %s", forum, e)

    today = date.today().strftime("%Y%m%d")
    output_path = OUTPUT_DIR / f"dcard_{today}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    log.info("Saved %d results to %s", len(all_results), output_path)


if __name__ == "__main__":
    main()
