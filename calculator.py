"""
Calculator module for depreciator app
Does all depreciation schedule calculations
TODO: Depreciation % Depreciated
"""

from models import Asset

METHODS = [
    "straight line",
    "double declining balance",
    "sum of years digits",
    "sl",
    "ddb",
    "syd",
]


def depreciation_schedule(asset: Asset) -> list[tuple[int, float]]:
    method = asset.method
    db = asset.cost - asset.salvage
    if method in ("sl", "straight line"):
        depr = db / asset.life_years
        schedule = []
        for year in range(asset.life_years):
            schedule.append((year + 1, depr))
        return schedule
    if method in ("ddb", "double declining balance"):
        schedule = []
        bv = asset.cost
        rate = (1 / asset.life_years) * 2
        for year in range(asset.life_years):
            if bv <= asset.salvage:
                schedule.append((year + 1, 0))
                continue
            depr = min(bv * rate, bv - asset.salvage)
            bv -= depr
            schedule.append((year + 1, depr))
        return schedule
    if method in ("syd", "sum of years digits"):
        schedule = []
        db = asset.cost - asset.salvage
        digits = asset.life_years * (asset.life_years + 1) / 2
        for year in range(asset.life_years):
            depr = db * (asset.life_years - year) / digits
            schedule.append((year + 1, depr))
        return schedule
