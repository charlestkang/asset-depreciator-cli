"""
Storage module for project depreciator app
Handles reading and writing asset data to the csv file
"""

import csv
from datetime import date
from pathlib import Path
from collections.abc import Mapping, Sequence

from .models import Asset

FILE = Path("storage/assets.csv")

FIELDNAMES = Asset.FIELDS


class StorageError(Exception):
    """Base storage-layer exception."""


class AssetNotFoundError(StorageError):
    """Raised when an asset cannot be found in storage."""


class DuplicateAssetError(StorageError):
    """Raised when attempting to store an already-existing asset id."""


def _read_rows() -> list[dict[str, str]]:
    if not FILE.exists():
        return []
    with FILE.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _write_rows_atomic(rows: Sequence[Mapping[str, object]], write_header: bool = True) -> None:
    FILE.parent.mkdir(parents=True, exist_ok=True)
    temp_file = FILE.with_suffix(f"{FILE.suffix}.tmp")
    try:
        with temp_file.open("w", newline="", encoding="utf-8") as f:
            if write_header:
                writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
                writer.writeheader()
                writer.writerows(rows)
        temp_file.replace(FILE)
    except Exception:
        if temp_file.exists():
            temp_file.unlink()
        raise


def store_asset(asset: Asset) -> None:
    rows = _read_rows()
    if any(int(row["id_"]) == asset.id_ for row in rows):
        raise DuplicateAssetError(f"Asset with id {asset.id_} already exists")
    rows.append(asset.to_dict())
    rows.sort(key=lambda row: int(row["id_"]))
    _write_rows_atomic(rows)


def get_asset(id_: int) -> Asset:
    """Return the asset with given id or raise AssetNotFoundError."""
    rows = _read_rows()
    if not rows:
        raise AssetNotFoundError("No assets found")
    for row in rows:
        if int(row["id_"]) == id_:
            return asset_from_row(row)
    raise AssetNotFoundError(f"No asset found with id {id_}")

def get_all_assets() -> list[Asset]:
    """Return a list of all assets, or empty list if none found."""
    return [asset_from_row(row) for row in _read_rows()]


def asset_from_row(row: dict[str, str]) -> Asset:
    return Asset(
        id_=int(row["id_"]),
        name=row["name"],
        cost=float(row["cost"]),
        salvage=float(row["salvage"]),
        life_years=int(row["life_years"]),
        method=row["method"],
        date_=date.fromisoformat(row["date_"]),
    )


def get_next_id() -> int:
    rows = _read_rows()
    if not rows:
        return 1
    return max(int(row["id_"]) for row in rows) + 1


def get_id_s() -> list[int]:
    return [int(row["id_"]) for row in _read_rows()]


def remove_asset(id_: int) -> None:
    rows = _read_rows()
    if not rows:
        raise AssetNotFoundError("No assets found")
    new_rows = [row for row in rows if int(row["id_"]) != id_]
    if len(new_rows) == len(rows):
        raise AssetNotFoundError(f"No asset found with id {id_}")
    _write_rows_atomic(new_rows)


def remove_all() -> None:
    if not FILE.exists():
        return
    _write_rows_atomic([], write_header=False)


def edit_asset(asset: Asset) -> None:
    rows = _read_rows()
    if not rows:
        raise AssetNotFoundError("No assets found")
    if all(int(row["id_"]) != asset.id_ for row in rows):
        raise AssetNotFoundError(f"No asset found with id {asset.id_}")
    new_rows = [row for row in rows if int(row["id_"]) != asset.id_]
    new_rows.append(asset.to_dict())
    new_rows.sort(key=lambda row: int(row["id_"]))
    _write_rows_atomic(new_rows)
