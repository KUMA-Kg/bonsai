#!/usr/bin/env python3
"""Build asanoha-bg.webp from a photograph (wood marquetry / yosegi) for LP background.

Default source (CC BY-SA 4.0): Wikimedia Commons yosegi puzzle box photo
(see ATTRIBUTION in images/kinjyakka/).

Override with your own image (e.g. the reference photo you shot):
  PYTHONPATH=__pypackages__ python3 scripts/build_asanoha_texture.py \\
    --source images/kinjyakka/masanoha-source.jpg

Processing: grayscale → colorize to jade palette → soft blur → blend onto kiji → WebP.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "images" / "kinjyakka" / "asanoha-bg.webp"
KIJI = (250, 250, 247)  # --kiji


def process(src: Path, out: Path) -> None:
    im = Image.open(src).convert("RGB")
    max_w = 900
    if im.width > max_w:
        ratio = max_w / im.width
        im = im.resize(
            (max_w, int(im.height * ratio)),
            Image.Resampling.LANCZOS,
        )
    gray = ImageOps.grayscale(im)
    # 木目写真 → 翡翠トーン（コントラストは維持しつめ）
    mapped = ImageOps.colorize(gray, black="#18392e", white="#fafaf7")
    mapped = mapped.filter(ImageFilter.GaussianBlur(radius=0.45))
    kiji_layer = Image.new("RGB", mapped.size, KIJI)
    # Texture strength (lower = calmer)
    # Texture strength vs --kiji (higher = more photo grain visible)
    blended = Image.blend(kiji_layer, mapped, 0.46)
    out.parent.mkdir(parents=True, exist_ok=True)
    blended.save(
        out,
        "WEBP",
        quality=82,
        method=6,
    )
    print(f"Wrote {out} ({out.stat().st_size // 1024} KiB)")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--source",
        type=Path,
        help="Input JPEG/PNG (defaults to downloaded Commons file if present)",
    )
    args = p.parse_args()
    default_commons = ROOT / "images" / "kinjyakka" / "_yosegi_source_download.jpg"
    src = args.source or default_commons
    if not src.is_file():
        raise SystemExit(
            f"Missing source image: {src}\n"
            "Place a yosegi/marquetry photo there, or run curl to fetch the default "
            "(see README in images/kinjyakka/)."
        )
    process(src, OUT)


if __name__ == "__main__":
    main()
