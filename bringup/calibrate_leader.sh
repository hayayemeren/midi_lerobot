#!/bin/bash
set -e

PORT="/dev/serial/by-id/usb-1a86_USB_Single_Serial_5AE6084621-if00"
[ ! -e "${PORT}" ] && PORT="/dev/ttyACM1"

echo "=========================================================="
echo " Calibrating SO-100 Leader Arm on ${PORT}"
echo " 1. Move arm to middle of its range of motion, press Enter"
echo " 2. Move joints sequentially through full range of motion"
echo "=========================================================="

lerobot-calibrate   --teleop.type="so100_leader"   --teleop.id="so100_leader"   --teleop.port="${PORT}"

# Backup new calibration to repo
cp ~/.cache/huggingface/lerobot/calibration/teleoperators/so_leader/so100_leader.json "$(dirname "$0")/../calibration/so100_leader.json" 2>/dev/null || true
echo "Calibration saved to repo in calibration/so100_leader.json"
