"""Tests for compare.py."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from compare import compare_snapshots


YESTERDAY = [
    {"id": "1", "address": "10 High St", "price": 500000},
    {"id": "2", "address": "5 Oak Rd", "price": 300000},
    {"id": "3", "address": "20 Park Ave", "price": 400000},
]

TODAY = [
    {"id": "1", "address": "10 High St", "price": 500000},  # Unchanged
    {"id": "2", "address": "5 Oak Rd", "price": 280000},    # Price drop
    {"id": "4", "address": "15 New Lane", "price": 350000}, # New listing
]


class TestCompareSnapshots:
    def test_new_listings(self):
        result = compare_snapshots(YESTERDAY, TODAY)
        assert result["stats"]["new_count"] == 1
        assert result["new_listings"][0]["id"] == "4"

    def test_removed_listings(self):
        result = compare_snapshots(YESTERDAY, TODAY)
        assert result["stats"]["removed_count"] == 1
        assert result["removed_listings"][0]["id"] == "3"

    def test_price_changes(self):
        result = compare_snapshots(YESTERDAY, TODAY)
        assert result["stats"]["price_changes_count"] == 1
        change = result["price_changes"][0]
        assert change["old_price"] == 300000
        assert change["new_price"] == 280000
        assert change["change"] == -20000
        assert change["change_percent"] == -6.7

    def test_price_drops_count(self):
        result = compare_snapshots(YESTERDAY, TODAY)
        assert result["stats"]["price_drops"] == 1
        assert result["stats"]["price_increases"] == 0

    def test_empty_snapshots(self):
        result = compare_snapshots([], [])
        assert result["stats"]["new_count"] == 0
        assert result["stats"]["removed_count"] == 0

    def test_counts(self):
        result = compare_snapshots(YESTERDAY, TODAY)
        assert result["stats"]["yesterday_count"] == 3
        assert result["stats"]["today_count"] == 3

    def test_price_zero_ignored(self):
        """Properties with price=0 should not appear in price changes."""
        yesterday = [{"id": "1", "address": "10 High St", "price": 0}]
        today = [{"id": "1", "address": "10 High St", "price": 500000}]
        result = compare_snapshots(yesterday, today)
        assert result["stats"]["price_changes_count"] == 0
