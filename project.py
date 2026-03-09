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
    else:
        raise ValueError("Invalid method")


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
            display.inspect(asset, calculator.depreciation_schedule(asset), calculator.percent_depreciated(asset))
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
