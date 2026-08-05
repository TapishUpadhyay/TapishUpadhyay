"""
make_info_card.py — Tapish's ASCII portrait pipeline, step 3.

Hand-authors a neofetch-style SVG panel: title bar + colored key/value rows
that fade + slide in on a short stagger, then freeze (no looping).

Set STATIC=1 to emit a frozen (non-animated) frame — useful for local
Quick Look previews where SMIL doesn't render.

Usage:
    python scripts/make_info_card.py
Output:
    info-card.svg
"""

import os

STATIC = os.environ.get("STATIC") == "1"

BG = "#0d1117"
BORDER = "#30363d"
TITLE_BAR = "#161b22"
LABEL_COLOR = "#7ee787"     # green, like a neofetch key color
VALUE_COLOR = "#c9d1d9"
ACCENT = "#58a6ff"

WIDTH = 490
HEIGHT = 300
PAD_X = 24
LINE_H = 26
STAGGER = 0.12
FADE_DUR = 0.35

# --- content, personalized for Tapish ---
TITLE = "tapish@github"

ROWS = [
    ("Now", "2nd-yr CSE @ VIT Bhopal | Building TAPISH OS"),
    ("Prev", "Notion workspace architect | Portfolio dev"),
    ("Stack", "Next.js . TypeScript . Python . Tailwind . FL Studio"),
    ("", ""),  # spacer
    ("Highlights", ""),
    ("", "Music producer (FL Studio) . YouTube @Rugnut1"),
    ("", "Chess -- TapishU on chess.com / Lichess"),
    ("", "Food donation initiative with PROJECT GOOD"),
    ("", "Football + running"),
]


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_svg(out_path: str):
    parts = [
        f'<svg viewBox="0 0 {WIDTH} {HEIGHT}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="Menlo, Consolas, monospace" font-size="14">',
        f'<rect x="0.5" y="0.5" width="{WIDTH-1}" height="{HEIGHT-1}" rx="8" '
        f'fill="{BG}" stroke="{BORDER}"/>',
        # title bar
        f'<rect x="0.5" y="0.5" width="{WIDTH-1}" height="34" rx="8" fill="{TITLE_BAR}"/>',
        f'<rect x="0.5" y="26" width="{WIDTH-1}" height="8.5" fill="{TITLE_BAR}"/>',
        f'<circle cx="20" cy="17" r="5" fill="#ff5f56"/>',
        f'<circle cx="38" cy="17" r="5" fill="#ffbd2e"/>',
        f'<circle cx="56" cy="17" r="5" fill="#27c93f"/>',
        f'<text x="{WIDTH/2}" y="22" text-anchor="middle" fill="{VALUE_COLOR}" '
        f'font-size="12">{esc(TITLE)}</text>',
    ]

    y = 66
    row_index = 0
    for label, value in ROWS:
        if label == "" and value == "":
            y += LINE_H // 2
            continue

        delay = row_index * STAGGER
        anim = ""
        opacity_start = "1" if STATIC else "0"
        transform_attr = ""

        if not STATIC:
            anim = (
                f'<animate attributeName="opacity" from="0" to="1" '
                f'begin="{delay:.3f}s" dur="{FADE_DUR}s" fill="freeze"/>'
                f'<animateTransform attributeName="transform" type="translate" '
                f'from="-10 0" to="0 0" begin="{delay:.3f}s" dur="{FADE_DUR}s" '
                f'fill="freeze"/>'
            )

        if label == "Highlights":
            parts.append(
                f'<g opacity="{opacity_start}">'
                f'<text x="{PAD_X}" y="{y}" fill="{ACCENT}" font-weight="bold">'
                f'{esc(label)}</text>{anim}</g>'
            )
        elif label:
            parts.append(
                f'<g opacity="{opacity_start}">'
                f'<text x="{PAD_X}" y="{y}" fill="{LABEL_COLOR}">{esc(label)}:</text>'
                f'<text x="{PAD_X + 90}" y="{y}" fill="{VALUE_COLOR}">{esc(value)}</text>'
                f'{anim}</g>'
            )
        else:
            parts.append(
                f'<g opacity="{opacity_start}">'
                f'<text x="{PAD_X + 12}" y="{y}" fill="{VALUE_COLOR}">- {esc(value)}</text>'
                f'{anim}</g>'
            )

        y += LINE_H
        row_index += 1

    parts.append("</svg>")
    with open(out_path, "w") as f:
        f.write("\n".join(parts))
    print(f"[ok] wrote {out_path}{' (static)' if STATIC else ''}")


if __name__ == "__main__":
    build_svg("info-card.svg")
