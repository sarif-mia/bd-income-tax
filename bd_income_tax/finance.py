"""Savings and loan helpers (DPS, FDR, EMI)."""
from __future__ import annotations


def future_value(principal: float, monthly_deposit: float, annual_rate: float, months: int) -> float:
    """Value of a lump sum plus monthly deposits after ``months``, compounded monthly.

    ``annual_rate`` is a percentage, e.g. ``9`` for 9%.

    >>> future_value(100_000, 10_000, 0, 12)
    220000.0
    """
    principal, deposit, months = max(0.0, principal), max(0.0, monthly_deposit), max(0, int(months))
    r = annual_rate / 100 / 12
    if r == 0:
        return float(principal + deposit * months)
    growth = (1 + r) ** months
    return principal * growth + deposit * (growth - 1) / r


def emi(principal: float, annual_rate: float, months: int) -> float:
    """Equal monthly instalment for a loan. ``annual_rate`` is a percentage.

    >>> emi(120_000, 0, 12)
    10000.0
    >>> round(emi(500_000, 12, 36), 2)
    16607.15
    """
    principal, months = max(0.0, principal), max(0, int(months))
    if not principal or not months:
        return 0.0
    r = annual_rate / 100 / 12
    if r == 0:
        return principal / months
    growth = (1 + r) ** months
    return principal * r * growth / (growth - 1)
