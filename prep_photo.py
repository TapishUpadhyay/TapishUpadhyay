"""
prep_photo.py — Tapish's ASCII portrait pipeline, step 1.

Takes a raw photo, removes the background, boosts local contrast (CLAHE),
and composites onto pure white so the background maps to blank space in
the final ASCII ramp.

Usage:
    python scripts/prep_photo.py source-photo.jpg
Output:
    source-prepped.png  (grayscale, background-removed, contrast-boosted)
"""

import sys
import numpy as np
import cv2
from PIL import Image
from rembg import remove


def prep_photo(input_path: str, output_path: str = "source-prepped.png"):
    # 1. Remove background -> RGBA with transparent bg
    with open(input_path, "rb") as f:
        input_bytes = f.read()
    result_bytes = remove(input_bytes)

    from io import BytesIO
    subject = Image.open(BytesIO(result_bytes)).convert("RGBA")

    # 2. Composite onto pure white background
    white_bg = Image.new("RGBA", subject.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(white_bg, subject).convert("RGB")

    # 3. Boost local contrast with CLAHE (gives flat lighting real depth)
    img_np = np.array(composited)
    gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)

    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # 4. Save grayscale, contrast-enhanced, white-background result
    Image.fromarray(enhanced).save(output_path)
    print(f"[ok] wrote {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/prep_photo.py <photo.jpg>")
        sys.exit(1)
    prep_photo(sys.argv[1])
