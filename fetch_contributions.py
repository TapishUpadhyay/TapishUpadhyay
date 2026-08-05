"""
fetch_contributions.py — Tapish's live heatmap pipeline, step 1.

Fetches the public contribution-calendar HTML fragment GitHub serves for any
username (no GraphQL API, no personal access token needed), parses the day
cells, and writes data/contributions.json with raw days + derived stats
(current streak, longest streak, best day, monthly totals, total count).

Usage:
    python scripts/fetch_contributions.py
Output:
    data/contributions.json
"""

import json
import re
from datetime import datetime, timedelta, timezone

import requests
from bs4 import BeautifulSoup

USERNAME = "TapishUpadhyay"
URL = f"https://github.com/users/{USERNAME}/contributions"


def fetch_html() -> str:
    headers = {"User-Agent": "Mozilla/5.0 (profile-readme-bot)"}
    resp = requests.get(URL, headers=headers, timeout=20)
    resp.raise_for_status()
    return resp.text


def parse_days(html: str):
    soup = BeautifulSoup(html, "html.parser")
    days = []

    # GitHub renders each day as a <td class="ContributionCalendar-day">
    # with data-date and data-level, but the actual COUNT lives in a
    # sibling <tool-tip for="cell-id">N contributions on <date>.</tool-tip>
    tooltip_by_id = {}
    for tip in soup.select("tool-tip"):
        target_id = tip.get("for")
        if target_id:
            tooltip_by_id[target_id] = tip.get_text(strip=True)

    cells = soup.select("td.ContributionCalendar-day")
    for cell in cells:
        date = cell.get("data-date")
        level = cell.get("data-level")
        if date is None:
            continue

        cell_id = cell.get("id")
        tip_text = tooltip_by_id.get(cell_id, "")

        count = 0
        if tip_text:
            if tip_text.lower().startswith("no contributions"):
                count = 0
            else:
                match = re.match(r"([\d,]+)\s+contribution", tip_text)
                if match:
                    count = int(match.group(1).replace(",", ""))

        try:
            level = int(level) if level is not None else 0
        except ValueError:
            level = 0

        days.append({"date": date, "count": count, "level": level})

    days.sort(key=lambda d: d["date"])
    return days


def compute_stats(days):
    total = sum(d["count"] for d in days)

    # streaks
    current_streak = 0
    longest_streak = 0
    running = 0
    today = datetime.now(timezone.utc).date()

    for d in days:
        if d["count"] > 0:
            running += 1
            longest_streak = max(longest_streak, running)
        else:
            running = 0

    # current streak: count backwards from most recent day with data
    for d in reversed(days):
        d_date = datetime.strptime(d["date"], "%Y-%m-%d").date()
        if d_date > today:
            continue
        if d["count"] > 0:
            current_streak += 1
        else:
            break

    best_day = max(days, key=lambda d: d["count"], default=None)

    monthly = {}
    for d in days:
        month_key = d["date"][:7]  # YYYY-MM
        monthly[month_key] = monthly.get(month_key, 0) + d["count"]

    return {
        "total_last_year": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "monthly_totals": monthly,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def main():
    html = fetch_html()
    days = parse_days(html)
    stats = compute_stats(days)

    output = {"username": USERNAME, "days": days, "stats": stats}

    with open("data/contributions.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"[ok] wrote data/contributions.json — {stats['total_last_year']} contributions parsed")


if __name__ == "__main__":
    main()
