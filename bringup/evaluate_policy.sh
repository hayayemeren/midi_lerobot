#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Load configuration from bringup/config.json
eval "$(python3 "${SCRIPT_DIR}/config_helper.py" --export-env)"

POLICY_PATH="${1:-$POLICY_PATH}"
EVAL_REPO="${2:-$EVAL_REPO_ID}"
EPISODE_TIME_S="${EPISODE_TIME_S:-$EPISODE_TIME_S}"

echo "=========================================================="
echo " Running Autonomous Policy Evaluation on Follower Arm"
echo " Configuration: ${SCRIPT_DIR}/config.json"
echo " Policy Path:   ${POLICY_PATH}"
echo " Follower Port: ${FOLLOWER_PORT}"
echo " Cameras JSON:  ${CAMERAS_JSON}"
echo " Evaluation ID: ${EVAL_REPO}"
echo "=========================================================="

lerobot-record   --robot.type="${FOLLOWER_TYPE}"   --robot.id="${FOLLOWER_ID}"   --robot.port="${FOLLOWER_PORT}"   --robot.cameras="${CAMERAS_JSON}"   --policy.path="${POLICY_PATH}"   --policy.device="${POLICY_DEVICE}"   --policy.n_action_steps="${POLICY_N_ACTION_STEPS}"   --policy.use_amp="${POLICY_USE_AMP}"   --dataset.repo_id="${EVAL_REPO}"   --dataset.single_task="${TASK}"   --dataset.push_to_hub=false   --dataset.fps="${FPS}"   --dataset.episode_time_s="${EPISODE_TIME_S}"   --display_data=false
