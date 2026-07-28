"""Tiny server-rendered SVG sparklines: a filled area over the full series,
with the most recent horizon highlighted in the indicator's trend colour --
in the spirit of the Times dashboard's charts, not a JS charting library.
A pure function from data to markup has no client-side dependency, no CDN,
and is trivial to unit test.
"""

from __future__ import annotations

from datetime import date, timedelta

_COLOUR_HEX = {"green": "#22c55e", "red": "#ef4444", "grey": "#9ca3af"}
_MIN_HIGHLIGHT_FRACTION = 0.12


def sparkline_svg(
    data: list[tuple[date, float]],
    *,
    colour: str = "grey",
    highlight_days: int = 365,
    width: int = 260,
    height: int = 70,
) -> str:
    if not data:
        return f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg"></svg>'

    values = [v for _, v in data]
    if len(data) == 1:
        data = [data[0], data[0]]
        values = [values[0], values[0]]

    low, high = min(values), max(values)
    span = high - low or 1.0
    chart_height = height - 16  # leave room for year labels
    step = width / (len(data) - 1)

    def y_for(v: float) -> float:
        return chart_height - ((v - low) / span) * chart_height

    points = [(i * step, y_for(v)) for i, v in enumerate(values)]
    line_points = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    area_path = (
        f"M{points[0][0]:.1f},{chart_height} "
        + " ".join(f"L{x:.1f},{y:.1f}" for x, y in points)
        + f" L{points[-1][0]:.1f},{chart_height} Z"
    )

    cutoff = data[-1][0] - timedelta(days=highlight_days)
    calendar_start = next((i for i, (d, _) in enumerate(data) if d >= cutoff), len(data) - 1)
    # A calendar-accurate cutoff can highlight only the last point or two for
    # sparse (annual) series, which is too thin to read. Widen it to at least
    # a fixed fraction of the chart so every card's highlight is legible,
    # without shrinking a highlight that's already wider than that (dense
    # series keep their accurate ~1-year proportion).
    min_start = max(0, len(data) - max(2, round(len(data) * _MIN_HIGHLIGHT_FRACTION)))
    highlight_start = min(calendar_start, min_start)
    hex_colour = _COLOUR_HEX.get(colour, _COLOUR_HEX["grey"])

    highlight_svg = ""
    if highlight_start < len(points) - 1:
        highlight_points = points[highlight_start:]
        highlight_line = " ".join(f"{x:.1f},{y:.1f}" for x, y in highlight_points)
        highlight_area = (
            f"M{highlight_points[0][0]:.1f},{chart_height} "
            + " ".join(f"L{x:.1f},{y:.1f}" for x, y in highlight_points)
            + f" L{highlight_points[-1][0]:.1f},{chart_height} Z"
        )
        highlight_svg = (
            f'<path d="{highlight_area}" fill="{hex_colour}" fill-opacity="0.18" />'
            f'<polyline points="{highlight_line}" fill="none" stroke="{hex_colour}" '
            f'stroke-width="2" stroke-linejoin="round" stroke-linecap="round" />'
        )

    first_year, last_year = data[0][0].year, data[-1][0].year

    return (
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'preserveAspectRatio="none" class="sparkline">'
        f'<path d="{area_path}" fill="currentColor" fill-opacity="0.08" />'
        f'<polyline points="{line_points}" fill="none" stroke="currentColor" '
        f'stroke-opacity="0.35" stroke-width="1.5" stroke-linejoin="round" '
        f'stroke-linecap="round" />'
        f"{highlight_svg}"
        f'<text x="2" y="{height - 3}" font-size="10" fill="currentColor" fill-opacity="0.5">'
        f"{first_year}</text>"
        f'<text x="{width - 2}" y="{height - 3}" font-size="10" fill="currentColor" '
        f'fill-opacity="0.5" text-anchor="end">{last_year}</text>'
        f"</svg>"
    )
