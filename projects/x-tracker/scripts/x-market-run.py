#!/usr/bin/env python3
"""
X Market Run — scrape market-relevant accounts using Brightdata REST API.
Uses x-accounts-market.json. Writes results to x-tracker-state.json (seenIds)
and outputs structured JSON for the agent to process.
"""

import json
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).parent.parent
MONITOR_BASE = Path("/home/node/.openclaw/workspace/projects/x-monitor")
ACCOUNTS_FILE = BASE / "x-accounts-market.json"
STATE_FILE = BASE / "x-tracker-state.json"
SECRETS_PATH = Path("/home/node/.openclaw/agents/bird/agent/secrets/brightdata.json")

DATASET_ID = "gd_lwxmeb2u1cniijd7t4"
BASE_URL = "https://api.brightdata.com/datasets/v3"
MAX_POSTS_PER_HANDLE = 8

sys.path.insert(0, str(MONITOR_BASE))
from x_rate_limiter import RateLimiter


def load_token() -> str:
    return json.loads(SECRETS_PATH.read_text())["BRIGHTDATA_API_TOKEN"]


def trigger_scrape(token: str, handles: list, max_posts: int = MAX_POSTS_PER_HANDLE) -> str:
    url = f"{BASE_URL}/trigger?dataset_id={DATASET_ID}&format=json&uncompressed_webhook=true&notify=false&include_errors=true"
    payload = [{"url": f"https://x.com/{h.lstrip('@')}", "max_number_of_posts": max_posts} for h in handles]
    req = urllib.request.Request(url, method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, json.dumps(payload).encode()) as resp:
        data = json.loads(resp.read())
        return data["snapshot_id"]


def poll_snapshot(token: str, snapshot_id: str, timeout: int = 180, interval: int = 5) -> list:
    url = f"{BASE_URL}/snapshot/{snapshot_id}?format=json"
    deadline = time.time() + timeout
    while time.time() < deadline:
        req = urllib.request.Request(url)
        req.add_header("Authorization", f"Bearer {token}")
        try:
            with urllib.request.urlopen(req) as resp:
                if resp.status == 200:
                    return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code == 202:
                pass
            else:
                raise
        time.sleep(interval)
    raise TimeoutError(f"Snapshot {snapshot_id} not ready after {timeout}s")


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"seenIds": {}, "lastCheck": None}


def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False))


def extract_new_tweets(profile: dict, handle_key: str, seen: set, max_new: int = 5) -> list:
    posts = profile.get("posts") or []
    new_tweets = []
    for p in posts:
        post_id = str(p.get("post_id", ""))
        if not post_id or post_id in seen:
            continue
        text = p.get("description", "").strip()
        if len(text) < 10:
            continue
        new_tweets.append({
            "id": post_id,
            "date": p.get("date_posted", ""),
            "text": text,
            "url": p.get("post_url", f"https://x.com/{handle_key}/status/{post_id}"),
        })
        if len(new_tweets) >= max_new:
            break
    return new_tweets


def main():
    token = load_token()
    accounts = json.loads(ACCOUNTS_FILE.read_text())
    enabled = [a for a in accounts if a.get("enabled", True)]

    rl = RateLimiter()
    status = rl.status()
    print(f"[rate] {status['used']}/{status['budget']} used this month ({status['usage_pct']}%)", file=sys.stderr)

    if not rl.can_request(count=1):
        print("[rate] BUDGET EXHAUSTED", file=sys.stderr)
        print(json.dumps({"error": "budget_exhausted", "results": []}))
        return

    handles = [a["handle"] for a in enabled]
    handle_map = {a["handle"].lstrip("@").lower(): a for a in enabled}

    print(f"Triggering scrape for {len(handles)} market handles...", file=sys.stderr)
    t0 = time.time()
    snapshot_id = trigger_scrape(token, handles, MAX_POSTS_PER_HANDLE)
    print(f"Snapshot: {snapshot_id}", file=sys.stderr)

    profiles = poll_snapshot(token, snapshot_id, timeout=180, interval=5)
    elapsed = time.time() - t0
    print(f"Got {len(profiles)} profiles in {elapsed:.1f}s", file=sys.stderr)

    rl.record(count=1, source="market-run-batch", handle=f"{len(handles)}-market-handles")

    state = load_state()
    if "seenIds" not in state:
        state["seenIds"] = {}

    results = []
    for profile in profiles:
        handle = str(profile.get("id", "")).lstrip("@")
        if not handle:
            continue
        handle_key = handle.lower()
        account_info = handle_map.get(handle_key, {})
        seen = set(state["seenIds"].get(handle_key, []))
        new_tweets = extract_new_tweets(profile, handle_key, seen, max_new=5)

        if new_tweets:
            if handle_key not in state["seenIds"]:
                state["seenIds"][handle_key] = []
            state["seenIds"][handle_key].extend([t["id"] for t in new_tweets])
            state["seenIds"][handle_key] = state["seenIds"][handle_key][-200:]
            print(f"  @{handle}: {len(new_tweets)} new", file=sys.stderr)
        else:
            print(f"  @{handle}: no new", file=sys.stderr)

        results.append({
            "handle": handle,
            "name": account_info.get("name", handle),
            "category": account_info.get("category", ""),
            "note": account_info.get("note", ""),
            "hasNew": len(new_tweets) > 0,
            "newTweets": new_tweets,
        })

    state["lastCheck"] = datetime.now(timezone.utc).isoformat()
    save_state(state)

    print(json.dumps({"results": results, "elapsed": round(elapsed, 1)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
