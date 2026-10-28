#!/bin/bash
set -e

DATASET_REPO="${1:-hayayemeren/tidy_socks}"
OUTPUT_DIR="outputs/train/tidy_socks_act"
BATCH_SIZE=${BATCH_SIZE:-8}
STEPS=${STEPS:-100000}

echo "=========================================================="
echo " Training ACT Policy: Tidy Up The Socks"
echo " Dataset:    ${DATASET_REPO}"
echo " Output Dir: ${OUTPUT_DIR}"
echo " Batch Size: ${BATCH_SIZE}"
echo " Steps:      ${STEPS}"
echo " Device:     CUDA (GPU)"
echo "=========================================================="

lerobot-train   --policy.type=act   --dataset.repo_id="${DATASET_REPO}"   --output_dir="${OUTPUT_DIR}"   --job_name="tidy_socks_act"   --training.batch_size=${BATCH_SIZE}   --training.steps=${STEPS}   --training.save_freq=10000   --training.log_freq=200   --eval.n_episodes=0   --device=cuda
