#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ARM="${1:-}"

if [ -n "$ARM" ]; then
    python3 "${SCRIPT_DIR}/calibrate_arm.py" --arm "$ARM"
else
    python3 "${SCRIPT_DIR}/calibrate_arm.py"
fi
