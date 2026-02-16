#!/bin/bash
# Unified property fetch dispatcher

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CACHE_DIR="$SCRIPT_DIR/cache"

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
    
EXAMPLES:
    # Fetch all portals (4+ beds)
    ./fetch.sh all 4
    
    # Deduplicate across portals
    ./fetch.sh dedupe cache/espc.json cache/rightmove.json
    
    # Filter to good areas, max £600k
    ./fetch.sh filter cache/all.json --use-defaults --max-price 600000
    
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
        
        python3 "$SCRIPT_DIR/parsers/espc.py" "$BEDS" > "$CACHE_DIR/espc.json" 2>/dev/null &
        PID_ESPC=$!
        
        python3 "$SCRIPT_DIR/parsers/rightmove.py" "$BEDS" > "$CACHE_DIR/rightmove.json" 2>/dev/null &
        PID_RM=$!
        
        python3 "$SCRIPT_DIR/parsers/zoopla.py" "$BEDS" > "$CACHE_DIR/zoopla.json" 2>/dev/null &
        PID_Z=$!
        
        # Wait for all
        wait $PID_ESPC $PID_RM $PID_Z
        
        echo "✅ All portals fetched" >&2
        
        # Combine into single file
        python3 -c "
import json
with open('$CACHE_DIR/espc.json') as f: espc = json.load(f)
with open('$CACHE_DIR/rightmove.json') as f: rm = json.load(f)
with open('$CACHE_DIR/zoopla.json') as f: z = json.load(f)

all_props = espc['properties'] + rm['properties'] + z['properties']
print(json.dumps({'properties': all_props}, indent=2))
" > "$CACHE_DIR/all.json"
        
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
    
    *)
        echo "Unknown command: $COMMAND"
        usage
        ;;
esac
