#!/bin/bash
set -e

POLICY_PATH="${1:-outputs/train/tidy_socks_act/checkpoints/last/pretrained_model}"
EVAL_REPO="${2:-hayayemeren/eval_tidy_socks}"
EPISODE_TIME_S=${EPISODE_TIME_S:-60}

FOLLOWER_PORT="/dev/serial/by-id/usb-1a86_USB_Single_Serial_5AE6084008-if00"
[ ! -e "${FOLLOWER_PORT}" ] && FOLLOWER_PORT="/dev/ttyACM0"

CAM_PATH="/dev/v4l/by-id/usb-Sonix_Technology_Co.__Ltd._USB2.0_CAM1_USB2.0_CAM1-video-index0"
[ ! -e "${CAM_PATH}" ] && CAM_PATH="/dev/video0"

CAM_NAME="camera"
FPS=30

CAM_JSON=$(cat <<EOC
{
  "${CAM_NAME}": {
    "type": "opencv",
    "index_or_path": "${CAM_PATH}",
    "width": 640,
    "height": 480,
    "fps": ${FPS},
    "fourcc": "MJPG"
  }
}
EOC
)

echo "=========================================================="
echo " Running Autonomous Policy Evaluation on Follower Arm"
echo " Policy Path:   ${POLICY_PATH}"
echo " Follower Port: ${FOLLOWER_PORT}"
echo " Camera:        ${CAM_PATH}"
echo " Evaluation ID: ${EVAL_REPO}"
echo "=========================================================="

lerobot-record   --robot.type="so100_follower"   --robot.id="so100_follower"   --robot.port="${FOLLOWER_PORT}"   --robot.cameras="${CAM_JSON}"   --policy.path="${POLICY_PATH}"   --policy.device="cuda"   --policy.n_action_steps=30   --policy.use_amp=true   --dataset.repo_id="${EVAL_REPO}"   --dataset.single_task="Tidy up the socks."   --dataset.push_to_hub=false   --dataset.fps=${FPS}   --dataset.episode_time_s=${EPISODE_TIME_S}   --display_data=false
