"""Tests for CSV-backed storage operations."""

from datetime import date
from pathlib import Path

import pytest

from asset_depreciator import storage
from asset_depreciator.models import Asset


@pytest.fixture
def isolated_storage(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    file_path = tmp_path / "assets.csv"
    monkeypatch.setattr(storage, "FILE", file_path)
    return file_path


def make_asset(asset_id: int = 1, name: str = "Item") -> Asset:
    return Asset(asset_id, name, 1200.0, 200.0, 5, "sl", date(2024, 1, 1))


def test_store_and_get_asset(isolated_storage: Path) -> None:
    asset = make_asset(1)
    storage.store_asset(asset)
    fetched = storage.get_asset(1)
    assert fetched == asset


def test_get_asset_missing_file_raises(isolated_storage: Path) -> None:
    with pytest.raises(storage.AssetNotFoundError, match="No assets found"):
        storage.get_asset(1)


def test_get_asset_missing_id_raises(isolated_storage: Path) -> None:
    storage.store_asset(make_asset(1))
    with pytest.raises(storage.AssetNotFoundError, match="No asset found with id 2"):
        storage.get_asset(2)


def test_get_all_assets_empty_when_missing_file(isolated_storage: Path) -> None:
    assert storage.get_all_assets() == []


def test_get_next_id(isolated_storage: Path) -> None:
    assert storage.get_next_id() == 1
    storage.store_asset(make_asset(3))
    storage.store_asset(make_asset(5))
    assert storage.get_next_id() == 6


def test_get_id_s(isolated_storage: Path) -> None:
    storage.store_asset(make_asset(4))
    storage.store_asset(make_asset(8))
    assert storage.get_id_s() == [4, 8]


def test_remove_asset(isolated_storage: Path) -> None:
    storage.store_asset(make_asset(1, "A"))
    storage.store_asset(make_asset(2, "B"))
    storage.remove_asset(1)
    remaining = storage.get_all_assets()
    assert [a.id_ for a in remaining] == [2]


def test_remove_asset_missing_file_raises(isolated_storage: Path) -> None:
    with pytest.raises(storage.AssetNotFoundError, match="No assets found"):
        storage.remove_asset(1)


def test_edit_asset_replaces_existing_and_keeps_sort(isolated_storage: Path) -> None:
    storage.store_asset(make_asset(2, "B"))
    storage.store_asset(make_asset(1, "A"))
    edited = Asset(1, "A-edit", 1500.0, 100.0, 6, "ddb", date(2023, 6, 1))
    storage.edit_asset(edited)

    assets = storage.get_all_assets()
    assert [a.id_ for a in assets] == [1, 2]
    assert assets[0].name == "A-edit"
    assert assets[0].method == "ddb"


def test_store_asset_duplicate_id_raises(isolated_storage: Path) -> None:
    storage.store_asset(make_asset(1, "A"))
    with pytest.raises(storage.DuplicateAssetError, match="already exists"):
        storage.store_asset(make_asset(1, "B"))


def test_edit_asset_missing_file_raises(isolated_storage: Path) -> None:
    with pytest.raises(storage.AssetNotFoundError, match="No assets found"):
        storage.edit_asset(make_asset(1))


def test_remove_all_clears_file(isolated_storage: Path) -> None:
    storage.store_asset(make_asset(1))
    storage.remove_all()
    assert isolated_storage.exists()
    assert isolated_storage.read_text(encoding="utf-8") == ""
