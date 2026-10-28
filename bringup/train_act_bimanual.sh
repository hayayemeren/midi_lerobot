# #!/bin/bash

# lerobot-train \
#   --dataset.repo_id="defneerkan/messy_towel" \
#   --dataset.video_backend="pyav" \
#   --policy.type=act \
#   --output_dir="outputs/train/messy_towel_act" \
#   --job_name="act_bimanual_messy_towel" \
#   --policy.device=cuda \
#   --wandb.enable=true \
#   --steps=100000 \
#   --batch_size=4 \
#   --num_workers=2 \
#   --policy.push_to_hub=false \
#   --dataset.image_transforms.enable=true


#!/bin/bash

lerobot-train \
  --dataset.repo_id="defneerkan/merged_fold_cloth_50hz_3" \
  --dataset.video_backend="pyav" \
  --policy.type=act \
  --output_dir="outputs/train/model_fold_cloth_twice_latest" \
  --job_name="act_fold_cloth_twice" \
  --policy.device=cuda \
  --wandb.enable=true \
  --wandb.project="lerobot_folding_new" \
  --steps=100000 \
  --eval_freq=10000 \
  --save_freq=10000 \
  --batch_size=6 \
  --num_workers=4 \
  --dataset.image_transforms.enable=true \
  --policy.push_to_hub=false

