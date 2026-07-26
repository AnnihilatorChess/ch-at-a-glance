"""Tiny server-rendered SVG sparklines.

Deliberately not a JS charting library: this frontend exists to validate
collected data, not to look like the final product. A pure function that
turns a list of floats into an SVG polyline has no client-side dependency,
no CDN, and is trivial to unit test.
"""

from __future__ import annotations


def sparkline_svg(
    values: list[float], *, width: int = 140, height: int = 36, stroke: str = "#3b82f6"
) -> str:
    if not values:
        return f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg"></svg>'

    if len(values) == 1:
        values = [values[0], values[0]]

    low, high = min(values), max(values)
    span = high - low or 1.0
    step = width / (len(values) - 1)

    points = " ".join(
        f"{i * step:.1f},{height - ((v - low) / span) * height:.1f}" for i, v in enumerate(values)
    )

    return (
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'preserveAspectRatio="none">'
        f'<polyline points="{points}" fill="none" stroke="{stroke}" '
        f'stroke-width="2" stroke-linejoin="round" stroke-linecap="round" />'
        f"</svg>"
    )
