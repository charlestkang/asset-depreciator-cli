# GPT Code Review Briefing

## Project Overview
This merged file was generated from the project folder: C:\Users\Paul\Documents\9-Projects\asset-depreciator-cli

The contents below were aggregated recursively into one review document.
Included file types: .md, .py

## File Structure
Each file is preceded by a marker in this format:
===== FILE: relative/path/to/file.ext =====

## Review Objectives
Please review the project for:
1. Architecture and separation of concerns
2. Bugs and logical errors
3. Refactoring opportunities
4. Style and readability improvements
5. Testing gaps

## Project Tree
asset-depreciator-cli/
  calculator.py
  display.py
  models.py
  project.py
  README.md
  storage.py
  test_project.py

## Merged Code Begins Below


================================================================================
===== FILE: calculator.py =====
================================================================================
"""
Calculator module for depreciator app
Does all depreciation schedule calculations
"""

from datetime import date

from models import Asset

METHODS = [
    "straight line",
    "double declining balance",
    "sum of years digits",
    "sl",
    "ddb",
    "syd",
]

# All data comes from storage/assets.csv which is normalized data, clean water to drink
def depreciation_schedule(asset: Asset) -> list[tuple[int, float, float]]:
    if asset.method == "sl":
        return sl(asset)
    if asset.method == "ddb":
        return ddb(asset)
    if asset.method == "syd":
        return syd(asset)
    else:
        raise ValueError("No method or unusable method name")


def sl(asset: Asset) -> list[tuple[int, float, float]]:
    db = asset.cost - asset.salvage
    depr = db / asset.life_years
    schedule = []
    a_depr = 0
    for year in range(asset.life_years):
        a_depr += depr
        schedule.append((year + 1, depr, a_depr))
    return schedule


def ddb(asset: Asset) -> list[tuple[int, float, float]]:
    db = asset.cost - asset.salvage
    schedule = []
    bv = asset.cost
    rate = (1 / asset.life_years) * 2
    a_depr = 0
    for year in range(asset.life_years):
        sl_depr = (bv - asset.salvage) / (asset.life_years - year)
        if bv <= asset.salvage:
            schedule.append((year + 1, 0, a_depr))
            continue
        depr = min(bv * rate, bv - asset.salvage)
        # Per accounting convention, switches to sl if sl > ddb for given year onwards
        if sl_depr > depr:
            depr = min(sl_depr, bv - asset.salvage)
        if year == asset.life_years - 1:
            depr = bv - asset.salvage
        bv -= depr
        a_depr += depr
        schedule.append((year + 1, depr, a_depr))
    return schedule


def syd(asset: Asset) -> list[tuple[int, float, float]]:
    db = asset.cost - asset.salvage
    schedule = []
    digits = asset.life_years * (asset.life_years + 1) / 2
    a_depr = 0
    for year in range(asset.life_years):
        depr = db * (asset.life_years - year) / digits
        a_depr += depr
        schedule.append((year + 1, depr, a_depr))
    return schedule


def total_depreciation(asset: Asset) -> float:
    schedule = depreciation_schedule(asset)
    if not schedule:
        raise ValueError
    return schedule[-1][2]


def percent_time(asset: Asset) -> float:
    delta = date.today() - asset.date_
    return min(delta.days / (asset.life_years * 365.25), 1.0)


def elapsed_depreciation(asset: Asset) -> float:
    percent = percent_time(asset)
    elapsed_idx = int(percent * asset.life_years) - 1
    if elapsed_idx < 0:
        return 0.0
    return depreciation_schedule(asset)[elapsed_idx][2]


def percent_depreciated(asset: Asset) -> float:
    return elapsed_depreciation(asset) / total_depreciation(asset)

================================================================================
===== FILE: display.py =====
================================================================================
"""
Display module for depreciator app
Handles all input/output for the app
"""

from models import Asset
import calculator

ID_WIDTH = 5
NAME_WIDTH = 20
COST_WIDTH = 8
SALVAGE_WIDTH = 8
LIFE_YEARS_WIDTH = 5
METHOD_WIDTH = 7
YEAR_WIDTH = 5
DEPRECIATION_WIDTH = 20
DATE_WIDTH = 11
ACCUMULATED_WIDTH = 20
CHART_WIDTH = 20
PROGRESS_BAR_LENGTH = 45

def hello() -> None:
    print("\nWelcome to the Depreciator app!\n")


def display_asset(asset: Asset) -> None:
    if not asset:
        print("\nNo asset found")
        return
    name = asset.name
    if len(name) >= NAME_WIDTH:
        name = name[: NAME_WIDTH - 3] + "..."
    print(
        f"{asset.id_:<{ID_WIDTH}} "
        f"{name:<{NAME_WIDTH}} "
        f"{asset.cost:>{COST_WIDTH}} "
        f"{asset.salvage:>{SALVAGE_WIDTH}} "
        f"{asset.life_years:>{LIFE_YEARS_WIDTH}} "
        f"{asset.method:>{METHOD_WIDTH}} "
        f"{str(asset.date_):>{DATE_WIDTH}} "
    )


def display_assets(assets: list[Asset]) -> None:
    if not assets:
        print("\nNo assets to display")
        return None
    print_view_header()
    for asset in assets:
        display_asset(asset)


def print_view_header() -> None:
    print()
    print(
        f"{'ID':<{ID_WIDTH}} "
        f"{'NAME':<{NAME_WIDTH}} "
        f"{'COST':>{COST_WIDTH}} "
        f"{'SALVAGE':>{SALVAGE_WIDTH}} "
        f"{'LIFE':>{LIFE_YEARS_WIDTH}} "
        f"{'METHOD':>{METHOD_WIDTH}} "
        f"{'DATE (YMD)':>{DATE_WIDTH}} "
    )
    print(
        f"{'-'*ID_WIDTH} "
        f"{'-'*NAME_WIDTH} "
        f"{'-'*COST_WIDTH} "
        f"{'-'*SALVAGE_WIDTH} "
        f"{'-'*LIFE_YEARS_WIDTH} "
        f"{'-'*METHOD_WIDTH} "
        f"{'-'*DATE_WIDTH} "
    )


def print_depreciation_header(asset: Asset) -> None:
    print(f"\nID: {asset.id_}, Name: {asset.name} ")

    progress = (calculator.percent_depreciated(asset))
    bar = int(progress * PROGRESS_BAR_LENGTH)
    percent = f"{progress * 100:.2f}%"
    print()
    print("Progress: ", "█" * bar, "░" * (PROGRESS_BAR_LENGTH - bar), " ", percent, sep="")
    print()
    print(
        f"{'YEAR':<{YEAR_WIDTH}} "
        f"{'Depreciation':>{DEPRECIATION_WIDTH}} "
        f"{'Accumulated':>{ACCUMULATED_WIDTH}} "
        f"{'Depreciated':>{CHART_WIDTH}} "
    )
    print(
        f"{'-'*YEAR_WIDTH} "
        f"{'-'*DEPRECIATION_WIDTH} "
        f"{'-'*ACCUMULATED_WIDTH} "
        f"{'-'*CHART_WIDTH}"
    )


def inspect(asset: Asset, schedule: list[tuple[int, float, float]]) -> None:
    print_depreciation_header(asset)
    total_accum = schedule[-1][2]
    for year, depreciation, accumulated in schedule:
        chart_mult = int(CHART_WIDTH * (accumulated / total_accum))
        print(
            f"{year:<{YEAR_WIDTH}}|{depreciation:>{DEPRECIATION_WIDTH}.2f}|{accumulated:>{ACCUMULATED_WIDTH}.2F}|{'█'*chart_mult}"
        )

================================================================================
===== FILE: models.py =====
================================================================================
"""
Models for the depreciator app.
Defines the Asset class and related domain logic.
"""

from datetime import date


class Asset:

    FIELDS = ["id_", "name", "cost", "salvage", "life_years", "method", "date_"]

    def __init__(
        self,
        id_: int,
        name: str,
        cost: float,
        salvage: float,
        life_years: int,
        method: str,
        date_: date,
    ):
        if cost < 0:
            raise ValueError("Cost cannot be negative")
        if life_years <= 0:
            raise ValueError("Life years must be greater than 0")
        if salvage >= cost:
            raise ValueError("Salvage must be less than cost")

        self.id_ = id_
        self.name = name
        self.cost = cost
        self.salvage = salvage
        self.life_years = life_years
        self.method = method
        self.date_ = date_

    def __str__(self):
        return (
            f"id: {self.id_}, "
            f"name: {self.name}, "
            f"cost: {self.cost}, "
            f"salvage: {self.salvage}, "
            f"life years: {self.life_years}, "
            f"method: {self.method}, "
            f"date placed in service: {self.date_} "
        )

    def __eq__(self, other):
        if not isinstance(other, Asset):
            return False
        return (
            self.id_ == other.id_
            and self.name == other.name
            and self.cost == other.cost
            and self.salvage == other.salvage
            and self.life_years == other.life_years
            and self.method == other.method
            and self.date_ == other.date_
        )

    def to_dict(self):
        return {
            "id_": self.id_,
            "name": self.name,
            "cost": self.cost,
            "salvage": self.salvage,
            "life_years": self.life_years,
            "method": self.method,
            "date_": self.date_,
        }

================================================================================
===== FILE: project.py =====
================================================================================
"""
Main CLI entry point for the depreciator app.
Handles user interaction and coordinates modules.
"""

from datetime import date
import string

import calculator
import display
from models import Asset
import storage

# TODO:


OPTIONS = ["add", "view", "remove all", "exit"]
FIELD_NAMES = ["id", "name", "cost", "salvage", "life", "method", "date"]


def hello_user() -> None:
    display.hello()


def add_asset() -> Asset:
    while True:
        try:
            id_ = storage.get_next_id()
            name = get_str("Item name: ")
            cost = get_float("Item cost: ")
            salvage = get_float_optional("Salvage value (default 0): ")
            life_years = get_int("Item lifetime in whole number years: ")
            method = get_method("Depreciation method: ")
            date_ = get_date("Date put in service (YYYY-MM-DD): ")
            new_asset = build_asset(id_, name, cost, salvage, life_years, method, date_)
            print("\nItem added")
            return new_asset
        except ValueError as e:
            print(f"\n{e}\n")
            pass


def build_asset(
    id_: int,
    name: str,
    cost: float,
    salvage: float,
    life_years: int,
    method: str,
    date_: date,
) -> Asset:
    return Asset(id_, name, cost, salvage, life_years, method, date_)


def normalize_method(method) -> str:
    if method in ("straight line", "sl"):
        return "sl"
    elif method in ("double declining balance", "ddb"):
        return "ddb"
    elif method in ("sum of years digits", "syd"):
        return "syd"


def get_intention() -> str:
    while True:
        print(f"{" | ".join(OPTIONS)}")
        s = input(">").strip().lower()
        if s in OPTIONS:
            return s
        elif s == "":
            return "exit"
        print("\nPlease input one of the given options")


def get_date(prompt: str = "") -> date:
    while True:
        s = input(prompt)
        try:
            if not s.strip():
                raise ValueError
            if not all(c.isnumeric() or c == "-" for c in s):
                raise ValueError
            year, month, day = s.split("-")
            year, month, day = int(year), int(month), int(day)
            return date(year, month, day)
        except ValueError:
            print("Please input a valid date in YYYY-MM-DD format")


def get_str(prompt: str = "") -> str:
    while True:
        s = input(prompt)
        try:
            # Guard clauses against empty and all-punct strs
            if not s.strip():
                raise ValueError
            if all(c in string.punctuation for c in s):
                raise ValueError
            return s.strip()
        except ValueError:
            print("Must not be empty or only punctuation")
            pass


def get_method(prompt: str = "") -> str:
    while True:
        print(f"Method options: {" | ".join(calculator.METHODS)}")
        s = input(prompt).strip().lower()
        if s in calculator.METHODS:
            return normalize_method(s)
        print("\nPlease select one of the given methods\n")


def get_float(prompt: str = "") -> float:
    while True:
        s = input(prompt)
        try:
            if not s.strip():
                raise ValueError
            s = s.replace("$", "").replace(",", "")
            s = float(s)
            if s < 0:
                raise ValueError
            return s
        except ValueError:
            print("Must be a non-empty, nonnegative number")
            pass


def get_float_optional(prompt: str = "", default=0) -> float:
    while True:
        s = input(prompt)
        try:
            if not s.strip():
                return default
            s = s.replace("$", "").replace(",", "")
            s = float(s)
            if s < 0:
                raise ValueError
            return s
        except ValueError:
            print("Must be a non-empty, nonnegative number")
            pass


def get_int(prompt: str = "") -> int:
    while True:
        s = input(prompt)
        try:
            if not s.strip():
                raise ValueError
            else:
                s = s.replace("$", "").replace(",", "")
            s = float(s)
            if s <= 0 or not s.is_integer():
                raise ValueError
            return int(s)
        except ValueError:
            print("Years must be a positive whole number.")
            pass


def find_asset_by_id_(id_: int, assets: list[Asset]) -> Asset | None:
    return next((asset for asset in assets if asset.id_ == id_), None)


def view_screen() -> None:
    while True:
        assets = storage.get_all_assets()
        if not assets:
            print("\nNo assets to display\n")
            return
        id_s = {asset.id_ for asset in assets}
        display.display_assets(assets)
        try:
            id_ = input("\nInspect id (enter to return): ").strip()
            if id_ == "":
                return
            id_ = int(id_)
            if id_ in id_s:
                inspect(id_, assets)
            else:
                print("Please select a valid id")
                continue
        except ValueError:
            print("Please select a valid id 2")
            continue


def inspect(id_: int, assets: list[Asset]) -> None:
    asset = find_asset_by_id_(id_, assets)
    if asset:
        while True:
            asset = storage.get_asset(id_)
            display.inspect(asset, calculator.depreciation_schedule(asset))
            print('\nType "remove" to delete, "edit" to edit or press Enter to return')
            response = input(">").strip().lower()
            if response == "remove":
                yn = input("Are you sure? y/n: ").strip().lower()
                if yn in ("y", "yes"):
                    storage.remove_asset(id_)
                return
            if response == "":
                return
            if response == "edit":
                edit_asset(id_)
    else:
        print("\nNo such asset")
        return


def edit_asset(id_: int) -> None:
    while True:
        print(" | ".join(FIELD_NAMES[1:]))
        print("Which attribute to edit? Press Enter to return: ")
        c_attr = input(">").strip().lower()
        if c_attr == "name":
            c_val = get_str("New name: ")
        elif c_attr == "cost":
            c_val = get_float("New cost: ")
        elif c_attr == "salvage":
            c_val = get_float("New salvage: ")
        elif c_attr == "life":
            c_attr = "life_years"
            c_val = get_int("New object useful life: ")
        elif c_attr == "method":
            c_val = get_method("New depreciation method: ")
        elif c_attr == "date":
            c_attr = "date_"
            c_val = get_date("New put in service date (YYYY-M-DD): ")
        elif c_attr == "":
            return
        else:
            print("\nPlease select one of the given options\n")
            continue

        old_asset = storage.get_asset(id_)
        data = old_asset.to_dict()
        data[c_attr] = c_val
        new_asset = Asset(**data)
        storage.edit_asset(new_asset)
        return


def main():
    hello_user()
    while True:
        intention = get_intention()
        match intention:
            case "add":
                new_asset = add_asset()
                storage.store_asset(new_asset)
                print()
            case "view":
                view_screen()
            case "remove all":
                response = input("Are you sure? ").strip().lower()
                if response == "y" or response == "yes":
                    storage.remove_all()
            case "exit":
                return


if __name__ == "__main__":
    main()

================================================================================
===== FILE: README.md =====
================================================================================
# Asset Depreciation CLI

A command-line tool for tracking assets and calculating depreciation schedules and
accumulated depreciation using multiple accounting methods.

Built as a final project for Harvard's CS50P course.

### Usage:
 - This is a CLI script running in the terminal, simply type "python project.py" to get
    up and running

### Implementation Details:
 - Uses an Asset class for assets added to the depreciator to keep attributes organized
 - Separated into different modules for separation of concerns and debugging ease
 - Uses csv.DictWriter to maintain data persistence by writing into and reading csv
     files
 - Built for and while completing CS50P


================================================================================
===== FILE: storage.py =====
================================================================================
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


def get_asset(id_: int) -> Asset | None:
    """Return the asset with given id, or None if not found."""
    if not FILE.exists():
        return None
    with FILE.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if int(row["id_"]) == id_:
                return asset_from_row(row)
    return None


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

================================================================================
===== FILE: test_project.py =====
================================================================================
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
        Asset(42, "test", 50, 42, 1, "sl", "1999-01-01"),
        Asset(43, "test2", 50, 42, 1, "sl", "1999-01-01"),
    ]
    assert project.find_asset_by_id_(43, test_assets) == test_assets[1]


def test_build_asset():
    test_asset = Asset(43, "test2", 50, 42, 1, "sl", "1999-01-01")
    assert project.build_asset(43, "test2", 50, 42, 1, "sl", "1999-01-01") == test_asset

