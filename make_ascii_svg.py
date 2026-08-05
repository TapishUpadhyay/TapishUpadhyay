"""
make_ascii_svg.py — Tapish's ASCII portrait pipeline, step 2.

Downsamples source-prepped.png to a character grid, maps brightness to a
glyph density ramp, and writes a monochrome, self-typing SVG: each row wipes
in left-to-right, staggered top to bottom, then freezes (no looping).

Usage:
    python scripts/make_ascii_svg.py
Output:
    tapish-ascii.svg
"""

from PIL import Image

# bright (sparse) -> dark (dense); leading space clears background to nothing
RAMP = " .`:-=+*cs#%@"

COLS = 100
ROWS = 53
CHAR_W = 7
CHAR_H = 13
FILL = "#c9d1d9"          # single light-gray fill — monochrome, no rainbow
BG = "#0d1117"
STAGGER_PER_ROW = 0.035   # seconds between each row starting to type
ROW_TYPE_DURATION = 0.5   # seconds for a single row's wipe


def image_to_ascii_grid(path: str, cols: int, rows: int):
    img = Image.open(path).convert("L").resize((cols, rows))
    pixels = list(img.getdata())
    grid = []
    for r in range(rows):
        row_chars = []
        for c in range(cols):
            brightness = pixels[r * cols + c]  # 0=black .. 255=white
            idx = int((255 - brightness) / 255 * (len(RAMP) - 1))
            row_chars.append(RAMP[idx])
        grid.append("".join(row_chars))
    return grid


def build_svg(grid, out_path: str):
    width = COLS * CHAR_W + 20
    height = ROWS * CHAR_H + 20

    svg_parts = [
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="Menlo, Consolas, monospace" font-size="{CHAR_H}">',
        f'<rect width="100%" height="100%" fill="{BG}"/>',
        "<style>",
        ".row { fill:" + FILL + "; }",
        "</style>",
    ]

    for r, row_text in enumerate(grid):
        row_text_escaped = (
            row_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        )
        y = 15 + r * CHAR_H
        clip_id = f"clip{r}"
        delay = r * STAGGER_PER_ROW
        row_px_width = COLS * CHAR_W

        # Clip path animates its width from 0 -> full row width (the "wipe")
        svg_parts.append(f'<clipPath id="{clip_id}">')
        svg_parts.append(
            f'<rect x="10" y="{y - CHAR_H}" width="0" height="{CHAR_H + 2}">'
            f'<animate attributeName="width" from="0" to="{row_px_width}" '
            f'begin="{delay:.3f}s" dur="{ROW_TYPE_DURATION}s" '
            f'fill="freeze" calcMode="linear"/>'
            f'</rect>'
        )
        svg_parts.append('</clipPath>')

        svg_parts.append(
            f'<text class="row" x="10" y="{y}" clip-path="url(#{clip_id})" '
            f'xml:space="preserve">{row_text_escaped}</text>'
        )

    svg_parts.append("</svg>")
    with open(out_path, "w") as f:
        f.write("\n".join(svg_parts))
    print(f"[ok] wrote {out_path}")


if __name__ == "__main__":
    grid = image_to_ascii_grid("source-prepped.png", COLS, ROWS)
    build_svg(grid, "tapish-ascii.svg")
