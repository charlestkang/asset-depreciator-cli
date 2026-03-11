"""Tests for calculator module depreciation and metrics behavior."""

from datetime import date

import pytest

from asset_depreciator import calculator
from asset_depreciator.models import Asset


class _FakeDate:
    """Simple date shim for deterministic calculator.today() behavior in tests."""

    @staticmethod
    def today():
        return date(2026, 1, 1)


def _make_asset(method: str = "sl", in_service_date: date = date(2024, 1, 1)) -> Asset:
    return Asset(
        id_=1,
        name="Laptop",
        cost=1200.0,
        salvage=200.0,
        life_years=5,
        method=method,
        date_=in_service_date,
    )


def test_depreciation_schedule_selects_sl():
    asset = _make_asset(method="sl")
    schedule = calculator.depreciation_schedule(asset)
    assert len(schedule) == 5
    assert schedule[0][0] == 1


def test_depreciation_schedule_selects_ddb():
    asset = _make_asset(method="ddb")
    schedule = calculator.depreciation_schedule(asset)
    assert len(schedule) == 5
    assert schedule[-1][2] == pytest.approx(asset.cost - asset.salvage)


def test_depreciation_schedule_selects_syd():
    asset = _make_asset(method="syd")
    schedule = calculator.depreciation_schedule(asset)
    assert len(schedule) == 5
    assert schedule[-1][2] == pytest.approx(asset.cost - asset.salvage)


def test_depreciation_schedule_raises_for_unknown_method():
    asset = _make_asset(method="unknown")
    with pytest.raises(ValueError):
        calculator.depreciation_schedule(asset)


def test_sl_schedule_uses_constant_yearly_amount():
    asset = _make_asset(method="sl")
    schedule = calculator.sl(asset)
    yearly = [(row[1]) for row in schedule]

    assert all(amount == pytest.approx(200.0) for amount in yearly)
    assert schedule[-1][2] == pytest.approx(1000.0)


def test_ddb_schedule_never_exceeds_total_depreciation_base():
    asset = _make_asset(method="ddb")
    schedule = calculator.ddb(asset)

    assert schedule[-1][2] == pytest.approx(asset.cost - asset.salvage)
    assert all(row[1] >= 0 for row in schedule)


def test_syd_schedule_front_loads_depreciation():
    asset = _make_asset(method="syd")
    schedule = calculator.syd(asset)

    assert schedule[0][1] > schedule[-1][1]
    assert schedule[-1][2] == pytest.approx(asset.cost - asset.salvage)


def test_total_depreciation_matches_schedule_terminal_value():
    asset = _make_asset(method="sl")
    assert calculator.total_depreciation(asset) == pytest.approx(1000.0)


def test_percent_time_clamps_future_assets_to_zero(monkeypatch):
    monkeypatch.setattr(calculator, "date", _FakeDate)
    future_asset = _make_asset(in_service_date=date(2030, 1, 1))
    assert calculator.percent_time(future_asset) == 0.0


def test_percent_time_caps_at_one_for_fully_elapsed_assets(monkeypatch):
    monkeypatch.setattr(calculator, "date", _FakeDate)
    old_asset = _make_asset(in_service_date=date(2000, 1, 1))
    assert calculator.percent_time(old_asset) == 1.0


def test_build_metrics_for_future_asset_has_no_elapsed_depreciation(monkeypatch):
    monkeypatch.setattr(calculator, "date", _FakeDate)
    asset = _make_asset(in_service_date=date(2030, 1, 1))

    metrics = calculator.build_metrics(asset)

    assert metrics.elapsed_depr == 0.0
    assert metrics.yearly_depr == 0.0
    assert metrics.daily_depr == 0.0
    assert metrics.percent_depr == 0.0


def test_build_metrics_for_fully_depreciated_asset_stops_yearly_and_daily(monkeypatch):
    monkeypatch.setattr(calculator, "date", _FakeDate)
    asset = _make_asset(in_service_date=date(2000, 1, 1))

    metrics = calculator.build_metrics(asset)

    assert metrics.elapsed_depr == pytest.approx(metrics.total_depr)
    assert metrics.percent_time == 1.0
    assert metrics.percent_depr == pytest.approx(1.0)
    assert metrics.yearly_depr == 0.0
    assert metrics.daily_depr == 0.0


def test_legacy_helpers_match_build_metrics(monkeypatch):
    monkeypatch.setattr(calculator, "date", _FakeDate)
    asset = _make_asset(in_service_date=date(2024, 1, 1))
    metrics = calculator.build_metrics(asset)

    assert calculator.elapsed_depreciation(asset) == pytest.approx(metrics.elapsed_depr)
    assert calculator.percent_depreciated(asset) == pytest.approx(metrics.percent_depr)
    assert calculator.yearly_depreciation(asset) == pytest.approx(metrics.yearly_depr)
    assert calculator.daily_depreciation(asset) == pytest.approx(metrics.daily_depr)
