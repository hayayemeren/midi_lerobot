#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
eval "$(python3 "${SCRIPT_DIR}/config_helper.py" --export-env)"

echo "=========================================================="
echo " Calibrating SO-100 Leader Arm on ${LEADER_PORT}"
echo " 1. Move arm to middle of its range of motion, press Enter"
echo " 2. Move joints sequentially through full range of motion"
echo "=========================================================="

lerobot-calibrate   --teleop.type="${LEADER_TYPE}"   --teleop.id="${LEADER_ID}"   --teleop.port="${LEADER_PORT}"

# Backup new calibration to repo
cp ~/.cache/huggingface/lerobot/calibration/teleoperators/so_leader/so100_leader.json "${SCRIPT_DIR}/../calibration/so100_leader.json" 2>/dev/null || true
echo "Calibration saved to repo in calibration/so100_leader.json"
