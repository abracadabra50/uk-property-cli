#!/usr/bin/env python3
"""
Interactive setup for UK Property CLI preferences.

Usage:
    python3 setup.py
"""

import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).parent
PREFERENCES_FILE = SCRIPT_DIR / 'preferences.json'


# Common UK areas by city
AREA_PRESETS = {
    'edinburgh': {
        'desired': ['EH10', 'EH12', 'EH13', 'EH14', 'EH4', 'EH9', 'EH3', 'EH15'],
        'excluded': ['EH17', 'EH29', 'Moredun', 'Niddrie', 'Wester Hailes', 'Sighthill', 'Muirhouse', 'Pilton', 'Granton'],
        'premium': ['EH10', 'EH9', 'EH3']
    },
    'manchester': {
        'desired': ['M20', 'M21', 'WA14', 'WA15', 'M33'],
        'excluded': ['M14', 'M13'],
        'premium': ['M20', 'WA14', 'WA15']
    },
    'london': {
        'desired': ['SW', 'W', 'NW', 'SE'],
        'excluded': [],
        'premium': ['SW3', 'SW7', 'W8', 'NW3']
    },
    'custom': {
        'desired': [],
        'excluded': [],
        'premium': []
    }
}


def prompt(question: str, default: str = None) -> str:
    """Prompt user for input."""
    if default:
        response = input(f"{question} [{default}]: ").strip()
        return response if response else default
    else:
        return input(f"{question}: ").strip()


def prompt_int(question: str, default: int = None) -> int:
    """Prompt user for integer."""
    while True:
        response = prompt(question, str(default) if default else None)
        try:
            return int(response) if response else default
        except ValueError:
            print("Please enter a valid number.")


def prompt_yes_no(question: str, default: bool = True) -> bool:
    """Prompt user for yes/no."""
    default_str = "Y/n" if default else "y/N"
    response = prompt(f"{question} ({default_str})", "").lower()
    
    if not response:
        return default
    return response in ['y', 'yes']


def setup_user_info():
    """Setup user information."""
    print("\n=== User Information ===\n")
    
    name = prompt("Your name (for reference)", "Property Searcher")
    location = prompt("Your city/location", "Edinburgh")
    
    return {
        'name': name,
        'location': location
    }


def setup_search_criteria():
    """Setup search criteria."""
    print("\n=== Search Criteria ===\n")
    
    min_beds = prompt_int("Minimum bedrooms", 4)
    max_beds = prompt_int("Maximum bedrooms (leave blank for no limit)", None)
    
    min_price = prompt_int("Minimum price (leave blank for no limit)", None)
    max_price = prompt_int("Maximum price", 600000)
    
    print("\nProperty types (comma-separated):")
    print("Examples: house, detached, semi-detached, terraced, flat, bungalow")
    types_input = prompt("Property types", "house,detached,semi-detached")
    property_types = [t.strip() for t in types_input.split(',')]
    
    return {
        'min_beds': min_beds,
        'max_beds': max_beds,
        'min_price': min_price,
        'max_price': max_price,
        'property_types': property_types
    }


def setup_areas():
    """Setup area preferences."""
    print("\n=== Area Preferences ===\n")
    
    print("Choose a preset or configure custom areas:")
    print("1. Edinburgh (EH10, EH12, EH4, etc.)")
    print("2. Manchester (M20, M21, Didsbury, etc.)")
    print("3. London (SW, W, NW postcodes)")
    print("4. Custom (configure manually)")
    
    choice = prompt("Choice [1-4]", "1")
    
    preset_map = {
        '1': 'edinburgh',
        '2': 'manchester',
        '3': 'london',
        '4': 'custom'
    }
    
    preset = AREA_PRESETS.get(preset_map.get(choice, 'edinburgh'))
    
    if choice == '4':
        print("\nEnter desired areas/postcodes (comma-separated):")
        print("Examples: EH10,EH12,Morningside or M20,M21,Didsbury")
        desired_input = prompt("Desired areas")
        preset['desired'] = [a.strip() for a in desired_input.split(',')]
        
        print("\nEnter areas to EXCLUDE (comma-separated):")
        print("Examples: Niddrie,Moredun or M13,M14")
        excluded_input = prompt("Excluded areas", "")
        preset['excluded'] = [a.strip() for a in excluded_input.split(',')] if excluded_input else []
        
        print("\nEnter PREMIUM areas (comma-separated):")
        print("These get highest scoring priority")
        premium_input = prompt("Premium areas", "")
        preset['premium'] = [a.strip() for a in premium_input.split(',')] if premium_input else []
    else:
        print(f"\nUsing {preset_map.get(choice)} preset:")
        print(f"Desired areas: {', '.join(preset['desired'][:5])}...")
        print(f"Excluded areas: {', '.join(preset['excluded'][:5])}...")
        
        customize = prompt_yes_no("Customize these areas?", False)
        if customize:
            print("\nAdd more desired areas (comma-separated, or leave blank):")
            more_desired = prompt("Additional areas", "")
            if more_desired:
                preset['desired'].extend([a.strip() for a in more_desired.split(',')])
            
            print("\nAdd more excluded areas (comma-separated, or leave blank):")
            more_excluded = prompt("Additional exclusions", "")
            if more_excluded:
                preset['excluded'].extend([a.strip() for a in more_excluded.split(',')])
    
    return preset


def setup_scoring():
    """Setup scoring preferences."""
    print("\n=== Scoring Preferences ===\n")
    
    print("Scoring weights (higher = more important):")
    premium_weight = prompt_int("Premium area weight", 30)
    excellent_weight = prompt_int("Excellent area weight", 25)
    good_weight = prompt_int("Good area weight", 20)
    
    print("\nIdeal price range for scoring:")
    price_ideal_min = prompt_int("Ideal minimum price", 400000)
    price_ideal_max = prompt_int("Ideal maximum price", 550000)
    
    prefer_images = prompt_yes_no("Prefer properties with images?", True)
    prefer_multiple = prompt_yes_no("Prefer properties on multiple portals?", True)
    
    return {
        'area_weights': {
            'premium': premium_weight,
            'excellent': excellent_weight,
            'good': good_weight
        },
        'price_ideal_min': price_ideal_min,
        'price_ideal_max': price_ideal_max,
        'prefer_images': prefer_images,
        'prefer_multiple_portals': prefer_multiple
    }


def setup_deduplication():
    """Setup deduplication preferences."""
    print("\n=== Deduplication ===\n")
    
    print("Properties often appear on multiple portals (Rightmove + Zoopla + ESPC).")
    print("Deduplication merges these into single entries.")
    
    enabled = prompt_yes_no("Enable automatic deduplication?", True)
    
    if enabled:
        print("\nSimilarity threshold (0.0 - 1.0):")
        print("0.85 = 85% similar addresses match (recommended)")
        print("0.90 = stricter matching (fewer duplicates found)")
        print("0.80 = looser matching (more duplicates found)")
        threshold = float(prompt("Threshold", "0.85"))
    else:
        threshold = 0.85
    
    return {
        'enabled': enabled,
        'threshold': threshold
    }


def setup_briefing():
    """Setup daily briefing preferences."""
    print("\n=== Daily Briefing ===\n")
    
    enabled = prompt_yes_no("Enable daily briefings?", True)
    
    if enabled:
        print("\nBriefing schedule (cron format):")
        print("0 9 * * * = 9am daily")
        print("0 7 * * 1-5 = 7am weekdays")
        schedule = prompt("Schedule", "0 9 * * *")
        
        include_price_changes = prompt_yes_no("Include price changes?", True)
        include_new_only = prompt_yes_no("Show only NEW listings (vs all matching)?", False)
        max_results = prompt_int("Maximum results in briefing", 10)
    else:
        schedule = "0 9 * * *"
        include_price_changes = True
        include_new_only = False
        max_results = 10
    
    return {
        'enabled': enabled,
        'schedule': schedule,
        'include_price_changes': include_price_changes,
        'include_new_only': include_new_only,
        'max_results': max_results
    }


def main():
    print("=" * 60)
    print("UK Property CLI - Setup")
    print("=" * 60)
    print("\nThis will configure your property search preferences.")
    print("You can edit preferences.json manually later.\n")
    
    # Check if preferences exist
    if PREFERENCES_FILE.exists():
        print(f"⚠️  Existing preferences found at {PREFERENCES_FILE}")
        if not prompt_yes_no("Overwrite existing preferences?", False):
            print("Setup cancelled.")
            sys.exit(0)
    
    # Build preferences
    preferences = {
        'user': setup_user_info(),
        'search': setup_search_criteria(),
        'areas': setup_areas(),
        'scoring': setup_scoring(),
        'deduplication': setup_deduplication(),
        'briefing': setup_briefing()
    }
    
    # Save
    print("\n=== Summary ===\n")
    print(json.dumps(preferences, indent=2))
    
    print(f"\n\nSaving preferences to {PREFERENCES_FILE}...")
    
    with open(PREFERENCES_FILE, 'w') as f:
        json.dump(preferences, f, indent=2)
    
    print("\n✅ Setup complete!\n")
    print("Next steps:")
    print(f"  1. Edit {PREFERENCES_FILE} if needed")
    print("  2. Run: ./fetch.sh briefing")
    print("  3. Or use individual tools with --config flag")
    print()


if __name__ == '__main__':
    main()
