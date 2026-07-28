from datetime import date

from ch_at_a_glance.web.charts import sparkline_svg


def test_empty_data_returns_empty_svg() -> None:
    svg = sparkline_svg([])
    assert svg.startswith("<svg")
    assert "polyline" not in svg


def test_single_point_does_not_crash() -> None:
    svg = sparkline_svg([(date(2024, 1, 1), 5.0)])
    assert "<polyline" in svg


def test_constant_series_does_not_divide_by_zero() -> None:
    data = [(date(2022, 1, 1), 2.0), (date(2023, 1, 1), 2.0), (date(2024, 1, 1), 2.0)]
    svg = sparkline_svg(data)
    assert "<polyline" in svg


def test_multi_point_series_has_matching_point_count() -> None:
    data = [
        (date(2021, 1, 1), 1.0),
        (date(2022, 1, 1), 2.0),
        (date(2023, 1, 1), 3.0),
        (date(2024, 1, 1), 1.5),
    ]
    svg = sparkline_svg(data)
    points_attr = svg.split('points="')[1].split('"')[0]
    assert len(points_attr.split(" ")) == 4


def test_recent_horizon_is_highlighted_in_indicator_colour() -> None:
    data = [(date(2020, 1, 1), 1.0), (date(2024, 6, 1), 2.0), (date(2025, 1, 1), 3.0)]
    svg = sparkline_svg(data, colour="red", highlight_days=365)
    assert "#ef4444" in svg


def _highlight_point_count(svg: str) -> int:
    # The highlight overlay is the second <polyline> (the first is the full
    # base line drawn in currentColor).
    polylines = svg.split('<polyline points="')[1:]
    highlight_points_attr = polylines[1].split('"')[0]
    return len(highlight_points_attr.split(" "))


def test_sparse_series_gets_a_minimum_two_point_highlight() -> None:
    # A calendar-accurate cutoff would only catch the very last of 20 yearly
    # points here (a single dot can't draw a line); the floor should widen it
    # to exactly the final interval, not further.
    data = [(date(2005 + i, 1, 1), float(i)) for i in range(20)]
    svg = sparkline_svg(data, colour="green", highlight_days=1)
    assert "#22c55e" in svg
    assert _highlight_point_count(svg) == 2


def test_long_annual_series_does_not_over_widen_the_highlight() -> None:
    # Regression for a real bug: widening by a FRACTION of the whole series
    # (e.g. 12% of 164 points spanning 1861-2024) highlighted a decade-plus
    # for what should be a single year's change. The floor must stay fixed
    # at 2 points regardless of how long the overall series is.
    data = [(date(1861 + i, 1, 1), float(i)) for i in range(164)]
    svg = sparkline_svg(data, colour="green", highlight_days=365)
    assert _highlight_point_count(svg) == 2


def test_year_labels_reflect_first_and_last_observation() -> None:
    data = [(date(2010, 1, 1), 1.0), (date(2024, 1, 1), 2.0)]
    svg = sparkline_svg(data)
    assert ">2010<" in svg
    assert ">2024<" in svg
