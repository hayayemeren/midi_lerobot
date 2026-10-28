#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Ensure calibration cache exists
mkdir -p ~/.cache/huggingface/lerobot/calibration/teleoperators/so_leader
mkdir -p ~/.cache/huggingface/lerobot/calibration/robots/so_follower
cp -n "${REPO_ROOT}/calibration/so100_leader.json" ~/.cache/huggingface/lerobot/calibration/teleoperators/so_leader/so100_leader.json 2>/dev/null || true
cp -n "${REPO_ROOT}/calibration/so100_follower.json" ~/.cache/huggingface/lerobot/calibration/robots/so_follower/so100_follower.json 2>/dev/null || true

# ==========================================
# 1. HARDWARE CONFIGURATION
# ==========================================
LEADER_PORT="/dev/serial/by-id/usb-1a86_USB_Single_Serial_5AE6084621-if00"
[ ! -e "${LEADER_PORT}" ] && LEADER_PORT="/dev/ttyACM1"

FOLLOWER_PORT="/dev/serial/by-id/usb-1a86_USB_Single_Serial_5AE6084008-if00"
[ ! -e "${FOLLOWER_PORT}" ] && FOLLOWER_PORT="/dev/ttyACM0"

CAM_PATH="/dev/v4l/by-id/usb-Sonix_Technology_Co.__Ltd._USB2.0_CAM1_USB2.0_CAM1-video-index0"
[ ! -e "${CAM_PATH}" ] && CAM_PATH="/dev/video0"

CAM_NAME="camera"
CAM_WIDTH=640
CAM_HEIGHT=480
CAM_FPS=30
CAM_FOURCC="MJPG"

# ==========================================
# 2. DATASET & RECORDING CONFIGURATION
# ==========================================
REPO_ID="${REPO_ID:-hayayemeren/tidy_socks}"
TASK="${TASK:-Tidy up the socks.}"

NUM_EPISODES=${NUM_EPISODES:-50}
EPISODE_TIME_S=${EPISODE_TIME_S:-60}
RESET_TIME_S=${RESET_TIME_S:-15}
FPS=${FPS:-30}
PUSH_TO_HUB=${PUSH_TO_HUB:-false}

# ==========================================
# 3. BUILD JSON CAMERA PAYLOAD
# ==========================================
CAM_JSON=$(cat <<EOC
{
  "${CAM_NAME}": {
    "type": "opencv",
    "index_or_path": "${CAM_PATH}",
    "width": ${CAM_WIDTH},
    "height": ${CAM_HEIGHT},
    "fps": ${CAM_FPS},
    "fourcc": "${CAM_FOURCC}"
  }
}
EOC
)

# ==========================================
# 4. EXECUTE RECORDING COMMAND
# ==========================================
echo "=========================================================="
echo " Starting LeRobot Data Collection: Tidy Up The Socks"
echo " Leader Port:   ${LEADER_PORT}"
echo " Follower Port: ${FOLLOWER_PORT}"
echo " Camera:        ${CAM_PATH} (${CAM_NAME})"
echo " Dataset Repo:  ${REPO_ID}"
echo " Task:          ${TASK}"
echo " Episodes:      ${NUM_EPISODES} (${EPISODE_TIME_S}s max each, reset: ${RESET_TIME_S}s)"
echo " Push to Hub:   ${PUSH_TO_HUB}"
echo "----------------------------------------------------------"
echo " KEYBOARD CONTROLS (in terminal):"
echo "   - Press 'c' : Start episode recording early or finish early"
echo "   - Press 'r' : Re-record / discard current episode if failed"
echo "   - Press 'exit' or Ctrl+C : End recording session"
echo "=========================================================="

lerobot-record   --robot.type="so100_follower"   --robot.id="so100_follower"   --robot.port="${FOLLOWER_PORT}"   --robot.cameras="${CAM_JSON}"   --teleop.type="so100_leader"   --teleop.id="so100_leader"   --teleop.port="${LEADER_PORT}"   --display_data=false   --dataset.repo_id="${REPO_ID}"   --dataset.num_episodes="${NUM_EPISODES}"   --dataset.single_task="${TASK}"   --dataset.episode_time_s="${EPISODE_TIME_S}"   --dataset.reset_time_s="${RESET_TIME_S}"   --dataset.fps="${FPS}"   --dataset.streaming_encoding=true   --dataset.push_to_hub="${PUSH_TO_HUB}"   --resume=true
