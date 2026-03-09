"""
Storage module for project depreciator app
Handles reading and writing asset data to the csv file
"""

import csv
from pathlib import Path
from datetime import date

from models import Asset

FILE = Path("storage/assets.csv")

FIELDNAMES = Asset.FIELDS


def store_asset(asset: Asset) -> None:
    with FILE.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if f.tell() == 0:
            writer.writeheader()
        writer.writerow(asset.to_dict())


def get_asset(id_: int) -> Asset:
    """Return the asset with given id, or None if not found."""
    if not FILE.exists():
        raise ValueError("No assets found")
    with FILE.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if int(row["id_"]) == id_:
                return asset_from_row(row)
    raise ValueError(f"No asset found with id {id_}")   

# returns None if no assets
def get_all_assets() -> list[Asset]:
    """Return a list of all assets, or empty list if none found."""
    if not FILE.exists():
        return []
    with FILE.open("r", newline="", encoding="utf-8") as f:
        assets = []
        reader = csv.DictReader(f)
        for row in reader:
            assets.append(asset_from_row(row))
    return assets


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


def get_next_id() -> int :
    if not FILE.exists():
        return 1
    with FILE.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        max_id_ = 0
        for row in reader:
            max_id_ = max(int(row["id_"]), max_id_)
        return max_id_ + 1


def get_id_s() -> list[int]:
    if not FILE.exists():
        return []
    with FILE.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [int(row["id_"]) for row in reader]


def remove_asset(id_: int) -> bool:
    if not FILE.exists():
        return False
    with FILE.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [row for row in reader if int(row["id_"]) != id_]
    with FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return True


def remove_all() -> None:
    if not FILE.exists():
        return
    with FILE.open("w", newline="", encoding="utf-8") as f:
        pass


def edit_asset(asset: Asset) -> None:
    if not FILE.exists():
        return None
    with FILE.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        assets = [row for row in reader if int(row["id_"]) != asset.id_]
    assets.append(asset.to_dict())
    assets.sort(key=lambda a: int(a["id_"]))
    with FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for row in assets:
            writer.writerow(row)
