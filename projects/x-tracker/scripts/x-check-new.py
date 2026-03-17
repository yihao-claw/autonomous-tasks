#!/usr/bin/env python3
"""
x-check-new.py — Parse scraped X profile markdown, extract tweets, deduplicate against state.

Usage:
    echo "<markdown>" | python3 x-check-new.py --handle @AndrewYNg --state state.json

Outputs JSON: {"hasNew": true/false, "newTweets": [...], "handle": "@..."}
"""

import argparse, json, re, sys, os
from datetime import datetime, timezone


def extract_tweets(markdown: str, handle: str) -> list[dict]:
    """Extract tweets from Brightdata's scraped X profile markdown."""
    tweets = []

    # Pattern: look for tweet-like blocks with timestamps and engagement
    # Brightdata returns X profiles with posts containing text + metadata
    lines = markdown.split('\n')
    current_tweet = []
    in_tweet = False

    for i, line in enumerate(lines):
        # Detect tweet boundaries — look for the handle pattern or date patterns
        # X profile pages show: username, handle, date, text, engagement
        stripped = line.strip()

        # Skip navigation/UI elements
        if any(skip in stripped.lower() for skip in [
            'iniciar sesión', 'regístrate', 'ver posts', 'siguiendo',
            'seguidores', 'mostrar más', 'se unió', 'traducir',
            'fecha de nacimiento', 'posts de ', 'respuestas',
            'destacados', 'artículos', 'multimedia', 'fijado'
        ]):
            continue

        # Look for date patterns like "7 ene.", "27 abr. 2023", "14h", "2d"
        date_match = re.match(
            r'^\[?\d{1,2}\s+(ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic)\.?\s*(\d{4})?\]?$',
            stripped, re.IGNORECASE
        )
        time_match = re.match(r'^\d{1,2}[hmd]$', stripped)

        if date_match or time_match:
            # Save previous tweet if any
            if current_tweet:
                text = '\n'.join(current_tweet).strip()
                if len(text) > 20:  # Filter out noise
                    tweets.append({
                        'text': text,
                        'id': _tweet_hash(text),
                    })
            current_tweet = []
            in_tweet = True
            continue

        # Engagement metrics line (likes, retweets etc) — ends a tweet
        if re.match(r'^\d[\d,.]*\s*(mil|K|M)?$', stripped):
            continue

        # Skip link-only lines that are X internal navigation
        if re.match(r'^\[.*\]\(/\w+', stripped):
            continue

        # Accumulate tweet text
        if stripped and not stripped.startswith('[') and not stripped.startswith('\\['):
            if in_tweet or len(stripped) > 30:
                current_tweet.append(stripped)
                in_tweet = True

    # Don't forget last tweet
    if current_tweet:
        text = '\n'.join(current_tweet).strip()
        if len(text) > 20:
            tweets.append({
                'text': text,
                'id': _tweet_hash(text),
            })

    return tweets


def _tweet_hash(text: str) -> str:
    """Generate a short deterministic hash for dedup."""
    import hashlib
    # Use first 200 chars to avoid minor rendering differences
    return hashlib.sha256(text[:200].encode()).hexdigest()[:16]


def load_state(path: str) -> dict:
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {"seenHashes": {}, "lastCheck": None}


def save_state(path: str, state: dict):
    with open(path, 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--handle', required=True, help='X handle e.g. @AndrewYNg')
    parser.add_argument('--state', default='x-tracker-state.json')
    parser.add_argument('--update-state', action='store_true',
                        help='Mark new tweets as seen in state')
    parser.add_argument('--max', type=int, default=10, help='Max new tweets to return')
    args = parser.parse_args()

    markdown = sys.stdin.read()
    if not markdown.strip():
        print(json.dumps({"hasNew": False, "error": "empty input", "handle": args.handle}))
        sys.exit(0)

    state = load_state(args.state)
    handle_key = args.handle.lower().lstrip('@')
    seen = set(state.get("seenHashes", {}).get(handle_key, []))

    all_tweets = extract_tweets(markdown, args.handle)
    new_tweets = [t for t in all_tweets if t['id'] not in seen][:args.max]

    if args.update_state and new_tweets:
        if "seenHashes" not in state:
            state["seenHashes"] = {}
        if handle_key not in state["seenHashes"]:
            state["seenHashes"][handle_key] = []
        state["seenHashes"][handle_key].extend([t['id'] for t in new_tweets])
        # Keep last 500 hashes per handle
        state["seenHashes"][handle_key] = state["seenHashes"][handle_key][-500:]
        state["lastCheck"] = datetime.now(timezone.utc).isoformat()
        save_state(args.state, state)

    result = {
        "hasNew": len(new_tweets) > 0,
        "newCount": len(new_tweets),
        "totalScraped": len(all_tweets),
        "handle": args.handle,
        "newTweets": new_tweets,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
