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

