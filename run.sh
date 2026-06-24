#!/bin/bash
set -euo pipefail

usage() {
  echo "Usage: ./run.sh <data.csv> <config.pkl>"
  echo ""
  echo "Available configs:"
  for f in config/*.pkl; do
    echo "  $f"
  done
  exit 1
}

if [[ $# -lt 2 ]]; then
  usage
fi

CSV_FILE="$1"
CONFIG_PKL="$2"
CONFIG_JSON="config.json"

echo "Generating $CONFIG_JSON from $CONFIG_PKL..."
pkl eval "$CONFIG_PKL" -f json -o "$CONFIG_JSON"

python main.py "$CONFIG_JSON" "$CSV_FILE" credentials.json
