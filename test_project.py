"""
Tests for the project module
"""

import pytest
from datetime import date

import project
from models import Asset


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
