#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT="${1:-8080}"

echo "Starting LeRobot Camera Live Stream & Focus Server on port ${PORT}..."
python3 "${SCRIPT_DIR}/view_camera.py" --port "${PORT}"
