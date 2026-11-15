import json
import math

import pytest

from bd_income_tax import (
    Category,
    calculate,
    calculate_rebate,
    calculate_tax,
    emi,
    format_bangla,
    format_bdt,
    future_value,
)
from bd_income_tax.cli import main


# --- Ported from the bd-income-tax-calculator web app's tests ---------------

def test_general_bands_are_progressive():
    r = calculate_tax(850_000, "general")
    assert r.gross_tax == 56_250
    assert [b.income for b in r.bands] == [300_000, 175_000]


def test_category_threshold_shifts_bands():
    r = calculate_tax(950_000, "seniorCitizen")
    assert r.gross_tax == 63_750
    assert r.bands[0].lower == 425_001


def test_no_tax_at_threshold():
    r = calculate_tax(375_000)
    assert r.gross_tax == 0 and r.taxable_income == 0 and r.bands == []


def test_rebate_uses_lowest_limit():
    assert calculate_rebate(1_000_000, 500_000).amount == 30_000


def test_rebate_cap():
    r = calculate_rebate(100_000_000, 100_000_000)
    assert r.amount == 1_000_000 and r.capped


def test_final_sums_income_items():
    r = calculate({"salary": "800000", "other": "50000"})
    assert r.total_income == 850_000
    assert isinstance(r.effective_rate, float)


def test_minimum_tax():
    r = calculate({"salary": "376000"}, {"dps": "100000"})
    assert r.tax_payable == 5_000 and r.minimum_tax_applied


# --- Extra coverage --------------------------------------------------------

@pytest.mark.parametrize(
    "category,threshold",
    [("general", 375_000), ("female", 425_000), ("senior", 425_000), ("disabled", 500_000),
     ("freedom-fighter", 525_000), ("third-gender", 500_000)],
)
def test_thresholds(category, threshold):
    assert Category.parse(category).threshold == threshold
    assert calculate(threshold, category=category).tax_payable == 0
    assert calculate(threshold + 1, category=category).tax_payable == 5_000


def test_category_aliases():
    assert Category.parse("SENIOR_CITIZEN") is Category.SENIOR_CITIZEN
    assert Category.parse("freedomFighter") is Category.FREEDOM_FIGHTER
    with pytest.raises(ValueError):
        Category.parse("student")


def test_top_band():
    # 375k free, then 300k@10 + 400k@15 + 500k@20 + 2M@25 = 30k+60k+100k+500k = 690k, then 1M@30 = 300k
    r = calculate_tax(375_000 + 3_200_000 + 1_000_000)
    assert r.gross_tax == 990_000
    assert r.bands[-1].upper == math.inf and r.bands[-1].rate == 30


def test_rebate_reduces_tax():
    r = calculate({"salary": 800_000, "house_rent": 50_000}, investment=100_000)
    assert r.rebate.amount == 15_000
    assert r.tax_payable == 41_250
    assert r.net_income == 850_000 - 41_250


def test_string_amounts_with_lakh_commas():
    assert calculate("8,50,000").total_income == 850_000


def test_rejects_non_finite():
    with pytest.raises(ValueError):
        calculate(float("nan"))


def test_to_dict_is_json_safe():
    data = calculate(5_000_000).to_dict()
    json.dumps(data)
    assert data["breakdown"]["bands"][-1]["upper"] is None
    assert data["category"] == "general"


def test_formatting():
    assert format_bdt(1_234_567) == "12,34,567"
    assert format_bdt(999) == "999"
    assert format_bdt(100_000, symbol=True) == "৳1,00,000"
    assert format_bdt(-12_345_678) == "-1,23,45,678"
    assert format_bangla(1_234_567) == "১২,৩৪,৫৬৭"


def test_finance():
    assert future_value(100_000, 10_000, 0, 12) == 220_000
    assert emi(120_000, 0, 12) == 10_000
    assert emi(0, 12, 12) == 0 and emi(120_000, 12, 0) == 0
    assert math.isfinite(future_value(100_000, 10_000, 12, 60))
    assert round(emi(500_000, 12, 36), 2) == 16_607.15


def test_cli_text(capsys):
    assert main(["850000", "--investment", "100000"]) == 0
    out = capsys.readouterr().out
    assert "Tax payable        ৳41,250" in out


def test_cli_json(capsys):
    main(["400000", "50000", "-c", "female", "--json"])
    data = json.loads(capsys.readouterr().out)
    assert data["total_income"] == 450_000 and data["tax_payable"] == 5_000
