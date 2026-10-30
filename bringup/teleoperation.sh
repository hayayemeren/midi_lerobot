#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Load configuration from bringup/config.json
eval "$(python3 "${SCRIPT_DIR}/config_helper.py" --export-env)"

# Ensure calibration cache exists
mkdir -p ~/.cache/huggingface/lerobot/calibration/teleoperators/so_leader
mkdir -p ~/.cache/huggingface/lerobot/calibration/robots/so_follower
cp -n "${REPO_ROOT}/calibration/so100_leader.json" ~/.cache/huggingface/lerobot/calibration/teleoperators/so_leader/so100_leader.json 2>/dev/null || true
cp -n "${REPO_ROOT}/calibration/so100_follower.json" ~/.cache/huggingface/lerobot/calibration/robots/so_follower/so100_follower.json 2>/dev/null || true

echo "=========================================================="
echo " Starting LeRobot Teleoperation (1 Leader -> 1 Follower)"
echo " Configuration: ${SCRIPT_DIR}/config.json"
echo " Leader Port:   ${LEADER_PORT}"
echo " Follower Port: ${FOLLOWER_PORT}"
echo " FPS:           ${FPS}"
echo " Press Ctrl+C in terminal to stop teleoperation."
echo "=========================================================="

lerobot-teleoperate   --robot.type="${FOLLOWER_TYPE}"   --robot.id="${FOLLOWER_ID}"   --robot.port="${FOLLOWER_PORT}"   --teleop.type="${LEADER_TYPE}"   --teleop.id="${LEADER_ID}"   --teleop.port="${LEADER_PORT}"   --fps="${FPS}"   --display_data=false
