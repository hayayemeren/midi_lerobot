#!/bin/bash
# =============================================================================
# Retrain ACT for messy_towel — optimized for Quadro RTX 4000 (8GB VRAM)
# =============================================================================
#
# Key changes from the original training:
#   - chunk_size: 100 → 50  (predict 1.7s ahead, not 3.3s — better for grasping)
#   - n_action_steps: 100 → 50  (must match chunk_size during training)
#   - batch_size: 4 → 6  (use_amp frees ~30% VRAM, enough to go from 4 to 6)
#   - use_amp: true  (mixed precision — saves ~30% VRAM, may allow batch_size=6)
#   - steps: 100000 → 200000  (loss was still 0.201 — needs more steps)
#   - optimizer_lr: 1e-5 → 5e-5  (slightly faster convergence with small batch)
#   - optimizer_lr_backbone: 1e-5 → 1e-5  (keep backbone LR conservative)
#   - image_transforms: enabled  (data augmentation to prevent overfitting)
#   - save_freq: 10000  (more checkpoints to pick the best one)
#
# After training, run inference with:
#   --policy.n_action_steps=10 --policy.use_amp=true
#   (execute 10 of 50 predicted steps = 0.33s between re-queries)

lerobot-train \
  --dataset.repo_id="defneerkan/messy_towel" \
  --dataset.video_backend="pyav" \
  --policy.type=act \
  --output_dir="outputs/train/messy_towel_act_v2" \
  --job_name="act_messy_towel_v2" \
  --policy.device=cuda \
  --policy.use_amp=true \
  --policy.chunk_size=50 \
  --policy.n_action_steps=50 \
  --policy.optimizer_lr=5e-5 \
  --policy.optimizer_lr_backbone=1e-5 \
  --policy.kl_weight=10.0 \
  --steps=200000 \
  --batch_size=4 \
  --num_workers=4 \
  --save_freq=10000 \
  --eval_freq=20000 \
  --log_freq=200 \
  --dataset.image_transforms.enable=true \
  --policy.push_to_hub=false \
  --wandb.enable=true \
  --wandb.project="lerobot"
