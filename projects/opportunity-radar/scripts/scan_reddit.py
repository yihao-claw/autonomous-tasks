#!/usr/bin/env python3
"""Reddit scraper for Japan market pain point detection."""

import json
import logging
import time
from datetime import date
from pathlib import Path

import requests

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config" / "keywords_jp.json"
OUTPUT_DIR = BASE_DIR / "data" / "raw"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("scan_reddit")

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "OpportunityRadar/1.0 (research bot; contact: research@example.com)",
})

MAX_RETRIES = 3
RETRY_DELAY = 3
REQUEST_DELAY = 2.0  # Reddit is strict on rate limits


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def fetch_json(url: str) -> dict | None:
    for attempt in range(MAX_RETRIES):
        try:
            resp = SESSION.get(url, timeout=15)
            if resp.status_code == 429:
                wait = int(resp.headers.get("Retry-After", 60))
                log.warning("Rate limited by Reddit, waiting %ds", wait)
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
    text_lower = text.lower()
    return [kw for kw in keywords if kw.lower() in text_lower]


def scan_subreddit(subreddit: str, pain_signals: list[str]) -> list[dict]:
    log.info("Scanning subreddit: r/%s", subreddit)
    results = []
    after = None

    for page in range(3):  # 3 pages of 100
        url = f"https://www.reddit.com/r/{subreddit}/new.json?limit=100"
        if after:
            url += f"&after={after}"

        data = fetch_json(url)
        if not data or "data" not in data:
            break

        children = data["data"].get("children", [])
        for child in children:
            post = child.get("data", {})
            title = post.get("title", "")
            selftext = post.get("selftext", "")
            text = f"{title} {selftext}"
            matches = detect_pain_keywords(text, pain_signals)

            if matches:
                results.append({
                    "subreddit": subreddit,
                    "title": title,
                    "url": f"https://www.reddit.com{post.get('permalink', '')}",
                    "date": post.get("created_utc", ""),
                    "pain_keywords_found": matches,
                    "content_snippet": selftext[:500],
                    "score": len(matches),
                    "upvotes": post.get("ups", 0),
                    "num_comments": post.get("num_comments", 0),
                })

        after = data["data"].get("after")
        if not after:
            break

        time.sleep(REQUEST_DELAY)

    log.info("r/%s: found %d posts with pain signals", subreddit, len(results))
    return results


def main():
    config = load_config()
    pain_signals = config["pain_signals"]
    subreddits = config["subreddits"]

    all_results = []
    for sub in subreddits:
        try:
            results = scan_subreddit(sub, pain_signals)
            all_results.extend(results)
        except Exception as e:
            log.error("Error scanning r/%s: %s", sub, e)

    today = date.today().strftime("%Y%m%d")
    output_path = OUTPUT_DIR / f"reddit_{today}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    log.info("Saved %d results to %s", len(all_results), output_path)


if __name__ == "__main__":
    main()
