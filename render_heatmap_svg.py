"""
render_heatmap_svg.py — Tapish's live heatmap pipeline, step 2.

Reads data/contributions.json and draws the classic 53-week x 7-day
calendar as rounded, colored boxes using a GitHub-green ramp. Boxes reveal
once with a diagonal, line-after-line slide-down (CSS keyframes that play
on load, then freeze), plus a Less->More legend and a live stats footer.

Usage:
    python scripts/render_heatmap_svg.py
Output:
    contrib-heatmap.svg
"""

import json
from datetime import datetime, timedelta

# none -> brightest (level 5 is a neon top end, matches original guide)
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

BG = "#0d1117"
TEXT = "#8b949e"
CELL = 11
GAP = 3
LEFT_PAD = 30
TOP_PAD = 40
BOTTOM_PAD = 40
WEEKS = 53
DAYS = 7


def load_data(path="data/contributions.json"):
    with open(path) as f:
        return json.load(f)


def build_week_grid(days):
    """Bucket the flat day list into 53 weeks x 7 days, aligned to Sunday."""
    by_date = {d["date"]: d for d in days}
    if not days:
        return []

    last_date = datetime.strptime(days[-1]["date"], "%Y-%m-%d").date()
    # walk back to the most recent Saturday to close the grid,
    # then back WEEKS*7 days to find the start (a Sunday)
    end = last_date
    while end.weekday() != 5:  # 5 = Saturday
        end += timedelta(days=1)
    start = end - timedelta(days=WEEKS * DAYS - 1)

    grid = []
    cursor = start
    for w in range(WEEKS):
        week = []
        for d in range(DAYS):
            date_str = cursor.strftime("%Y-%m-%d")
            entry = by_date.get(date_str, {"date": date_str, "count": 0, "level": 0})
            week.append(entry)
            cursor += timedelta(days=1)
        grid.append(week)
    return grid


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_svg(data, out_path="contrib-heatmap.svg"):
    grid = build_week_grid(data["days"])
    stats = data["stats"]

    width = LEFT_PAD + WEEKS * (CELL + GAP) + 20
    height = TOP_PAD + DAYS * (CELL + GAP) + BOTTOM_PAD

    parts = [
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="Menlo, Consolas, monospace" font-size="11">',
        f'<rect width="100%" height="100%" fill="{BG}"/>',
        "<style>",
        ".cell { animation-fill-mode: forwards; opacity: 0; }",
    ]

    # Diagonal reveal: keyframes per (week + day) offset, staggered
    max_delay_steps = WEEKS + DAYS
    for step in range(max_delay_steps):
        delay = step * 0.012
        parts.append(
            f".d{step} {{ animation: reveal{step} 0.25s ease-out {delay:.3f}s forwards; }}"
            f"@keyframes reveal{step} {{ from {{ opacity:0; transform: translateY(-6px); }} "
            f"to {{ opacity:1; transform: translateY(0); }} }}"
        )
    parts.append("</style>")

    # cells
    for w, week in enumerate(grid):
        for d, entry in enumerate(week):
            x = LEFT_PAD + w * (CELL + GAP)
            y = TOP_PAD + d * (CELL + GAP)
            level = max(0, min(entry.get("level", 0), len(PALETTE) - 1))
            color = PALETTE[level]
            step = w + d
            title = f"{entry['date']}: {entry['count']} contributions"
            parts.append(
                f'<rect class="cell d{step}" x="{x}" y="{y}" width="{CELL}" '
                f'height="{CELL}" rx="2" fill="{color}"><title>{esc(title)}</title></rect>'
            )

    # legend: Less -> More
    legend_x = LEFT_PAD
    legend_y = height - 20
    parts.append(f'<text x="{legend_x}" y="{legend_y+9}" fill="{TEXT}">Less</text>')
    lx = legend_x + 35
    for color in PALETTE:
        parts.append(f'<rect x="{lx}" y="{legend_y}" width="{CELL}" height="{CELL}" rx="2" fill="{color}"/>')
        lx += CELL + GAP
    parts.append(f'<text x="{lx+4}" y="{legend_y+9}" fill="{TEXT}">More</text>')

    # stats footer (right-aligned)
    stat_text = (
        f"{stats['total_last_year']} contributions in the last year . "
        f"streak {stats['current_streak']}d (best {stats['longest_streak']}d)"
    )
    parts.append(
        f'<text x="{width - 20}" y="{legend_y+9}" text-anchor="end" fill="{TEXT}">'
        f'{esc(stat_text)}</text>'
    )

    parts.append(f'<text x="{LEFT_PAD}" y="20" fill="{TEXT}">tapish@github ~ $ ./contributions.sh</text>')

    parts.append("</svg>")
    with open(out_path, "w") as f:
        f.write("\n".join(parts))
    print(f"[ok] wrote {out_path}")


if __name__ == "__main__":
    data = load_data()
    build_svg(data)
