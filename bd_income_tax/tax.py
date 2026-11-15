"""Income tax, investment rebate and minimum-tax calculations."""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Union

from .rules import (
    MINIMUM_TAX,
    REBATE_CAP,
    REBATE_INCOME_PERCENT,
    REBATE_INVESTMENT_PERCENT,
    TAX_BANDS,
    Category,
)

Number = Union[int, float]
Amounts = Union[Number, str, Mapping[str, Union[Number, str, None]], None]


@dataclass(frozen=True)
class BandTax:
    """Tax charged in one band."""

    lower: float  # first taka in the band (inclusive)
    upper: float  # last taka in the band (inclusive); inf for the top band
    rate: float
    income: float
    tax: float


@dataclass(frozen=True)
class TaxBreakdown:
    """Gross tax before rebate and minimum tax."""

    total_income: float
    tax_free_income: int
    taxable_income: float
    bands: List[BandTax]
    gross_tax: int
    effective_rate: float  # percent of total income


@dataclass(frozen=True)
class Rebate:
    """Investment tax rebate."""

    investment: float
    on_investment: float  # 15% of investment
    on_income: float  # 3% of income
    amount: int  # what is actually allowed, after the BDT 10 lakh cap
    capped: bool


@dataclass(frozen=True)
class TaxResult:
    """Full result of :func:`calculate`."""

    category: Category
    total_income: int
    total_investment: int
    breakdown: TaxBreakdown
    rebate: Rebate
    tax_after_rebate: int
    minimum_tax_applied: bool
    tax_payable: int
    net_income: int
    effective_rate: float  # percent of total income
    income_items: Dict[str, float] = field(default_factory=dict)
    investment_items: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Plain-dict form, ready for ``json.dumps``. The top band's upper bound is ``None``."""
        data = asdict(self)
        data["category"] = self.category.value
        for band in data["breakdown"]["bands"]:
            if band["upper"] == math.inf:
                band["upper"] = None
        return data


def _to_number(value: Union[Number, str, None]) -> float:
    if value is None or value == "":
        return 0.0
    if isinstance(value, str):
        value = value.replace(",", "").replace("_", "").strip()
    number = float(value)
    if math.isnan(number) or math.isinf(number):
        raise ValueError(f"Amount must be a finite number, got {value!r}")
    return number


def _items(amounts: Amounts) -> Dict[str, float]:
    if amounts is None:
        return {}
    if isinstance(amounts, Mapping):
        return {str(k): _to_number(v) for k, v in amounts.items()}
    return {"total": _to_number(amounts)}


def calculate_tax(total_income: Number, category: Union[Category, str] = Category.GENERAL) -> TaxBreakdown:
    """Gross income tax by band, before any rebate or minimum tax.

    >>> calculate_tax(850_000).gross_tax
    56250
    """
    category = Category.parse(category)
    income = _to_number(total_income)
    threshold = category.threshold
    taxable = max(0.0, income - threshold)

    bands: List[BandTax] = []
    remaining, start, tax = taxable, float(threshold), 0.0
    for band in TAX_BANDS:
        if remaining <= 0:
            break
        in_band = min(remaining, band.width)
        band_tax = in_band * band.rate / 100
        upper = start + band.width
        bands.append(BandTax(lower=start + 1, upper=upper, rate=band.rate, income=in_band, tax=band_tax))
        tax += band_tax
        remaining -= in_band
        start = upper

    return TaxBreakdown(
        total_income=income,
        tax_free_income=threshold,
        taxable_income=taxable,
        bands=bands,
        gross_tax=round(tax),
        effective_rate=round(tax / income * 100, 2) if income > 0 else 0.0,
    )


def calculate_rebate(total_income: Number, investment: Number) -> Rebate:
    """Investment rebate: the lowest of 3% of income, 15% of investment, or BDT 10 lakh.

    >>> calculate_rebate(1_000_000, 500_000).amount
    30000
    """
    income = max(0.0, _to_number(total_income))
    invested = max(0.0, _to_number(investment))
    on_investment = invested * REBATE_INVESTMENT_PERCENT / 100
    on_income = income * REBATE_INCOME_PERCENT / 100
    uncapped = min(on_investment, on_income)
    return Rebate(
        investment=invested,
        on_investment=on_investment,
        on_income=on_income,
        amount=round(min(uncapped, REBATE_CAP)),
        capped=uncapped > REBATE_CAP,
    )


def calculate(
    income: Amounts,
    investment: Amounts = None,
    category: Union[Category, str] = Category.GENERAL,
) -> TaxResult:
    """Tax payable after the investment rebate and minimum tax.

    ``income`` and ``investment`` can each be a single amount or a mapping of
    named amounts (e.g. ``{"salary": 800000, "house_rent": 50000}``). Strings
    such as ``"8,00,000"`` are accepted.

    >>> calculate({"salary": 800_000, "other": 50_000}).tax_payable
    56250
    >>> calculate(376_000, investment=100_000).minimum_tax_applied
    True
    """
    category = Category.parse(category)
    income_items = _items(income)
    investment_items = _items(investment)
    total_income = sum(income_items.values())
    total_investment = sum(investment_items.values())

    breakdown = calculate_tax(total_income, category)
    rebate = calculate_rebate(total_income, total_investment)

    after_rebate = max(0, breakdown.gross_tax - rebate.amount)
    minimum_applied = total_income > breakdown.tax_free_income and after_rebate < MINIMUM_TAX
    payable = MINIMUM_TAX if minimum_applied else after_rebate

    return TaxResult(
        category=category,
        total_income=round(total_income),
        total_investment=round(total_investment),
        breakdown=breakdown,
        rebate=rebate,
        tax_after_rebate=after_rebate,
        minimum_tax_applied=minimum_applied,
        tax_payable=payable,
        net_income=round(total_income - payable),
        effective_rate=round(payable / total_income * 100, 2) if total_income > 0 else 0.0,
        income_items=income_items,
        investment_items=investment_items,
    )


def tax_free_threshold(category: Optional[Union[Category, str]] = None) -> int:
    """Tax-free income for a category (general by default)."""
    return Category.parse(category or Category.GENERAL).threshold
