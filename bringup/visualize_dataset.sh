#!/bin/bash
set -e

DATASET_REPO="${1:-hayayemeren/tidy_socks}"
EPISODE_IDX="${2:-0}"

echo "=========================================================="
echo " Visualizing LeRobot Dataset with Rerun"
echo " Dataset: ${DATASET_REPO}"
echo " Episode: ${EPISODE_IDX}"
echo "=========================================================="

lerobot-dataset-viz   --repo-id "${DATASET_REPO}"   --episode-index "${EPISODE_IDX}"
