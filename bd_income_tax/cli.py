"""``bd-income-tax`` command-line interface."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from . import __version__
from .formatting import format_bangla, format_bdt
from .rules import ASSESSMENT_YEARS, Category
from .tax import TaxResult, calculate


def _amount(text: str) -> float:
    try:
        return float(text.replace(",", "").replace("_", ""))
    except ValueError:
        raise argparse.ArgumentTypeError(f"not a number: {text!r}") from None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bd-income-tax",
        description=f"Bangladesh individual income tax calculator (assessment years {', '.join(ASSESSMENT_YEARS)}).",
        epilog="Example: bd-income-tax 850000 --investment 100000 --category female",
    )
    parser.add_argument("income", type=_amount, nargs="+", help="annual income in BDT; several amounts are added up")
    parser.add_argument("-i", "--investment", type=_amount, action="append", default=[], metavar="BDT",
                        help="eligible investment for the rebate (repeatable)")
    parser.add_argument("-c", "--category", default="general", choices=[c.value for c in Category],
                        help="taxpayer category (default: general)")
    parser.add_argument("--bn", action="store_true", help="show numbers in Bangla digits")
    parser.add_argument("--json", action="store_true", help="print the full result as JSON")
    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def render(result: TaxResult, bangla: bool = False) -> str:
    fmt = (lambda n: format_bangla(n, symbol=True)) if bangla else (lambda n: format_bdt(n, symbol=True))
    b = result.breakdown
    lines = [
        f"Category           {result.category.label}",
        f"Total income       {fmt(result.total_income)}",
        f"Tax-free income    {fmt(b.tax_free_income)}",
        f"Taxable income     {fmt(b.taxable_income)}",
    ]
    if b.bands:
        lines.append("")
        for band in b.bands:
            upper = "∞" if band.upper == float("inf") else format_bdt(band.upper)
            lines.append(f"  {band.rate:>4g}%  {format_bdt(band.lower):>11} – {upper:<11} {fmt(band.tax):>12}")
        lines.append("")
    lines.append(f"Gross tax          {fmt(b.gross_tax)}")
    if result.rebate.amount:
        lines.append(f"Investment rebate  -{fmt(result.rebate.amount)}")
    if result.minimum_tax_applied:
        lines.append("Minimum tax        applied")
    lines += [
        f"Tax payable        {fmt(result.tax_payable)}",
        f"Effective rate     {result.effective_rate:.2f}%",
        f"Net income         {fmt(result.net_income)}",
    ]
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    income = {f"income_{i + 1}": v for i, v in enumerate(args.income)} if len(args.income) > 1 else args.income[0]
    result = calculate(income, sum(args.investment) or None, args.category)
    if args.json:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(render(result, bangla=args.bn))
    return 0


if __name__ == "__main__":
    sys.exit(main())
