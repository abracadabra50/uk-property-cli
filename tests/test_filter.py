"""Tests for filter.py."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from filter import filter_properties

SAMPLE_PROPERTIES = [
    {"id": "1", "address": "10 High St, EH10 4BF", "postcode": "EH10", "price": 500000, "beds": 4, "category": "family"},
    {"id": "2", "address": "5 Oak Rd, EH4 1AA", "postcode": "EH4", "price": 200000, "beds": 2, "category": "investment"},
    {"id": "3", "address": "3 Niddrie Mains, EH17 7AA", "postcode": "EH17", "price": 150000, "beds": 3, "category": "investment"},
    {"id": "4", "address": "20 Park Ave, M20 6JH", "postcode": "M20", "price": 350000, "beds": 3, "category": "other"},
    {"id": "5", "address": "1 Queen St, EH10 5AA", "postcode": "EH10", "price": 700000, "beds": 5, "category": "family"},
]


class TestFilterProperties:
    def test_no_filters(self):
        result = filter_properties(SAMPLE_PROPERTIES)
        assert len(result) == 5

    def test_filter_by_area(self):
        result = filter_properties(SAMPLE_PROPERTIES, areas=["EH10"])
        assert len(result) == 2
        assert all("EH10" in p["postcode"] for p in result)

    def test_filter_exclude(self):
        result = filter_properties(SAMPLE_PROPERTIES, exclude=["EH17", "Niddrie"])
        assert len(result) == 4
        assert not any("EH17" in p["postcode"] for p in result)

    def test_filter_min_price(self):
        result = filter_properties(SAMPLE_PROPERTIES, min_price=300000)
        assert len(result) == 3
        assert all(p["price"] >= 300000 for p in result)

    def test_filter_max_price(self):
        result = filter_properties(SAMPLE_PROPERTIES, max_price=400000)
        assert len(result) == 3
        assert all(p["price"] <= 400000 for p in result)

    def test_filter_min_beds(self):
        result = filter_properties(SAMPLE_PROPERTIES, min_beds=4)
        assert len(result) == 2
        assert all(p["beds"] >= 4 for p in result)

    def test_filter_category(self):
        result = filter_properties(SAMPLE_PROPERTIES, category="family")
        assert len(result) == 2
        assert all(p["category"] == "family" for p in result)

    def test_combined_filters(self):
        result = filter_properties(
            SAMPLE_PROPERTIES,
            areas=["EH10"],
            max_price=600000,
            min_beds=4,
        )
        assert len(result) == 1
        assert result[0]["id"] == "1"
