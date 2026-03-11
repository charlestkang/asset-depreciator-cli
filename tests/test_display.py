"""Tests for display module rendering paths."""

from datetime import date

from asset_depreciator import display
from asset_depreciator.models import Asset, Metrics


def test_display_assets_empty(capsys) -> None:
    display.display_assets([])
    out = capsys.readouterr().out
    assert "No assets to display" in out


def test_inspect_renders_sections(capsys) -> None:
    asset = Asset(1, "Laptop", 1200.0, 200.0, 5, "sl", date(2024, 1, 1))
    schedule = [(1, 200.0, 200.0), (2, 200.0, 400.0)]
    metrics = Metrics(
        asset=asset,
        schedule=schedule,
        total_depr=1000.0,
        percent_time=0.25,
        percent_depr=0.4,
        yearly_depr=200.0,
        daily_depr=200.0 / 365.25,
        elapsed_depr=400.0,
    )

    display.inspect(metrics)
    out = capsys.readouterr().out

    assert "Current Depreciation Status" in out
    assert "Annual Depreciation Schedule" in out
    assert "Laptop" in out
    assert "YEAR" in out


def test_display_view_totals_renders_all_periods(capsys) -> None:
    display.display_view_totals(12.345, 370.35, 4444.2)
    out = capsys.readouterr().out

    assert "Portfolio depreciation totals" in out
    assert "Per day:" in out
    assert "Per month:" in out
    assert "Per year:" in out
