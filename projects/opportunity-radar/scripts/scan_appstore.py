#!/usr/bin/env python3
"""App Store rankings and reviews scraper for Taiwan and Japan markets."""

import json
import logging
import time
from datetime import date
from pathlib import Path
from urllib.parse import quote

import requests

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config" / "categories.json"
TW_CONFIG = BASE_DIR / "config" / "keywords_tw.json"
JP_CONFIG = BASE_DIR / "config" / "keywords_jp.json"
OUTPUT_DIR = BASE_DIR / "data" / "raw"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("scan_appstore")

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) OpportunityRadar/1.0",
})

MAX_RETRIES = 3
RETRY_DELAY = 2
REQUEST_DELAY = 1.0


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def fetch_json(url: str) -> dict | None:
    for attempt in range(MAX_RETRIES):
        try:
            resp = SESSION.get(url, timeout=20)
            if resp.status_code == 429:
                time.sleep(RETRY_DELAY * (attempt + 2))
                continue
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            log.warning("Fetch %s attempt %d failed: %s", url, attempt + 1, e)
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))
    return None


def fetch_rankings(country: str, categories: list[str], top_n: int) -> list[dict]:
    """Fetch top grossing apps for each category in a country."""
    all_apps = []
    for category in categories:
        url = f"https://rss.applemarketingtools.com/api/v2/{country}/apps/top-grossing/{top_n}/{category}/apps.json"
        log.info("Fetching rankings: %s/%s", country, category)
        data = fetch_json(url)
        if not data:
            continue

        feed = data.get("feed", {})
        results = feed.get("results", [])
        for rank, app in enumerate(results, 1):
            all_apps.append({
                "country": country,
                "category": category,
                "rank": rank,
                "name": app.get("name", ""),
                "id": app.get("id", ""),
                "artist": app.get("artistName", ""),
                "url": app.get("url", ""),
            })

        time.sleep(REQUEST_DELAY)

    return all_apps


def fetch_app_reviews(app_id: str, country: str) -> list[dict]:
    """Fetch reviews for an app, focusing on low-rating ones."""
    url = f"https://itunes.apple.com/rss/customerreviews/id={app_id}/sortBy=mostRecent/page=1/json?l=en&cc={country}"
    data = fetch_json(url)
    if not data:
        return []

    reviews = []
    try:
        entries = data.get("feed", {}).get("entry", [])
        if isinstance(entries, dict):
            entries = [entries]

        for entry in entries:
            rating = int(entry.get("im:rating", {}).get("label", "5"))
            if rating <= 3:
                reviews.append({
                    "title": entry.get("title", {}).get("label", ""),
                    "content": entry.get("content", {}).get("label", "")[:500],
                    "rating": rating,
                    "author": entry.get("author", {}).get("name", {}).get("label", ""),
                })
    except (KeyError, TypeError, ValueError) as e:
        log.debug("Error parsing reviews for app %s: %s", app_id, e)

    return reviews


def detect_pain_in_reviews(reviews: list[dict], pain_signals: list[str]) -> list[dict]:
    """Filter reviews that contain pain signals."""
    flagged = []
    for review in reviews:
        text = f"{review.get('title', '')} {review.get('content', '')}"
        matches = [kw for kw in pain_signals if kw.lower() in text.lower()]
        if matches:
            review["pain_keywords_found"] = matches
            flagged.append(review)
    return flagged


def main():
    config = load_json(CONFIG_PATH)
    tw_config = load_json(TW_CONFIG)
    jp_config = load_json(JP_CONFIG)

    today = date.today().strftime("%Y%m%d")

    # Fetch rankings
    all_rankings = []
    for country, cats_key in [("tw", "appstore_categories_tw"), ("jp", "appstore_categories_jp")]:
        categories = config.get(cats_key, [])
        rankings = fetch_rankings(country, categories, config.get("top_n", 100))
        all_rankings.extend(rankings)

    rankings_path = OUTPUT_DIR / f"appstore_rankings_{today}.json"
    rankings_path.parent.mkdir(parents=True, exist_ok=True)
    with open(rankings_path, "w", encoding="utf-8") as f:
        json.dump(all_rankings, f, ensure_ascii=False, indent=2)
    log.info("Saved %d app rankings to %s", len(all_rankings), rankings_path)

    # Fetch reviews for top 10 apps per category (to avoid rate limits)
    all_pain_signals = tw_config["pain_signals"] + jp_config["pain_signals"]
    reviews_analysis = []

    # Deduplicate apps by ID
    seen_ids = set()
    unique_apps = []
    for app in all_rankings:
        if app["id"] not in seen_ids and app["rank"] <= 10:
            seen_ids.add(app["id"])
            unique_apps.append(app)

    log.info("Fetching reviews for %d unique top-10 apps", len(unique_apps))
    for app in unique_apps:
        reviews = fetch_app_reviews(app["id"], app["country"])
        flagged = detect_pain_in_reviews(reviews, all_pain_signals)
        if flagged:
            reviews_analysis.append({
                "app_name": app["name"],
                "app_id": app["id"],
                "country": app["country"],
                "category": app["category"],
                "rank": app["rank"],
                "pain_reviews": flagged,
            })
        time.sleep(REQUEST_DELAY)

    reviews_path = OUTPUT_DIR / f"appstore_reviews_{today}.json"
    with open(reviews_path, "w", encoding="utf-8") as f:
        json.dump(reviews_analysis, f, ensure_ascii=False, indent=2)
    log.info("Saved %d apps with pain reviews to %s", len(reviews_analysis), reviews_path)


if __name__ == "__main__":
    main()
