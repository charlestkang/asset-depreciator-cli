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


class Metrics:
    def __init__(
        self,
        schedule: list[tuple[int, float, float]],
        total_depr: float,
        percent_time: float,
        percent_depr: float,
        progress: float,
        yearly_depr: float,
        daily_depr: float,
        elapsed_depr: float,
    ):
        self.schedule = schedule
        self.total_depr = total_depr
        self.percent_time = percent_time
        self.percent_depr = percent_depr
        self.progress = progress
        self.yearly_depr = yearly_depr
        self.daily_depr = daily_depr
        self.elapsed_depr = elapsed_depr


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
    """Calculate what fraction of the asset's useful life has elapsed (0.0 to 1.0+)."""
    delta = date.today() - asset.date_
    elapsed_days = max(0, delta.days)  # Clamp to 0 for future dates
    return min(elapsed_days / (asset.life_years * 365.25), 1.0)


def elapsed_depreciation(asset: Asset) -> float:
    """Legacy helper - prefer using build_metrics() instead."""
    metrics = build_metrics(asset)
    return metrics.elapsed_depr


def percent_depreciated(asset: Asset) -> float:
    """Legacy helper - prefer using build_metrics() instead."""
    metrics = build_metrics(asset)
    return metrics.percent_depr


def yearly_depreciation(asset: Asset) -> float:
    """Legacy helper - prefer using build_metrics() instead."""
    metrics = build_metrics(asset)
    return metrics.yearly_depr


def daily_depreciation(asset: Asset) -> float:
    """Legacy helper - prefer using build_metrics() instead."""
    metrics = build_metrics(asset)
    return metrics.daily_depr


def build_metrics(asset: Asset) -> Metrics:
    """
    Build all depreciation metrics for an asset in one pass.
    Computes depreciation_schedule() exactly once and derives all other values.
    """
    schedule = depreciation_schedule(asset)
    total_depr = schedule[-1][2]
    
    # Calculate elapsed time since asset was placed in service
    elapsed_days = (date.today() - asset.date_).days
    elapsed_years = elapsed_days / 365.25
    
    # Determine current year index (0-based) for schedule lookup
    if elapsed_days < 0:
        # Asset not yet in service (future date)
        year_idx = 0
        elapsed_depr = 0.0
        yearly_depr = 0.0
        percent_time_val = 0.0
    elif elapsed_years >= asset.life_years:
        # Asset has completed its useful life
        year_idx = asset.life_years - 1
        elapsed_depr = total_depr
        yearly_depr = 0.0  # No more depreciation after useful life
        percent_time_val = 1.0
    else:
        # Asset is currently in service
        year_idx = int(elapsed_years)
        year_idx = max(0, min(year_idx, asset.life_years - 1))
        elapsed_depr = schedule[year_idx][2]
        yearly_depr = schedule[year_idx][1]
        percent_time_val = min(elapsed_years / asset.life_years, 1.0)
    
    # Calculate derived metrics
    percent_depr = elapsed_depr / total_depr if total_depr > 0 else 0.0
    daily_depr = yearly_depr / 365.25
    
    return Metrics(
        schedule=schedule,
        total_depr=total_depr,
        percent_time=percent_time_val,
        percent_depr=percent_depr,
        progress=percent_depr,
        yearly_depr=yearly_depr,
        daily_depr=daily_depr,
        elapsed_depr=elapsed_depr,
    )