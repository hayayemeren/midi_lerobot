#!/bin/bash
# Fixed test script with correct camera key naming

# --- Robot Configuration ---
# Hardware Ports
RIGHT_PORT="/dev/ttyACM2"
LEFT_PORT="/dev/ttyACM3"

# Camera Paths (Persistent Physical USB Ports)
CAM_LEFT_PATH='"/dev/v4l/by-path/pci-0000:00:14.0-usb-0:3:1.0-video-index0"'
CAM_MID_PATH='"/dev/v4l/by-path/pci-0000:00:14.0-usb-0:13:1.0-video-index0"'
CAM_RIGHT_PATH='"/dev/v4l/by-path/pci-0000:00:14.0-usb-0:1.1:1.0-video-index0"'

# --- Project Configuration ---
OUTPUT_ROOT="/home/maksimgorki/Defne/lerobot/inference_outputs"
POLICY_PATH="/home/maksimgorki/lerobot/bringup/outputs/train/messy_towel_act_v2/checkpoints/last/pretrained_model"
DATASET_REPO="maksimgorki/eval_model_fold_cloth"
TASK_NAME="deneme"
FPS=30

# Optional: Try alternative checkpoint if model behavior is wrong
# POLICY_PATH="/home/maksimgorki/lerobot/bringup/outputs/train/messy_towel_act_v2/checkpoints/190000/pretrained_model"

rm -rf ${OUTPUT_ROOT}

# ==========================================
# BUILD JSON CAMERA PAYLOADS
# IMPORTANT: Camera keys MUST match training config
# ==========================================
# The model expects these exact keys:
# - observation.images.left_gripper_left
# - observation.images.left_middle
# - observation.images.right_gripper_right

LEFT_CAM_JSON=$(cat <<EOF
{
  "left_gripper_left": {
    "type": "opencv",
    "index_or_path": ${CAM_LEFT_PATH},
    "width": 640,
    "height": 480,
    "fps": ${FPS},
    "fourcc": "MJPG"
  },
  "left_middle": {
    "type": "opencv",
    "index_or_path": ${CAM_MID_PATH},
    "width": 640,
    "height": 480,
    "fps": ${FPS},
    "fourcc": "MJPG"
  }
}
EOF
)

RIGHT_CAM_JSON=$(cat <<EOF
{
  "right_gripper_right": {
    "type": "opencv",
    "index_or_path": ${CAM_RIGHT_PATH},
    "width": 640,
    "height": 480,
    "fps": ${FPS},
    "fourcc": "MJPG"
  }
}
EOF
)

# ==========================================
# FORCE MANUAL CAMERA EXPOSURE (Unlock 30 FPS)
# ==========================================
# auto_exposure=1 (Manual Mode)
# exposure_dynamic_framerate=0 (Never drop FPS for light)
# exposure_time_absolute=100 (Fast shutter)

# Left Camera
v4l2-ctl -d /dev/v4l/by-path/pci-0000:00:14.0-usb-0:3:1.0-video-index0 --set-ctrl=exposure_dynamic_framerate=0
v4l2-ctl -d /dev/v4l/by-path/pci-0000:00:14.0-usb-0:3:1.0-video-index0 --set-ctrl=auto_exposure=1
v4l2-ctl -d /dev/v4l/by-path/pci-0000:00:14.0-usb-0:3:1.0-video-index0 --set-ctrl=exposure_time_absolute=100

# Middle Camera
v4l2-ctl -d /dev/v4l/by-path/pci-0000:00:14.0-usb-0:13:1.0-video-index0 --set-ctrl=exposure_dynamic_framerate=0
v4l2-ctl -d /dev/v4l/by-path/pci-0000:00:14.0-usb-0:13:1.0-video-index0 --set-ctrl=auto_exposure=1
v4l2-ctl -d /dev/v4l/by-path/pci-0000:00:14.0-usb-0:13:1.0-video-index0 --set-ctrl=exposure_time_absolute=100

# Right Camera
v4l2-ctl -d /dev/v4l/by-path/pci-0000:00:14.0-usb-0:1.1:1.0-video-index0 --set-ctrl=exposure_dynamic_framerate=0
v4l2-ctl -d /dev/v4l/by-path/pci-0000:00:14.0-usb-0:1.1:1.0-video-index0 --set-ctrl=auto_exposure=1
v4l2-ctl -d /dev/v4l/by-path/pci-0000:00:14.0-usb-0:1.1:1.0-video-index0 --set-ctrl=exposure_time_absolute=100

# --- Execute ---
echo "Starting LeRobot Evaluation Recording..."
echo "Policy Path: ${POLICY_PATH}"
echo "========================================"

lerobot-record \
  --robot.type="bi_so_follower" \
  --robot.id="homerobotics_bimanual_follower" \
  --robot.right_arm_config.port="${RIGHT_PORT}" \
  --robot.right_arm_config.cameras="${RIGHT_CAM_JSON}" \
  --robot.left_arm_config.port="${LEFT_PORT}" \
  --robot.left_arm_config.cameras="${LEFT_CAM_JSON}" \
  --display_data=false \
  --dataset.repo_id="${DATASET_REPO}" \
  --dataset.single_task="${TASK_NAME}" \
  --dataset.push_to_hub=false \
  --dataset.root="${OUTPUT_ROOT}" \
  --dataset.fps=${FPS} \
  --dataset.streaming_encoding=true \
  --policy.path="${POLICY_PATH}" \
  --policy.device="cuda" \
  --policy.n_action_steps=50 \
  --policy.use_amp=true \
  --dataset.episode_time_s=300
