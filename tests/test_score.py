"""Tests for score.py."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from score import score_property


DEFAULT_SCORING = {
    "area_weights": {"premium": 30, "excellent": 25, "good": 20},
    "price_ideal_min": 400000,
    "price_ideal_max": 550000,
    "prefer_images": True,
    "prefer_multiple_portals": True,
}


class TestScoreProperty:
    def test_premium_area(self):
        prop = {"address": "10 High St, EH10 4BF", "postcode": "EH10", "price": 500000, "beds": 4, "images": [], "portals": []}
        score = score_property(prop, DEFAULT_SCORING, desired=["EH10", "EH4"], premium=["EH10"])
        assert score >= 30  # Premium area weight

    def test_desired_area(self):
        prop = {"address": "5 Oak Rd, EH4 1AA", "postcode": "EH4", "price": 500000, "beds": 4, "images": [], "portals": []}
        score = score_property(prop, DEFAULT_SCORING, desired=["EH4"], premium=["EH10"])
        assert score >= 20  # Good area weight

    def test_ideal_price_range(self):
        prop = {"address": "10 High St", "postcode": "", "price": 450000, "beds": 3, "images": [], "portals": []}
        score_ideal = score_property(prop, DEFAULT_SCORING, desired=[], premium=[])

        prop_expensive = {"address": "10 High St", "postcode": "", "price": 900000, "beds": 3, "images": [], "portals": []}
        score_expensive = score_property(prop_expensive, DEFAULT_SCORING, desired=[], premium=[])

        assert score_ideal > score_expensive

    def test_image_bonus(self):
        prop_with_images = {"address": "10 High St", "postcode": "", "price": 0, "beds": 3, "images": ["a.jpg", "b.jpg", "c.jpg"], "portals": []}
        prop_no_images = {"address": "10 High St", "postcode": "", "price": 0, "beds": 3, "images": [], "portals": []}

        score_with = score_property(prop_with_images, DEFAULT_SCORING, desired=[], premium=[])
        score_without = score_property(prop_no_images, DEFAULT_SCORING, desired=[], premium=[])

        assert score_with > score_without

    def test_multi_portal_bonus(self):
        prop_multi = {"address": "10 High St", "postcode": "", "price": 0, "beds": 3, "images": [], "portals": ["rightmove", "espc"]}
        prop_single = {"address": "10 High St", "postcode": "", "price": 0, "beds": 3, "images": [], "portals": ["rightmove"]}

        score_multi = score_property(prop_multi, DEFAULT_SCORING, desired=[], premium=[])
        score_single = score_property(prop_single, DEFAULT_SCORING, desired=[], premium=[])

        assert score_multi > score_single

    def test_bedroom_bonus(self):
        prop_5bed = {"address": "10 High St", "postcode": "", "price": 0, "beds": 5, "images": [], "portals": []}
        prop_2bed = {"address": "10 High St", "postcode": "", "price": 0, "beds": 2, "images": [], "portals": []}

        score_5 = score_property(prop_5bed, DEFAULT_SCORING, desired=[], premium=[])
        score_2 = score_property(prop_2bed, DEFAULT_SCORING, desired=[], premium=[])

        assert score_5 > score_2
