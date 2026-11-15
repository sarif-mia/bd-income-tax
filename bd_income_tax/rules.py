"""Tax rules for individual taxpayers in Bangladesh.

The figures mirror the rules used by the bd-income-tax-calculator web app for
assessment years 2026-27 and 2027-28. Tax law changes with each Finance Act, so
always confirm against the latest NBR circulars before relying on a result.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Tuple

ASSESSMENT_YEARS: Tuple[str, ...] = ("2026-27", "2027-28")


class Category(str, Enum):
    """Taxpayer categories. Each has its own tax-free threshold."""

    GENERAL = "general"
    FEMALE = "female"
    SENIOR_CITIZEN = "senior"
    DISABLED = "disabled"
    FREEDOM_FIGHTER = "freedom-fighter"
    THIRD_GENDER = "third-gender"

    @property
    def threshold(self) -> int:
        return TAX_FREE_INCOME[self]

    @property
    def label(self) -> str:
        return CATEGORY_LABELS[self][0]

    @property
    def label_bn(self) -> str:
        return CATEGORY_LABELS[self][1]

    @classmethod
    def parse(cls, value: "Category | str") -> "Category":
        """Accept a Category, its value, its name, or the web app's camelCase id."""
        if isinstance(value, cls):
            return value
        key = str(value).strip()
        aliases = {"seniorCitizen": "senior", "freedomFighter": "freedom-fighter", "thirdGender": "third-gender"}
        key = aliases.get(key, key).lower().replace("_", "-")
        for member in cls:
            if key in (member.value, member.name.lower().replace("_", "-")):
                return member
        valid = ", ".join(m.value for m in cls)
        raise ValueError(f"Unknown taxpayer category {value!r}. Choose one of: {valid}")


TAX_FREE_INCOME: Dict[Category, int] = {
    Category.GENERAL: 375_000,
    Category.FEMALE: 425_000,
    Category.SENIOR_CITIZEN: 425_000,
    Category.DISABLED: 500_000,
    Category.FREEDOM_FIGHTER: 525_000,
    Category.THIRD_GENDER: 500_000,
}

CATEGORY_LABELS: Dict[Category, Tuple[str, str]] = {
    Category.GENERAL: ("General Taxpayer", "সাধারণ করদাতা"),
    Category.FEMALE: ("Female Taxpayer", "মহিলা করদাতা"),
    Category.SENIOR_CITIZEN: ("Senior Citizen (65+ years)", "সিনিয়র সিটিজেন (৬৫+ বছর)"),
    Category.DISABLED: ("Disabled Person", "প্রতিবন্ধী ব্যক্তি"),
    Category.FREEDOM_FIGHTER: ("Gazetted War-wounded Freedom Fighter", "গেজেটভুক্ত যুদ্ধাহত মুক্তিযোদ্ধা"),
    Category.THIRD_GENDER: ("Third Gender", "তৃতীয় লিঙ্গ"),
}


@dataclass(frozen=True)
class Band:
    """A tax band: the next ``width`` taka of taxable income is taxed at ``rate`` percent."""

    width: float
    rate: float


# Applied in order to income above the tax-free threshold.
TAX_BANDS: Tuple[Band, ...] = (
    Band(300_000, 10),
    Band(400_000, 15),
    Band(500_000, 20),
    Band(2_000_000, 25),
    Band(math.inf, 30),
)

# Investment rebate: the lowest of 3% of total income, 15% of eligible investment, or BDT 10 lakh.
REBATE_INCOME_PERCENT = 3
REBATE_INVESTMENT_PERCENT = 15
REBATE_CAP = 1_000_000

# Anyone with income above their tax-free threshold pays at least this much.
MINIMUM_TAX = 5_000
