#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
eval "$(python3 "${SCRIPT_DIR}/config_helper.py" --export-env)"

echo "=========================================================="
echo " Calibrating SO-100 Follower Arm on ${FOLLOWER_PORT}"
echo " 1. Move arm to middle of its range of motion, press Enter"
echo " 2. Move joints sequentially through full range of motion"
echo "=========================================================="

lerobot-calibrate   --robot.type="${FOLLOWER_TYPE}"   --robot.id="${FOLLOWER_ID}"   --robot.port="${FOLLOWER_PORT}"

# Backup new calibration to repo
cp ~/.cache/huggingface/lerobot/calibration/robots/so_follower/so100_follower.json "${SCRIPT_DIR}/../calibration/so100_follower.json" 2>/dev/null || true
echo "Calibration saved to repo in calibration/so100_follower.json"
