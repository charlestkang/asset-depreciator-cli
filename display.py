"""
Display module for depreciator app
Handles all input/output for the app
"""

from models import Asset

ID_WIDTH = 5
NAME_WIDTH = 40
COST_WIDTH = 10
SALVAGE_WIDTH = 10
LIFE_YEARS_WIDTH = 5
METHOD_WIDTH = 5
YEAR_WIDTH = 6
DEPRECIATION_WIDTH = 20


def hello() -> None:
    print("\nWelcome to the Depreciator app!")


def display_asset(asset: Asset) -> None:
    if not asset:
        print("\nNo asset found")
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
    )


def display_assets(assets: list[Asset]) -> None:
    if assets == []:
        print("\nNo assets to display")
        return None
    print_header()
    for asset in assets:
        display_asset(asset)


def print_header() -> None:
    print()
    print(
        f"{'ID':<{ID_WIDTH}} "
        f"{'NAME':<{NAME_WIDTH}} "
        f"{'COST':>{COST_WIDTH}} "
        f"{'SALVAGE':>{SALVAGE_WIDTH}} "
        f"{'LIFE':>{LIFE_YEARS_WIDTH}} "
        f"{'METHOD':<{METHOD_WIDTH}} "
    )
    print(
        f"{'-'*ID_WIDTH} "
        f"{'-'*NAME_WIDTH} "
        f"{'-'*COST_WIDTH} "
        f"{'-'*SALVAGE_WIDTH} "
        f"{'-'*LIFE_YEARS_WIDTH} "
        f"{'-'*METHOD_WIDTH} "
    )


def print_depreciation_header(asset: Asset) -> None:
    print(f"\nID: {asset.id_}, Name: {asset.name}\n")
    print(f"{'YEAR':<{YEAR_WIDTH}} " f"{'Depreciation':>{DEPRECIATION_WIDTH}} ")
    print(f"{'-'*YEAR_WIDTH} " f"{'-'*DEPRECIATION_WIDTH} ")


def inspect(asset: Asset, schedule: list[tuple[int, float]]) -> None:
    print_depreciation_header(asset)
    for year, depreciation in schedule:
        print(f"{year:<{YEAR_WIDTH}}|{depreciation:>{DEPRECIATION_WIDTH}.2f} ")
