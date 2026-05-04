#!/usr/bin/env python3
"""Build production WebP assets for kinjyakka-lp.html.

Sources live in /images/kinjyakka/. Each Job declares which file to read
(LINE_ALBUM index or explicit filename) and how to crop/resize.

Usage:
  PYTHONPATH=__pypackages__ python3 scripts/build_kinjyakka_assets.py
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "images" / "kinjyakka"
OUT_DIR = SRC_DIR


def line_src(n: int) -> Path:
    return SRC_DIR / f"LINE_ALBUM_金雀花_260430_{n}.jpg"


@dataclass(frozen=True)
class Job:
    out_name: str
    aspect: tuple[int, int] | None  # (w, h) for crop; None = no crop
    target_w: int
    quality: int = 80
    crop_y_bias: float = 0.5  # 0=top, 1=bottom
    crop_x_bias: float = 0.5
    method: int = 6  # WebP encoder effort (0..6)
    src_n: int | None = None
    src_file: str | None = None

    def src_path(self) -> Path:
        if self.src_file is not None:
            return SRC_DIR / self.src_file
        if self.src_n is None:
            raise ValueError(f"{self.out_name}: needs src_n or src_file")
        return line_src(self.src_n)

    def origin(self) -> str:
        return self.src_file if self.src_file else f"#{self.src_n}"


JOBS: list[Job] = [
    # hero: 元画像 1108x1477 (3:4)。スマホ縦ビューポートで鉢〜枝先が収まる構図。
    # 表示幅は実機 375px(2倍密度=750px) なので 960px に縮小して LCP 軽量化。
    Job(src_n=16, out_name="hero.webp", aspect=(3, 4), target_w=960,
        quality=85),
    # main-visual: 金閣寺＋金雀花の合成画像（ユーザ指定）
    Job(src_file="source-kinkaku-bonsai.png",
        out_name="main-visual.webp", aspect=(3, 4), target_w=800,
        quality=85),
    # story-1, story-2, story-4: 来歴の各エピソード（story-3 は LP では未使用）
    # 1:1 でフレーミングを保ちつつ、表示は 375px×2倍密度=750px を見据え 800px で生成。
    Job(src_n=10, out_name="story-1.webp", aspect=(1, 1), target_w=800,
        quality=85, crop_y_bias=0.55),
    Job(src_file="Gemini_Generated_Image_n4c4kqn4c4kqn4c4.png",
        out_name="story-2.webp", aspect=(1, 1), target_w=800,
        quality=85, crop_y_bias=0.50),
    Job(src_n=7,  out_name="story-4.webp", aspect=(1, 1), target_w=800,
        quality=85, crop_y_bias=0.50),
    Job(src_n=17, out_name="sub-care.webp", aspect=(16, 9), target_w=960,
        quality=80, crop_y_bias=0.55, crop_x_bias=0.62),
    # night: 夜の京都・八坂の塔×金雀花。世界観カット（メインビジュアル隣）
    Job(src_n=13, out_name="night.webp", aspect=(3, 4), target_w=720,
        quality=82, crop_y_bias=0.45),
]


def crop_to_aspect(img: Image.Image, aspect: tuple[int, int],
                   x_bias: float, y_bias: float) -> Image.Image:
    aw, ah = aspect
    w, h = img.size
    target = aw / ah
    src_ratio = w / h
    if abs(src_ratio - target) < 1e-3:
        return img
    if src_ratio > target:
        new_w = int(round(h * target))
        x0 = int(round((w - new_w) * x_bias))
        return img.crop((x0, 0, x0 + new_w, h))
    new_h = int(round(w / target))
    y0 = int(round((h - new_h) * y_bias))
    return img.crop((0, y0, w, y0 + new_h))


def run_job(job: Job) -> tuple[Path, int]:
    src_path = job.src_path()
    if not src_path.exists():
        raise FileNotFoundError(src_path)
    with Image.open(src_path) as raw:
        img = ImageOps.exif_transpose(raw).convert("RGB")
    if job.aspect is not None:
        img = crop_to_aspect(img, job.aspect, job.crop_x_bias, job.crop_y_bias)
    w, h = img.size
    if w > job.target_w:
        new_h = int(round(h * (job.target_w / w)))
        img = img.resize((job.target_w, new_h), Image.LANCZOS)
    out_path = OUT_DIR / job.out_name
    img.save(out_path, "WEBP", quality=job.quality, method=job.method)
    return out_path, out_path.stat().st_size


def main() -> None:
    print("source dir:", SRC_DIR)
    total = 0
    for job in JOBS:
        out, size = run_job(job)
        total += size
        print(f"  {out.name:>20}  {size:>8} bytes  (from {job.origin()})")
    print(f"total: {total} bytes ({total/1024:.1f} KB)")


if __name__ == "__main__":
    main()
