"""
Shared utilities for property parsers.

Eliminates duplication of BAD_AREAS, categorize(), parse_price(), etc.
across espc.py, rightmove.py, and zoopla.py.
"""

import json
import re
import subprocess
import sys
import time
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# UK-wide postcode regex (matches EH10, SW1A, M1, G12, etc.)
UK_POSTCODE_RE = re.compile(r'([A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2})', re.IGNORECASE)
UK_POSTCODE_AREA_RE = re.compile(r'([A-Z]{1,2}\d+)', re.IGNORECASE)


@dataclass
class Property:
    """Normalized property data across all portals."""
    id: str
    title: str
    price: int
    price_text: str
    beds: int
    baths: int
    property_type: str
    address: str
    area: str
    postcode: str
    description: str
    url: str
    image_url: str
    images: List[str]
    features: List[str]
    portal: str
    category: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PortalResult:
    """Standard output envelope for all parsers."""
    portal: str
    fetched_at: str
    count: int
    properties: List[Dict[str, Any]]
    error: Optional[str] = None
    note: Optional[str] = None

    def to_json(self, indent: int = 2) -> str:
        d = {
            "portal": self.portal,
            "fetched_at": self.fetched_at,
            "count": self.count,
            "properties": self.properties,
        }
        if self.error:
            d["error"] = self.error
        if self.note:
            d["note"] = self.note
        return json.dumps(d, indent=indent)


def now_iso() -> str:
    """Return current UTC time in ISO 8601 format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def is_bad_area(address: str, excluded_areas: List[str]) -> bool:
    """Check if property is in an excluded area."""
    addr_lower = address.lower()
    return any(bad.lower() in addr_lower for bad in excluded_areas)


def categorize(price: int, beds: int, investment_threshold: int = 250000, family_min_beds: int = 4) -> str:
    """Categorize property as investment, family, or other."""
    if price < investment_threshold:
        return "investment"
    elif beds >= family_min_beds:
        return "family"
    else:
        return "other"


def parse_price(text: str) -> int:
    """Extract numeric price from text like '£550,000' or '550000'."""
    if not text:
        return 0
    digits = re.sub(r'[^\d]', '', str(text))
    return int(digits) if digits else 0


def extract_postcode(address: str) -> str:
    """Extract UK postcode from an address string."""
    match = UK_POSTCODE_RE.search(address.upper())
    if match:
        return match.group(1).strip()
    # Fall back to postcode area only (e.g., EH10 without full postcode)
    match = UK_POSTCODE_AREA_RE.search(address.upper())
    if match:
        return match.group(1).strip()
    return ""


def extract_area(address: str) -> str:
    """Extract area name from address (last part after comma)."""
    if ',' in address:
        return address.split(',')[-1].strip()
    return ""


def fetch_url(url: str, timeout: int = 15, retries: int = 3) -> Optional[str]:
    """
    Fetch a URL using curl with retries and error handling.

    Returns the response body, or None on failure.
    """
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

    for attempt in range(retries):
        try:
            result = subprocess.run(
                ["curl", "-s", "-f", "-H", f"User-Agent: {user_agent}", url],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout
            print(f"curl failed (attempt {attempt + 1}/{retries}): exit code {result.returncode}", file=sys.stderr)
        except subprocess.TimeoutExpired:
            print(f"Request timed out (attempt {attempt + 1}/{retries})", file=sys.stderr)
        except Exception as e:
            print(f"Fetch error (attempt {attempt + 1}/{retries}): {e}", file=sys.stderr)

        if attempt < retries - 1:
            wait = 2 ** attempt
            print(f"Retrying in {wait}s...", file=sys.stderr)
            time.sleep(wait)

    return None


def validate_beds(beds_arg: Optional[str]) -> int:
    """Validate and return bedroom count from CLI argument."""
    if beds_arg is None:
        return 4
    try:
        beds = int(beds_arg)
        if beds < 0 or beds > 20:
            print(f"Invalid beds value: {beds}. Using default 4.", file=sys.stderr)
            return 4
        return beds
    except ValueError:
        print(f"Invalid beds value: {beds_arg!r}. Using default 4.", file=sys.stderr)
        return 4


def build_result(portal: str, properties: List[Property], error: Optional[str] = None, note: Optional[str] = None) -> PortalResult:
    """Build a standard PortalResult from a list of Property objects."""
    return PortalResult(
        portal=portal,
        fetched_at=now_iso(),
        count=len(properties),
        properties=[p.to_dict() for p in properties],
        error=error,
        note=note,
    )
