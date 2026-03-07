"""
Tests for the project module
"""

import pytest

import project
from models import Asset


def test_normalize_method():
    assert project.normalize_method("straight line") == "sl"
    assert project.normalize_method("Monty Python") == None


def test_find_asset_by_id():
    test_assets = [
        Asset(42, "test", 50, 42, 1, "sl"),
        Asset(43, "test2", 50, 42, 1, "sl"),
    ]
    assert project.find_asset_by_id_(43, test_assets) == test_assets[1]


def test_build_asset():
    test_asset = Asset(43, "test2", 50, 42, 1, "sl")
    assert project.build_asset(43, "test2", 50, 42, 1, "sl") == test_asset
