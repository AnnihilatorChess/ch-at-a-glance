from ch_at_a_glance.web.charts import sparkline_svg


def test_empty_values_returns_empty_svg() -> None:
    svg = sparkline_svg([])
    assert svg.startswith("<svg")
    assert "polyline" not in svg


def test_single_value_does_not_crash() -> None:
    svg = sparkline_svg([5.0])
    assert "<polyline" in svg


def test_constant_series_does_not_divide_by_zero() -> None:
    svg = sparkline_svg([2.0, 2.0, 2.0])
    assert "<polyline" in svg


def test_multi_point_series_has_matching_point_count() -> None:
    svg = sparkline_svg([1.0, 2.0, 3.0, 1.5])
    points_attr = svg.split('points="')[1].split('"')[0]
    assert len(points_attr.split(" ")) == 4
