#!/usr/bin/env python3
"""Scan Polymarket for trading opportunities using Gamma + CLOB APIs."""

import httpx
import json
import sys
from datetime import datetime, timezone

GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"


def get_trending_markets(limit=20):
    """Fetch trending markets sorted by volume."""
    resp = httpx.get(
        f"{GAMMA_API}/markets",
        params={
            "limit": limit,
            "active": True,
            "closed": False,
            "order": "volume24hr",
            "ascending": False,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def get_market_detail(condition_id):
    """Fetch detailed market info."""
    resp = httpx.get(f"{GAMMA_API}/markets/{condition_id}", timeout=30)
    resp.raise_for_status()
    return resp.json()


def get_orderbook(token_id):
    """Fetch order book from CLOB."""
    resp = httpx.get(
        f"{CLOB_API}/book",
        params={"token_id": token_id},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def get_midpoint(token_id):
    """Get midpoint price for a token."""
    resp = httpx.get(
        f"{CLOB_API}/midpoint",
        params={"token_id": token_id},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    return float(data.get("mid", 0))


def scan_opportunities(limit=20):
    """Scan for markets with potential opportunities."""
    markets = get_trending_markets(limit)
    opportunities = []

    for m in markets:
        try:
            question = m.get("question", "")
            condition_id = m.get("conditionId", "")
            tokens = m.get("clobTokenIds", "")
            
            if isinstance(tokens, str):
                tokens = json.loads(tokens) if tokens else []
            
            if not tokens or len(tokens) < 2:
                continue

            yes_token = tokens[0]
            no_token = tokens[1]

            # Get prices
            yes_price = get_midpoint(yes_token)
            no_price = get_midpoint(no_token)

            if yes_price <= 0 and no_price <= 0:
                continue

            # Calculate spread (deviation from 1.0)
            total = yes_price + no_price
            spread = abs(1.0 - total)

            volume_24h = float(m.get("volume24hr", 0) or 0)
            liquidity = float(m.get("liquidityClob", 0) or 0)

            opportunities.append({
                "question": question,
                "conditionId": condition_id,
                "yesToken": yes_token,
                "noToken": no_token,
                "yesPrice": round(yes_price, 4),
                "noPrice": round(no_price, 4),
                "spread": round(spread, 4),
                "volume24h": round(volume_24h, 2),
                "liquidity": round(liquidity, 2),
                "slug": m.get("slug", ""),
                "endDate": m.get("endDate", ""),
                "scannedAt": datetime.now(timezone.utc).isoformat(),
            })
        except Exception as e:
            print(f"  Skip: {e}", file=sys.stderr)
            continue

    # Sort by volume
    opportunities.sort(key=lambda x: x["volume24h"], reverse=True)
    return opportunities


def find_hedge_pairs(opportunities):
    """Find potential hedge pairs based on price inefficiencies."""
    hedges = []
    
    for opp in opportunities:
        # Markets where YES + NO significantly != 1.0 (spread > 2%)
        if opp["spread"] > 0.02 and opp["volume24h"] > 1000:
            hedges.append({
                "type": "spread_arb",
                "market": opp["question"],
                "conditionId": opp["conditionId"],
                "yesPrice": opp["yesPrice"],
                "noPrice": opp["noPrice"],
                "spread": opp["spread"],
                "potential_profit_pct": round(opp["spread"] * 100, 2),
                "volume24h": opp["volume24h"],
            })

    hedges.sort(key=lambda x: x["spread"], reverse=True)
    return hedges


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "scan"
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20

    if cmd == "scan":
        print(f"Scanning top {limit} markets...")
        opps = scan_opportunities(limit)
        print(json.dumps(opps, indent=2, ensure_ascii=False))
        print(f"\nFound {len(opps)} markets")

    elif cmd == "hedges":
        print(f"Scanning for hedge opportunities...")
        opps = scan_opportunities(limit)
        hedges = find_hedge_pairs(opps)
        print(json.dumps(hedges, indent=2, ensure_ascii=False))
        print(f"\nFound {len(hedges)} potential hedges")

    else:
        print(f"Usage: python scanner.py [scan|hedges] [limit]")
