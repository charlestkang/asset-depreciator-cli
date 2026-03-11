"""Tests for domain models."""

from datetime import date

import pytest

from asset_depreciator.models import Asset, Metrics


def test_asset_creation_valid() -> None:
    asset = Asset(1, "Laptop", 1200.0, 200.0, 5, "sl", date(2024, 1, 1))
    assert asset.id_ == 1
    assert asset.name == "Laptop"
    assert asset.cost == 1200.0


def test_asset_validation_cost_negative() -> None:
    with pytest.raises(ValueError, match="Cost cannot be negative"):
        Asset(1, "Laptop", -1.0, 0.0, 5, "sl", date(2024, 1, 1))


def test_asset_validation_life_years() -> None:
    with pytest.raises(ValueError, match="Life years must be greater than 0"):
        Asset(1, "Laptop", 1000.0, 0.0, 0, "sl", date(2024, 1, 1))


def test_asset_validation_salvage() -> None:
    with pytest.raises(ValueError, match="Salvage must be less than cost"):
        Asset(1, "Laptop", 1000.0, 1000.0, 5, "sl", date(2024, 1, 1))


def test_asset_to_dict_round_trip() -> None:
    asset = Asset(7, "Server", 5000.0, 500.0, 6, "ddb", date(2020, 5, 20))
    data = asset.to_dict()
    rebuilt = Asset(**data)
    assert rebuilt == asset


def test_metrics_container_fields() -> None:
    asset = Asset(1, "Printer", 900.0, 100.0, 4, "sl", date(2022, 6, 1))
    metrics = Metrics(
        asset=asset,
        schedule=[(1, 200.0, 200.0)],
        total_depr=800.0,
        percent_time=0.25,
        percent_depr=0.25,
        yearly_depr=200.0,
        daily_depr=200.0 / 365.25,
        elapsed_depr=200.0,
    )
    assert metrics.asset == asset
    assert metrics.total_depr == 800.0
    assert metrics.schedule[0][0] == 1
