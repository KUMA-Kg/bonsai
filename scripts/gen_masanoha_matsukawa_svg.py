#!/usr/bin/env python3
"""Generate seamless asanoha + matsukawabishi-style (jagged radial) SVG tile.

Output: images/kinjyakka/masanoha-matsukawa-tile.svg
Used as site watermark background (ultra-fine #eeeeee on transparent; body supplies paper tone).
"""
from __future__ import annotations

import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "images" / "kinjyakka" / "masanoha-matsukawa-tile.svg"

# Flat-top hex tile that stacks with row offset (classic 56 x 97 cell)
CX, CY = 28.0, 32.333333333333336
VERTS = [
    (28.0, 0.0),
    (56.0, 16.166666666666668),
    (56.0, 48.5),
    (28.0, 64.66666666666667),
    (0.0, 48.5),
    (0.0, 16.166666666666668),
]


def jagged_polyline(cx: float, cy: float, ex: float, ey: float, steps: int, amp: float) -> str:
    """Alternating perpendicular offset; endpoints exact (tile-safe)."""
    dx, dy = ex - cx, ey - cy
    length = math.hypot(dx, dy)
    if length < 1e-9:
        return ""
    ux, uy = dx / length, dy / length
    px, py = -uy, ux
    parts: list[str] = []
    for i in range(steps + 1):
        t = i / steps
        x = cx + t * dx
        y = cy + t * dy
        if 0 < i < steps:
            sign = -1 if i % 2 else 1
            x += sign * amp * px
            y += sign * amp * py
        parts.append((x, y))
    s = f"M{parts[0][0]:.4f} {parts[0][1]:.4f}"
    for x, y in parts[1:]:
        s += f"L{x:.4f} {y:.4f}"
    return s


def path_d(coords: list[tuple[float, float]], close: bool = False) -> str:
    x0, y0 = coords[0]
    s = f"M{x0:.4f} {y0:.4f}"
    for x, y in coords[1:]:
        s += f"L{x:.4f} {y:.4f}"
    if close:
        s += "Z"
    return s


def main() -> None:
    stroke = "#eeeeee"
    sw = "0.5"
    elems: list[str] = []

    elems.append(
        f'<path d="{path_d(list(VERTS), close=True)}" stroke="{stroke}" stroke-width="{sw}" '
        'stroke-linejoin="miter" stroke-linecap="butt"/>'
    )
    bp = [(28.0, 64.667), (56.0, 80.834), (56.0, 97.0), (0.0, 97.0), (0.0, 80.834)]
    elems.append(
        f'<path d="{path_d(bp, close=True)}" stroke="{stroke}" stroke-width="{sw}"/>'
    )

    amp = 0.48
    steps = 11
    for vx, vy in VERTS:
        d = jagged_polyline(CX, CY, vx, vy, steps, amp)
        elems.append(
            f'<path d="{d}" stroke="{stroke}" stroke-width="{sw}" '
            'stroke-linejoin="round" stroke-linecap="round"/>'
        )

    elems.append(
        f'<path d="M28 0L56 48.5L0 48.5Z" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="miter"/>'
    )
    elems.append(
        f'<path d="M56 16.167L28 64.667L0 16.167Z" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="miter"/>'
    )

    d1 = jagged_polyline(28.0, 64.667, 56.0, 80.834, 5, amp * 0.85)
    d2 = jagged_polyline(28.0, 64.667, 0.0, 80.834, 5, amp * 0.85)
    elems.extend(
        f'<path d="{d}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"/>'
        for d in (d1, d2)
    )
    elems.append(f'<path d="M28 87.25L28 97" stroke="{stroke}" stroke-width="{sw}"/>')
    elems.append(f'<path d="M14 88.917H42" stroke="{stroke}" stroke-width="{sw}"/>')

    svg = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<svg xmlns="http://www.w3.org/2000/svg" width="56" height="97" '
        'viewBox="0 0 56 97">\n'
        '  <!-- Asanoha + jagged matsukawa-style radials, seamless repeat -->\n'
        '  <g fill="none" vector-effect="non-scaling-stroke">\n    '
        + "\n    ".join(elems)
        + "\n  </g>\n</svg>\n"
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
