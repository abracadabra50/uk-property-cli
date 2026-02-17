#!/bin/bash
# Unified property fetch dispatcher

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export CACHE_DIR="$SCRIPT_DIR/cache"

# Create cache directory
mkdir -p "$CACHE_DIR"

usage() {
    cat << EOF
UK Property CLI - Fetch and process properties

USAGE:
    ./fetch.sh <command> [options]

COMMANDS:
    all <beds>              Fetch from all portals
    espc <beds>             Fetch from ESPC only
    rightmove <beds>        Fetch from Rightmove only
    zoopla <beds>           Fetch from Zoopla only

    dedupe <files...>       Deduplicate properties
    filter <file> [opts]    Filter properties
    compare <old> <new>     Compare snapshots
    score <file>            Score and rank properties

EXAMPLES:
    # Fetch all portals (4+ beds)
    ./fetch.sh all 4

    # Deduplicate across portals
    ./fetch.sh dedupe cache/espc.json cache/rightmove.json

    # Filter to good areas, max 600k
    ./fetch.sh filter cache/all.json --use-defaults --max-price 600000

    # Score and rank properties
    ./fetch.sh score cache/all.json

EOF
    exit 1
}

if [ $# -eq 0 ]; then
    usage
fi

COMMAND="$1"
shift

case "$COMMAND" in
    all)
        BEDS="${1:-4}"
        echo "Fetching from all portals (${BEDS}+ beds)..." >&2

        # Track which portals succeeded
        FAILED=""

        python3 "$SCRIPT_DIR/parsers/espc.py" "$BEDS" > "$CACHE_DIR/espc.json" &
        PID_ESPC=$!

        python3 "$SCRIPT_DIR/parsers/rightmove.py" "$BEDS" > "$CACHE_DIR/rightmove.json" &
        PID_RM=$!

        python3 "$SCRIPT_DIR/parsers/zoopla.py" "$BEDS" > "$CACHE_DIR/zoopla.json" &
        PID_Z=$!

        # Wait for each and track failures
        wait $PID_ESPC 2>/dev/null || FAILED="$FAILED espc"
        wait $PID_RM 2>/dev/null || FAILED="$FAILED rightmove"
        wait $PID_Z 2>/dev/null || FAILED="$FAILED zoopla"

        if [ -n "$FAILED" ]; then
            echo "Warning: failed portals:$FAILED" >&2
        fi

        # Combine all valid JSON files (graceful degradation)
        python3 -c "
import json, sys, os

cache_dir = os.environ['CACHE_DIR']
all_props = []
portals_ok = []
portals_err = []

for portal in ['espc', 'rightmove', 'zoopla']:
    path = os.path.join(cache_dir, portal + '.json')
    try:
        with open(path) as f:
            data = json.load(f)
        if data.get('error'):
            portals_err.append(portal + ': ' + data['error'])
        else:
            all_props.extend(data.get('properties', []))
            portals_ok.append(portal)
    except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
        portals_err.append(portal + ': ' + str(e))

result = {
    'count': len(all_props),
    'portals_ok': portals_ok,
    'properties': all_props,
}
if portals_err:
    result['portals_failed'] = portals_err

print(json.dumps(result, indent=2))
" > "$CACHE_DIR/all.json"

        echo "Done: $(CACHE_DIR="$CACHE_DIR" python3 -c "
import json, os
d = json.load(open(os.path.join(os.environ['CACHE_DIR'], 'all.json')))
print(str(d['count']) + ' properties from ' + ', '.join(d['portals_ok']))
")" >&2
        cat "$CACHE_DIR/all.json"
        ;;

    espc|rightmove|zoopla)
        BEDS="${1:-4}"
        python3 "$SCRIPT_DIR/parsers/${COMMAND}.py" "$BEDS"
        ;;

    dedupe)
        python3 "$SCRIPT_DIR/dedupe.py" "$@"
        ;;

    filter)
        python3 "$SCRIPT_DIR/filter.py" "$@"
        ;;

    compare)
        python3 "$SCRIPT_DIR/compare.py" "$@"
        ;;

    score)
        python3 "$SCRIPT_DIR/score.py" "$@"
        ;;

    *)
        echo "Unknown command: $COMMAND"
        usage
        ;;
esac
