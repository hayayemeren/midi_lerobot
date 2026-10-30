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

# Allow command-line overrides if user passes them (e.g. NUM_EPISODES=10 bash bringup/data_collection.sh)
REPO_ID="${REPO_ID:-$DATASET_REPO_ID}"
TASK="${TASK:-$TASK}"
NUM_EPISODES="${NUM_EPISODES:-$NUM_EPISODES}"
EPISODE_TIME_S="${EPISODE_TIME_S:-$EPISODE_TIME_S}"
RESET_TIME_S="${RESET_TIME_S:-$RESET_TIME_S}"
FPS="${FPS:-$FPS}"
PUSH_TO_HUB="${PUSH_TO_HUB:-$PUSH_TO_HUB}"

echo "=========================================================="
echo " Starting LeRobot Data Collection: Tidy Up The Socks"
echo " Configuration: ${SCRIPT_DIR}/config.json"
echo " Leader Port:   ${LEADER_PORT}"
echo " Follower Port: ${FOLLOWER_PORT}"
echo " Cameras JSON:  ${CAMERAS_JSON}"
echo " Dataset Repo:  ${REPO_ID}"
echo " Task:          ${TASK}"
echo " Episodes:      ${NUM_EPISODES} (${EPISODE_TIME_S}s max each, reset: ${RESET_TIME_S}s)"
echo " FPS:           ${FPS}"
echo " Push to Hub:   ${PUSH_TO_HUB}"
echo "----------------------------------------------------------"
echo " KEYBOARD CONTROLS (in terminal):"
echo "   - Press 'c' : Start episode recording early or finish early"
echo "   - Press 'r' : Re-record / discard current episode if failed"
echo "   - Press 'exit' or Ctrl+C : End recording session"
echo "=========================================================="

lerobot-record   --robot.type="${FOLLOWER_TYPE}"   --robot.id="${FOLLOWER_ID}"   --robot.port="${FOLLOWER_PORT}"   --robot.cameras="${CAMERAS_JSON}"   --teleop.type="${LEADER_TYPE}"   --teleop.id="${LEADER_ID}"   --teleop.port="${LEADER_PORT}"   --display_data=false   --dataset.repo_id="${REPO_ID}"   --dataset.num_episodes="${NUM_EPISODES}"   --dataset.single_task="${TASK}"   --dataset.episode_time_s="${EPISODE_TIME_S}"   --dataset.reset_time_s="${RESET_TIME_S}"   --dataset.fps="${FPS}"   --dataset.streaming_encoding=true   --dataset.push_to_hub="${PUSH_TO_HUB}"   --resume=true
