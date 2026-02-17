"""Tests for config.py."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config


class TestConfig:
    def test_load_config_returns_dict(self):
        # Reset cache
        config._config_cache = None
        result = config.load_config()
        assert isinstance(result, dict)
        assert "user" in result
        assert "search" in result
        assert "areas" in result

    def test_get_excluded_areas(self):
        config._config_cache = None
        areas = config.get_excluded_areas()
        assert isinstance(areas, list)
        assert len(areas) > 0

    def test_get_location(self):
        config._config_cache = None
        location = config.get_location()
        assert isinstance(location, str)
        assert location == location.lower()

    def test_get_rightmove_region(self):
        config._config_cache = None
        region = config.get_rightmove_region()
        # With Edinburgh config, should return the Edinburgh region
        if region:
            assert "REGION" in region

    def test_get_dedup_threshold(self):
        config._config_cache = None
        threshold = config.get_dedup_threshold()
        assert 0 < threshold <= 1.0

    def test_merge_dict(self):
        base = {"a": 1, "b": {"c": 2, "d": 3}}
        override = {"b": {"c": 99}}
        config._merge_dict(base, override)
        assert base["a"] == 1
        assert base["b"]["c"] == 99
        assert base["b"]["d"] == 3  # Not overwritten
