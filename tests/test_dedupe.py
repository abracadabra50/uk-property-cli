"""Tests for dedupe.py."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dedupe import addresses_match, deduplicate, merge_property_data, normalize_address


class TestNormalizeAddress:
    def test_lowercase(self):
        assert normalize_address("10 HIGH STREET") == "10 high st"

    def test_abbreviations(self):
        assert normalize_address("10 Main Road") == "10 main rd"
        assert normalize_address("5 Oak Avenue") == "5 oak ave"
        assert normalize_address("3 Park Drive") == "3 park dr"

    def test_remove_punctuation(self):
        assert normalize_address("10 High St., Edinburgh") == "10 high st edinburgh"

    def test_normalize_whitespace(self):
        assert normalize_address("10  High   Street") == "10 high st"


class TestAddressesMatch:
    def test_identical(self):
        assert addresses_match("10 High Street, Edinburgh", "10 High Street, Edinburgh")

    def test_slight_variation(self):
        assert addresses_match("10 High Street, Edinburgh", "10 High St, Edinburgh")

    def test_different_addresses(self):
        assert not addresses_match("10 High Street, Edinburgh", "5 Oak Road, Glasgow")

    def test_custom_threshold(self):
        assert addresses_match("10 High St", "10 High Street", threshold=0.7)


class TestMergePropertyData:
    def test_empty_list(self):
        assert merge_property_data([]) == {}

    def test_merge_basics(self):
        props = [
            {
                "id": "1", "portal": "rightmove", "url": "https://rm.co.uk/1",
                "price": 500000, "beds": 4, "baths": 2, "address": "10 High St",
                "images": ["img1.jpg"], "image_url": "img1.jpg",
                "features": ["garden"], "description": "Nice house",
            },
            {
                "id": "2", "portal": "espc", "url": "https://espc.com/2",
                "price": 495000, "beds": 4, "baths": 2, "address": "10 High Street",
                "images": ["img2.jpg"], "image_url": "img2.jpg",
                "features": ["parking"], "description": "A very nice detached house",
            },
        ]
        merged = merge_property_data(props)

        assert merged["price"] == 495000  # Lowest
        assert set(merged["portals"]) == {"rightmove", "espc"}
        assert "rightmove" in merged["urls"]
        assert "espc" in merged["urls"]
        assert len(merged["images"]) == 2
        assert set(merged["features"]) == {"garden", "parking"}
        assert merged["description"] == "A very nice detached house"  # Longest


class TestDeduplicate:
    def test_no_duplicates(self):
        props = [
            {"id": "1", "address": "10 High Street, Edinburgh EH10", "postcode": "EH10", "portal": "rightmove"},
            {"id": "2", "address": "5 Oak Road, Glasgow G12", "postcode": "G12", "portal": "rightmove"},
        ]
        result = deduplicate(props)
        assert len(result) == 2

    def test_finds_duplicates(self):
        props = [
            {
                "id": "1", "address": "10 High Street, Edinburgh, EH10 4BF", "postcode": "EH10",
                "portal": "rightmove", "url": "https://rm/1", "price": 500000,
                "beds": 4, "baths": 2, "images": [], "image_url": "",
                "features": [], "description": "",
            },
            {
                "id": "2", "address": "10 High St, Edinburgh, EH10 4BF", "postcode": "EH10",
                "portal": "espc", "url": "https://espc/2", "price": 495000,
                "beds": 4, "baths": 2, "images": [], "image_url": "",
                "features": [], "description": "",
            },
        ]
        result = deduplicate(props)
        assert len(result) == 1
        assert result[0]["price"] == 495000

    def test_different_postcodes_not_merged(self):
        props = [
            {"id": "1", "address": "10 High Street, Edinburgh EH10 4BF", "postcode": "EH10", "portal": "rightmove"},
            {"id": "2", "address": "10 High Street, Glasgow G12 8AP", "postcode": "G12", "portal": "rightmove"},
        ]
        result = deduplicate(props)
        assert len(result) == 2

    def test_empty_list(self):
        result = deduplicate([])
        assert result == []
