#!/bin/bash
set -e

PORT="/dev/serial/by-id/usb-1a86_USB_Single_Serial_5AE6084008-if00"
[ ! -e "${PORT}" ] && PORT="/dev/ttyACM0"

echo "=========================================================="
echo " Calibrating SO-100 Follower Arm on ${PORT}"
echo " 1. Move arm to middle of its range of motion, press Enter"
echo " 2. Move joints sequentially through full range of motion"
echo "=========================================================="

lerobot-calibrate   --robot.type="so100_follower"   --robot.id="so100_follower"   --robot.port="${PORT}"

# Backup new calibration to repo
cp ~/.cache/huggingface/lerobot/calibration/robots/so_follower/so100_follower.json "$(dirname "$0")/../calibration/so100_follower.json" 2>/dev/null || true
echo "Calibration saved to repo in calibration/so100_follower.json"
