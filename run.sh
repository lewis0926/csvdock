#!/bin/bash
set -euo pipefail

CONFIG_PKL="${2:-config/main.pkl}"
CONFIG_JSON="config.json"

echo "Generating $CONFIG_JSON from $CONFIG_PKL..."
pkl eval "$CONFIG_PKL" -f json -o "$CONFIG_JSON"

python main.py "$CONFIG_JSON" "$1" credentials.json
