#!/bin/bash
# Property fetcher - modular portal data fetcher

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORTAL="${1:-espc}"
BEDS="${2:-4}"

fetch_portal() {
  local portal=$1
  local parser="${SCRIPT_DIR}/parsers/${portal}.py"
  
  if [ -f "$parser" ]; then
    python3 "$parser" "$BEDS"
  else
    echo "{\"portal\":\"${portal}\",\"error\":\"Parser not implemented\"}" >&2
    return 1
  fi
}

case $PORTAL in
  espc|rightmove|zoopla)
    fetch_portal "$PORTAL"
    ;;
  all)
    # Fetch from all portals and combine
    echo '{"portals":['
    first=true
    for p in espc rightmove zoopla; do
      if [ "$first" = false ]; then echo ','; fi
      fetch_portal "$p" || true
      first=false
    done
    echo ']}'
    ;;
  *)
    echo "{\"error\":\"Unknown portal: $PORTAL\"}" >&2
    exit 1
    ;;
esac
