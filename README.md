# bd-income-tax

Calculate Bangladesh individual income tax in Python or from the command line. It covers the tax bands, the six taxpayer categories, the investment rebate and the minimum tax, and it formats amounts in lakh style or with Bangla digits.

No dependencies. Python 3.9+.

```sh
pip install bd-income-tax
```

## Command line

```console
$ bd-income-tax 850000 --investment 100000
Category           General Taxpayer
Total income       ৳8,50,000
Tax-free income    ৳3,75,000
Taxable income     ৳4,75,000

    10%     3,75,001 – 6,75,000         ৳30,000
    15%     6,75,001 – 10,75,000        ৳26,250

Gross tax          ৳56,250
Investment rebate  -৳15,000
Tax payable        ৳41,250
Effective rate     4.85%
Net income         ৳8,08,750
```

Options:

| Option | Meaning |
| --- | --- |
| `-c, --category` | `general` (default), `female`, `senior`, `disabled`, `freedom-fighter`, `third-gender` |
| `-i, --investment` | Eligible investment for the rebate. You can repeat it. |
| `--bn` | Show amounts in Bangla digits (৳৮,৫০,০০০) |
| `--json` | Print the full breakdown as JSON |

Several income amounts are added together: `bd-income-tax 600000 250000`.

## Python

```python
from bd_income_tax import calculate, format_bdt

result = calculate(
    income={"salary": 800_000, "house_rent": 50_000},
    investment={"sanchaypatra": 60_000, "dps": 40_000},
    category="female",
)
result.tax_payable          # 33750
result.breakdown.bands      # tax charged in each band
result.rebate.amount        # 15000
result.to_dict()            # JSON-ready
format_bdt(result.net_income, symbol=True)  # '৳8,16,250'
```

Other helpers:

- `calculate_tax(income, category)`: gross tax by band, before rebate
- `calculate_rebate(income, investment)`: the investment rebate
- `format_bdt`, `format_bangla`, `to_bangla_digits`: lakh/crore and Bangla number formatting
- `future_value(principal, monthly_deposit, annual_rate_pct, months)` and `emi(principal, annual_rate_pct, months)`: DPS and loan maths

## Rules used

These rules apply to assessment years **2026-27** and **2027-28**. They match the [bd-income-tax-calculator](https://github.com/sarif-mia/bd-income-tax-calculator) web app.

**Tax-free income by category**

| Category | Tax-free income |
| --- | --- |
| General | ৳3,75,000 |
| Female | ৳4,25,000 |
| Senior citizen (65+) | ৳4,25,000 |
| Disabled person | ৳5,00,000 |
| Third gender | ৳5,00,000 |
| Gazetted war-wounded freedom fighter | ৳5,25,000 |

**Tax bands**, applied to income above the tax-free amount:

| Band | Rate |
| --- | --- |
| Next ৳3,00,000 | 10% |
| Next ৳4,00,000 | 15% |
| Next ৳5,00,000 | 20% |
| Next ৳20,00,000 | 25% |
| Above that | 30% |

**Investment rebate:** the lowest of 3% of total income, 15% of eligible investment, or ৳10,00,000.

**Minimum tax:** anyone whose income is above their tax-free amount pays at least ৳5,000.

**Not covered:** the wealth surcharge, which depends on net-wealth details.

> Tax law changes with every Finance Act. Use this package as an estimate and check the latest NBR rules before you file.

## License

MIT
