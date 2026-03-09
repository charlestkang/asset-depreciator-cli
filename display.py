"""
Display module for depreciator app
Handles all input/output for the app
"""

from models import Asset

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


def print_depreciation_header(asset: Asset, progress: float) -> None:
    print(f"\nID: {asset.id_}, Name: {asset.name} ")

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


def inspect(asset: Asset, schedule: list[tuple[int, float, float]], progress: float) -> None:
    print_depreciation_header(asset, progress)
    total_accum = schedule[-1][2]
    for year, depreciation, accumulated in schedule:
        chart_mult = int(CHART_WIDTH * (accumulated / total_accum))
        print(
            f"{year:<{YEAR_WIDTH}}|{depreciation:>{DEPRECIATION_WIDTH}.2f}|{accumulated:>{ACCUMULATED_WIDTH}.2F}|{'█'*chart_mult}"
        )
