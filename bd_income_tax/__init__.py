"""Bangladesh individual income tax calculator.

>>> from bd_income_tax import calculate
>>> calculate({"salary": 800_000, "house_rent": 50_000}, investment=100_000).tax_payable
41250
"""
from .finance import emi, future_value
from .formatting import format_bangla, format_bdt, to_bangla_digits
from .rules import ASSESSMENT_YEARS, MINIMUM_TAX, TAX_BANDS, TAX_FREE_INCOME, Category
from .tax import BandTax, Rebate, TaxBreakdown, TaxResult, calculate, calculate_rebate, calculate_tax, tax_free_threshold

__version__ = "0.1.0"

__all__ = [
    "ASSESSMENT_YEARS",
    "MINIMUM_TAX",
    "TAX_BANDS",
    "TAX_FREE_INCOME",
    "BandTax",
    "Category",
    "Rebate",
    "TaxBreakdown",
    "TaxResult",
    "calculate",
    "calculate_rebate",
    "calculate_tax",
    "emi",
    "format_bangla",
    "format_bdt",
    "future_value",
    "tax_free_threshold",
    "to_bangla_digits",
]
