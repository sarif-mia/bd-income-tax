"""Number formatting in the South Asian (lakh/crore) style, in English or Bangla digits."""
from __future__ import annotations

import math

_BANGLA_DIGITS = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")


def format_bdt(amount: float, symbol: bool = False) -> str:
    """Format a whole-taka amount with lakh grouping: ``1234567 -> '12,34,567'``.

    >>> format_bdt(1234567)
    '12,34,567'
    >>> format_bdt(-5000.6, symbol=True)
    '-৳5,001'
    """
    if amount == math.inf:
        return "∞"
    negative = amount < 0
    digits = str(int(round(abs(amount))))
    if len(digits) > 3:
        head, tail = digits[:-3], digits[-3:]
        groups = []
        while len(head) > 2:
            groups.insert(0, head[-2:])
            head = head[:-2]
        if head:
            groups.insert(0, head)
        digits = ",".join(groups + [tail])
    return f"{'-' if negative else ''}{'৳' if symbol else ''}{digits}"


def to_bangla_digits(value: object) -> str:
    """Replace ASCII digits with Bangla digits: ``'12,500' -> '১২,৫০০'``."""
    return str(value).translate(_BANGLA_DIGITS)


def format_bangla(amount: float, symbol: bool = False) -> str:
    """:func:`format_bdt` using Bangla digits: ``1234567 -> '১২,৩৪,৫৬৭'``."""
    return to_bangla_digits(format_bdt(amount, symbol=symbol))
