#!/usr/bin/env python3
"""
X (Twitter) profile scraper using Brightdata REST API (datasets/v3).
Much faster than MCP: batch support, no cold start, structured JSON output.

Usage:
  python3 x-scrape-rest.py --handles karpathy,sama --max-posts 5
  python3 x-scrape-rest.py --handles karpathy --max-posts 10 --timeout 120

Output: JSON array of profile objects with posts.
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error

SECRETS_PATH = "/home/node/.openclaw/agents/bird/agent/secrets/brightdata.json"
DATASET_ID = "gd_lwxmeb2u1cniijd7t4"  # Twitter profile scraper
BASE_URL = "https://api.brightdata.com/datasets/v3"


def load_token():
    with open(SECRETS_PATH) as f:
        return json.load(f)["BRIGHTDATA_API_TOKEN"]


def trigger_scrape(token: str, handles: list[str], max_posts: int = 5) -> str:
    """Trigger async scrape, return snapshot_id."""
    url = f"{BASE_URL}/trigger?dataset_id={DATASET_ID}&format=json&uncompressed_webhook=true&notify=false&include_errors=true"
    payload = [{"url": f"https://x.com/{h.lstrip('@')}", "max_number_of_posts": max_posts} for h in handles]
    
    req = urllib.request.Request(url, method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    
    with urllib.request.urlopen(req, json.dumps(payload).encode()) as resp:
        data = json.loads(resp.read())
        return data["snapshot_id"]


def poll_snapshot(token: str, snapshot_id: str, timeout: int = 120, interval: int = 5) -> list:
    """Poll for results until ready or timeout."""
    url = f"{BASE_URL}/snapshot/{snapshot_id}?format=json"
    deadline = time.time() + timeout
    
    while time.time() < deadline:
        req = urllib.request.Request(url)
        req.add_header("Authorization", f"Bearer {token}")
        
        try:
            with urllib.request.urlopen(req) as resp:
                status = resp.status
                if status == 200:
                    return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code == 202:  # Still processing
                pass
            else:
                raise
        
        time.sleep(interval)
    
    raise TimeoutError(f"Snapshot {snapshot_id} not ready after {timeout}s")


def main():
    parser = argparse.ArgumentParser(description="Scrape X profiles via Brightdata REST API")
    parser.add_argument("--handles", required=True, help="Comma-separated handles")
    parser.add_argument("--max-posts", type=int, default=5, help="Max posts per profile")
    parser.add_argument("--timeout", type=int, default=120, help="Poll timeout in seconds")
    parser.add_argument("--poll-interval", type=int, default=5, help="Poll interval in seconds")
    args = parser.parse_args()
    
    handles = [h.strip() for h in args.handles.split(",") if h.strip()]
    token = load_token()
    
    # Trigger
    t0 = time.time()
    snapshot_id = trigger_scrape(token, handles, args.max_posts)
    print(f"Triggered snapshot: {snapshot_id} for {len(handles)} handles", file=sys.stderr)
    
    # Poll
    results = poll_snapshot(token, snapshot_id, args.timeout, args.poll_interval)
    elapsed = time.time() - t0
    print(f"Got {len(results)} results in {elapsed:.1f}s", file=sys.stderr)
    
    # Output
    json.dump(results, sys.stdout, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
