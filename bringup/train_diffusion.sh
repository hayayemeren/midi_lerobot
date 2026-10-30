#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
eval "$(python3 "${SCRIPT_DIR}/config_helper.py" --export-env)"

DATASET_REPO="${1:-$DATASET_REPO_ID}"
OUTPUT_DIR="${OUTPUT_DIR:-outputs/train/tidy_socks_diffusion}"
BATCH_SIZE="${BATCH_SIZE:-16}"
STEPS="${STEPS:-100000}"

echo "=========================================================="
echo " Training Diffusion Policy: Tidy Up The Socks (Wrist + Scene)"
echo " Configuration: ${SCRIPT_DIR}/config.json"
echo " Dataset:    ${DATASET_REPO}"
echo " Output Dir: ${OUTPUT_DIR}"
echo " Batch Size: ${BATCH_SIZE}"
echo " Steps:      ${STEPS}"
echo " Device:     CUDA (GPU)"
echo "=========================================================="

lerobot-train   --policy.type=diffusion   --dataset.repo_id="${DATASET_REPO}"   --output_dir="${OUTPUT_DIR}"   --job_name="tidy_socks_diffusion"   --training.batch_size=${BATCH_SIZE}   --training.steps=${STEPS}   --training.save_freq=10000   --training.log_freq=200   --eval.n_episodes=0   --device=cuda
