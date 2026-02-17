"""Tests for parsers.base shared utilities."""

import sys
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from parsers.base import (
    Property,
    categorize,
    extract_postcode,
    extract_area,
    is_bad_area,
    now_iso,
    parse_price,
    validate_beds,
)


class TestParsePrice:
    def test_standard_format(self):
        assert parse_price("£550,000") == 550000

    def test_plain_digits(self):
        assert parse_price("550000") == 550000

    def test_with_commas(self):
        assert parse_price("1,250,000") == 1250000

    def test_empty_string(self):
        assert parse_price("") == 0

    def test_none(self):
        assert parse_price(None) == 0

    def test_no_digits(self):
        assert parse_price("Price on application") == 0

    def test_with_qualifier(self):
        assert parse_price("Offers over £450,000") == 450000


class TestCategorize:
    def test_investment(self):
        assert categorize(200000, 2) == "investment"

    def test_family(self):
        assert categorize(500000, 4) == "family"

    def test_other(self):
        assert categorize(300000, 2) == "other"

    def test_boundary_investment(self):
        assert categorize(249999, 4) == "investment"

    def test_boundary_family(self):
        assert categorize(250000, 4) == "family"

    def test_custom_thresholds(self):
        assert categorize(300000, 3, investment_threshold=350000) == "investment"
        assert categorize(400000, 3, family_min_beds=3) == "family"


class TestIsBadArea:
    def test_matches(self):
        excluded = ["Moredun", "Niddrie", "Wester Hailes"]
        assert is_bad_area("123 High St, Moredun, Edinburgh", excluded) is True
        assert is_bad_area("5 Niddrie Mains Rd", excluded) is True

    def test_no_match(self):
        excluded = ["Moredun", "Niddrie"]
        assert is_bad_area("10 Morningside Road, Edinburgh", excluded) is False

    def test_case_insensitive(self):
        excluded = ["Moredun"]
        assert is_bad_area("123 MOREDUN ROAD", excluded) is True

    def test_empty_excluded(self):
        assert is_bad_area("10 Any Street", []) is False


class TestExtractPostcode:
    def test_edinburgh(self):
        assert extract_postcode("10 Morningside Road, Edinburgh EH10 4BF") == "EH10 4BF"

    def test_manchester(self):
        assert extract_postcode("5 Oak Road, Didsbury, Manchester M20 6JH") == "M20 6JH"

    def test_london_sw(self):
        assert extract_postcode("10 King's Road, London SW3 4ND") == "SW3 4ND"

    def test_glasgow(self):
        assert extract_postcode("20 Byres Road, Glasgow G12 8AP") == "G12 8AP"

    def test_no_postcode(self):
        assert extract_postcode("Some Street, Some Town") == ""

    def test_area_only(self):
        # When only postcode area is present (e.g., EH10 without full code)
        result = extract_postcode("Property in EH10")
        assert result.startswith("EH10")


class TestExtractArea:
    def test_with_comma(self):
        assert extract_area("10 High St, Morningside, Edinburgh") == "Edinburgh"

    def test_no_comma(self):
        assert extract_area("10 High St Edinburgh") == ""


class TestValidateBeds:
    def test_valid(self):
        assert validate_beds("4") == 4

    def test_none(self):
        assert validate_beds(None) == 4

    def test_invalid_string(self):
        assert validate_beds("abc") == 4

    def test_too_high(self):
        assert validate_beds("25") == 4

    def test_negative(self):
        assert validate_beds("-1") == 4

    def test_zero(self):
        assert validate_beds("0") == 0


class TestNowIso:
    def test_format(self):
        result = now_iso()
        assert result.endswith("Z")
        assert "T" in result


class TestProperty:
    def test_to_dict(self):
        prop = Property(
            id="123", title="Test", price=500000, price_text="£500,000",
            beds=4, baths=2, property_type="house", address="10 High St",
            area="Edinburgh", postcode="EH10 4BF", description="Nice house",
            url="https://example.com", image_url="https://img.com/1.jpg",
            images=["https://img.com/1.jpg"], features=["garden"],
            portal="rightmove", category="family",
        )
        d = prop.to_dict()
        assert d["id"] == "123"
        assert d["price"] == 500000
        assert d["portal"] == "rightmove"
        assert isinstance(d, dict)
