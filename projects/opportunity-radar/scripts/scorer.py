#!/usr/bin/env python3
"""Opportunity scoring engine — aggregates pain points and scores opportunities."""

import json
import logging
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
OUTPUT_DIR = BASE_DIR / "data" / "processed"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("scorer")

# Weights for final score
WEIGHTS = {
    "pain_level": 0.30,
    "market_size": 0.20,
    "willingness_to_pay": 0.15,
    "competition": 0.15,
    "build_complexity": 0.10,
    "distribution": 0.10,
}

# Source reach estimates
SOURCE_REACH = {
    "ptt": 5,       # medium
    "dcard": 6,      # medium-high (younger demographic)
    "reddit": 3,     # smaller for Japan niche
    "appstore": 8,   # large
}

# Pay-related keywords
PAY_KEYWORDS = [
    "付費", "訂閱", "subscribe", "paid", "premium", "pro版",
    "買", "花錢", "worth paying", "subscription", "月費", "年費",
    "課金", "有料", "サブスク",
]

# Complexity keywords (presence = more complex)
COMPLEX_KEYWORDS = [
    "AI", "machine learning", "blockchain", "hardware", "IoT",
    "醫療", "金融", "法規", "regulation", "api串接",
]

# Distribution keywords
DISTRIBUTION_KEYWORDS = [
    "KOL", "YouTuber", "網紅", "社群", "community", "推薦給朋友",
    "分享", "group", "line群", "discord",
]


def load_today_files(prefix: str) -> list[dict]:
    """Load today's raw data files matching prefix."""
    today = date.today().strftime("%Y%m%d")
    pattern = f"{prefix}_{today}.json"
    path = RAW_DIR / pattern
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    # Fallback: find most recent file with prefix
    files = sorted(RAW_DIR.glob(f"{prefix}_*.json"), reverse=True)
    if files:
        log.info("Using fallback file: %s", files[0])
        with open(files[0], "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def cluster_by_keyword(all_posts: list[dict]) -> dict[str, list[dict]]:
    """Group posts by their pain keywords into clusters."""
    clusters = defaultdict(list)
    for post in all_posts:
        keywords = post.get("pain_keywords_found", [])
        for kw in keywords:
            clusters[kw].append(post)
    return dict(clusters)


def detect_keyword_in_text(text: str, keywords: list[str]) -> bool:
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in keywords)


def score_cluster(keyword: str, posts: list[dict], appstore_data: list[dict]) -> dict:
    """Score a pain point cluster."""
    # Pain level: frequency * average keyword density
    frequency = len(posts)
    avg_keywords = sum(len(p.get("pain_keywords_found", [])) for p in posts) / max(frequency, 1)
    pain_level = min(10, (frequency / 5) * avg_keywords)

    # Market size: based on source mix
    source_scores = []
    for post in posts:
        source = "ptt" if "board" in post else "dcard" if "forum" in post else "reddit" if "subreddit" in post else "appstore"
        source_scores.append(SOURCE_REACH.get(source, 3))
    market_size = min(10, sum(source_scores) / max(len(source_scores), 1) * 1.2)

    # Willingness to pay
    all_text = " ".join(p.get("content_snippet", "") + " " + p.get("title", "") for p in posts)
    wtp = 7.0 if detect_keyword_in_text(all_text, PAY_KEYWORDS) else 3.0

    # Competition: check if similar apps exist in appstore top charts
    # More apps in category = more competition = lower score
    related_apps = [a for a in appstore_data if keyword.lower() in a.get("name", "").lower()]
    if len(related_apps) > 10:
        competition = 3.0  # high competition
    elif len(related_apps) > 3:
        competition = 6.0
    else:
        competition = 9.0  # low competition = good

    # Build complexity
    complexity = 4.0 if detect_keyword_in_text(all_text, COMPLEX_KEYWORDS) else 7.0

    # Distribution potential
    distribution = 8.0 if detect_keyword_in_text(all_text, DISTRIBUTION_KEYWORDS) else 4.0

    scores = {
        "pain_level": round(pain_level, 1),
        "market_size": round(market_size, 1),
        "willingness_to_pay": round(wtp, 1),
        "competition": round(competition, 1),
        "build_complexity": round(complexity, 1),
        "distribution": round(distribution, 1),
    }

    total = sum(scores[k] * WEIGHTS[k] for k in WEIGHTS)

    # Evidence quotes
    evidence = []
    for p in posts[:5]:
        snippet = p.get("content_snippet", p.get("title", ""))[:200]
        if snippet:
            evidence.append({
                "source": p.get("board", p.get("forum", p.get("subreddit", "appstore"))),
                "quote": snippet,
                "url": p.get("url", ""),
            })

    return {
        "keyword": keyword,
        "post_count": frequency,
        "scores": scores,
        "total_score": round(total, 2),
        "is_hot": total > 7.0,
        "evidence": evidence,
    }


def main():
    log.info("Loading raw data...")

    # Load all sources
    ptt_data = load_today_files("ptt")
    dcard_data = load_today_files("dcard")
    reddit_data = load_today_files("reddit")
    appstore_rankings = load_today_files("appstore_rankings")
    appstore_reviews = load_today_files("appstore_reviews")

    # Normalize appstore review posts
    review_posts = []
    for app in appstore_reviews:
        for review in app.get("pain_reviews", []):
            review_posts.append({
                "title": review.get("title", ""),
                "content_snippet": review.get("content", ""),
                "pain_keywords_found": review.get("pain_keywords_found", []),
                "url": "",
                "source": "appstore",
            })

    all_posts = ptt_data + dcard_data + reddit_data + review_posts
    log.info("Total posts loaded: %d (PTT=%d, Dcard=%d, Reddit=%d, AppStore=%d)",
             len(all_posts), len(ptt_data), len(dcard_data), len(reddit_data), len(review_posts))

    if not all_posts:
        log.warning("No data found. Run scanners first.")
        # Save empty results
        today = date.today().strftime("%Y%m%d")
        output_path = OUTPUT_DIR / f"opportunities_{today}.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump([], f)
        return

    # Cluster by pain keyword
    clusters = cluster_by_keyword(all_posts)
    log.info("Found %d pain keyword clusters", len(clusters))

    # Score each cluster
    opportunities = []
    for keyword, posts in clusters.items():
        opp = score_cluster(keyword, posts, appstore_rankings)
        opportunities.append(opp)

    # Sort by total score descending
    opportunities.sort(key=lambda x: x["total_score"], reverse=True)

    today = date.today().strftime("%Y%m%d")
    output_path = OUTPUT_DIR / f"opportunities_{today}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(opportunities, f, ensure_ascii=False, indent=2)

    hot_count = sum(1 for o in opportunities if o["is_hot"])
    log.info("Saved %d opportunities (%d hot) to %s", len(opportunities), hot_count, output_path)


if __name__ == "__main__":
    main()
