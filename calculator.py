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
