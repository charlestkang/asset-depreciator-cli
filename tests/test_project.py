"""
Tests for the project module
"""

import pytest
from datetime import date

from asset_depreciator import project
from asset_depreciator.models import Asset


def test_normalize_method():
    assert project.normalize_method("straight line") == "sl"
    with pytest.raises(ValueError):
        project.normalize_method("Monty Python")


def test_find_asset_by_id():
    test_assets = [
        Asset(42, "test", 50, 42, 1, "sl", date(1999, 1, 1)),
        Asset(43, "test2", 50, 42, 1, "sl", date(1999, 1, 1)),
    ]
    assert project.find_asset_by_id_(43, test_assets) == test_assets[1]


def test_build_asset():
    test_asset = Asset(43, "test2", 50, 42, 1, "sl", date(1999, 1, 1))
    assert project.build_asset(43, "test2", 50, 42, 1, "sl", date(1999, 1, 1)) == test_asset


def test_get_intention_empty_returns_exit(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "")
    assert project.get_intention() == "exit"


def test_get_intention_valid_option(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "view")
    assert project.get_intention() == "view"


def test_get_float_parses_currency(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "$1,250.50")
    assert project.get_float("Amount: ") == 1250.50


def test_get_float_optional_blank_returns_default(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "")
    assert project.get_float_optional("Optional: ", default=99.0) == 99.0


def test_get_int_requires_positive_whole_number(monkeypatch):
    answers = iter(["1.5", "0", "3"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    assert project.get_int("Years: ") == 3


def test_get_method_normalizes_alias(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "straight line")
    assert project.get_method("Method: ") == "sl"


def test_get_date_parses_ymd(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "2024-12-31")
    assert project.get_date("Date: ") == date(2024, 12, 31)


def test_get_str_rejects_only_punctuation(monkeypatch):
    answers = iter(["!!!", "  laptop  "])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    assert project.get_str("Name: ") == "laptop"


def test_calculate_view_totals_aggregates_rates():
    assets = [
        Asset(1, "A", 1000, 100, 5, "sl", date(2024, 1, 1)),
        Asset(2, "B", 600, 0, 3, "sl", date(2025, 1, 1)),
    ]

    daily_total, monthly_total, yearly_total = project.calculate_view_totals(assets)

    assert daily_total >= 0
    assert monthly_total >= 0
    assert yearly_total >= 0
    assert monthly_total == pytest.approx(yearly_total / 12)


def test_inspect_handles_missing_asset_from_storage(monkeypatch, capsys):
    asset = Asset(1, "A", 1000, 100, 5, "sl", date(2024, 1, 1))
    monkeypatch.setattr(project.storage, "get_asset", lambda _: (_ for _ in ()).throw(project.storage.AssetNotFoundError("missing")))

    project.inspect(1, [asset])
    out = capsys.readouterr().out

    assert "Asset not found" in out


def test_edit_asset_handles_missing_asset_from_storage(monkeypatch, capsys):
    answers = iter(["name", "Updated"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    monkeypatch.setattr(project.storage, "get_asset", lambda _: (_ for _ in ()).throw(project.storage.AssetNotFoundError("missing")))

    project.edit_asset(1)
    out = capsys.readouterr().out

    assert "Asset not found" in out
