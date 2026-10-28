#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Ensure calibration cache exists
mkdir -p ~/.cache/huggingface/lerobot/calibration/teleoperators/so_leader
mkdir -p ~/.cache/huggingface/lerobot/calibration/robots/so_follower
cp -n "${REPO_ROOT}/calibration/so100_leader.json" ~/.cache/huggingface/lerobot/calibration/teleoperators/so_leader/so100_leader.json 2>/dev/null || true
cp -n "${REPO_ROOT}/calibration/so100_follower.json" ~/.cache/huggingface/lerobot/calibration/robots/so_follower/so100_follower.json 2>/dev/null || true

# Hardware Ports (persistent by-id with ttyACM fallback)
LEADER_PORT="/dev/serial/by-id/usb-1a86_USB_Single_Serial_5AE6084621-if00"
[ ! -e "${LEADER_PORT}" ] && LEADER_PORT="/dev/ttyACM1"

FOLLOWER_PORT="/dev/serial/by-id/usb-1a86_USB_Single_Serial_5AE6084008-if00"
[ ! -e "${FOLLOWER_PORT}" ] && FOLLOWER_PORT="/dev/ttyACM0"

FPS=30

echo "=========================================================="
echo " Starting LeRobot Teleoperation (1 Leader -> 1 Follower)"
echo " Leader Port:   ${LEADER_PORT}"
echo " Follower Port: ${FOLLOWER_PORT}"
echo " FPS:           ${FPS}"
echo " Press Ctrl+C in terminal to stop teleoperation."
echo "=========================================================="

lerobot-teleoperate   --robot.type="so100_follower"   --robot.id="so100_follower"   --robot.port="${FOLLOWER_PORT}"   --teleop.type="so100_leader"   --teleop.id="so100_leader"   --teleop.port="${LEADER_PORT}"   --fps="${FPS}"   --display_data=false
