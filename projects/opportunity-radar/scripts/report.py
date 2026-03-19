#!/usr/bin/env python3
"""Weekly report generator for Opportunity Radar."""

import json
import logging
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
REPORTS_DIR = BASE_DIR / "data" / "reports"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("report")

SCORE_THRESHOLD = 7.0


def load_latest_opportunities() -> list[dict]:
    """Load the most recent opportunities file."""
    files = sorted(PROCESSED_DIR.glob("opportunities_*.json"), reverse=True)
    if not files:
        log.warning("No opportunities data found.")
        return []
    with open(files[0], "r", encoding="utf-8") as f:
        return json.load(f)


def generate_report(opportunities: list[dict]) -> str:
    today = date.today().strftime("%Y-%m-%d")
    lines = [
        f"# 🔭 商機雷達週報 — {today}",
        "",
    ]

    hot = [o for o in opportunities if o.get("is_hot", False)]
    top5 = opportunities[:5]

    lines.append(f"## 📊 總覽")
    lines.append(f"- 分析痛點數：{len(opportunities)}")
    lines.append(f"- 熱門商機（>{SCORE_THRESHOLD}）：{len(hot)}")
    lines.append("")

    # Summary table
    lines.append("## 📋 Top 5 商機排行")
    lines.append("")
    lines.append("| # | 痛點關鍵字 | 總分 | 出現次數 | 🔥 |")
    lines.append("|---|----------|------|---------|-----|")
    for i, opp in enumerate(top5, 1):
        hot_icon = "🔥" if opp.get("is_hot") else ""
        lines.append(f"| {i} | {opp['keyword']} | {opp['total_score']} | {opp['post_count']} | {hot_icon} |")
    lines.append("")

    # Detailed breakdown
    lines.append("## 🔍 詳細分析")
    lines.append("")
    for i, opp in enumerate(top5, 1):
        scores = opp.get("scores", {})
        lines.append(f"### {i}. {opp['keyword']}")
        lines.append(f"**總分：{opp['total_score']}** {'🔥 HOT OPPORTUNITY' if opp.get('is_hot') else ''}")
        lines.append("")
        lines.append("| 維度 | 分數 |")
        lines.append("|------|------|")
        labels = {
            "pain_level": "痛點強度",
            "market_size": "市場規模",
            "willingness_to_pay": "付費意願",
            "competition": "競爭程度（高=少競爭）",
            "build_complexity": "開發難度（高=容易）",
            "distribution": "推廣潛力",
        }
        for key, label in labels.items():
            lines.append(f"| {label} | {scores.get(key, 'N/A')} |")
        lines.append("")

        # Evidence
        evidence = opp.get("evidence", [])
        if evidence:
            lines.append("**佐證引述：**")
            for ev in evidence[:3]:
                source = ev.get("source", "unknown")
                quote = ev.get("quote", "")[:150]
                url = ev.get("url", "")
                lines.append(f'- [{source}] "{quote}"')
                if url:
                    lines.append(f"  {url}")
            lines.append("")

        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def main():
    opportunities = load_latest_opportunities()
    if not opportunities:
        print("No data available for report.")
        return

    report = generate_report(opportunities)

    today = date.today().strftime("%Y%m%d")
    report_path = REPORTS_DIR / f"weekly_{today}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    log.info("Report saved to %s", report_path)

    # Print to stdout for Telegram delivery
    print(report)


if __name__ == "__main__":
    main()
