#!/usr/bin/env python3
"""
Standalone script to test policy inference without robot connection.
Useful for debugging model behavior and action outputs.
"""

import torch
import numpy as np
from pathlib import Path
from lerobot.policies.factory import make_policy


def test_policy_inference():
    """Test policy forward pass with dummy data."""
    
    policy_path = Path("/home/maksimgorki/lerobot/bringup/outputs/train/messy_towel_act_v2/checkpoints/last/pretrained_model")
    
    print(f"Loading policy from: {policy_path}")
    print("=" * 70)
    
    # Load policy
    policy = make_policy(
        policy_name="act",
        pretrained_model_name_or_path=str(policy_path),
        device="cuda" if torch.cuda.is_available() else "cpu"
    )
    
    print(f"Policy loaded successfully!")
    print(f"Device: {policy.device}")
    print(f"Model type: {type(policy).__name__}")
    print()
    
    # Print model architecture info
    print("Model Configuration:")
    print(f"  Input features: {policy.policy_config.input_features}")
    print(f"  Output features: {policy.policy_config.output_features}")
    print(f"  n_obs_steps: {policy.policy_config.n_obs_steps}")
    print(f"  n_action_steps: {policy.policy_config.n_action_steps}")
    print()
    
    # Create dummy observations matching the expected shapes
    print("Creating dummy observations...")
    batch_size = 2
    
    observations = {
        "observation.state": torch.randn(
            batch_size, 1, 12,  # (batch, n_obs_steps, state_dim)
            dtype=torch.float32,
            device=policy.device
        ),
        "observation.images.left_gripper_left": torch.randn(
            batch_size, 1, 3, 480, 640,  # (batch, n_obs_steps, channels, height, width)
            dtype=torch.float32,
            device=policy.device
        ),
        "observation.images.left_middle": torch.randn(
            batch_size, 1, 3, 480, 640,
            dtype=torch.float32,
            device=policy.device
        ),
        "observation.images.right_gripper_right": torch.randn(
            batch_size, 1, 3, 480, 640,
            dtype=torch.float32,
            device=policy.device
        ),
    }
    
    print("Observation shapes:")
    for key, val in observations.items():
        print(f"  {key}: {val.shape}")
    print()
    
    # Run inference
    print("Running inference...")
    try:
        with torch.no_grad():
            output = policy(observations)
        
        print("✓ Inference successful!")
        print()
        print(f"Output type: {type(output)}")
        
        if isinstance(output, dict):
            for key, val in output.items():
                print(f"  {key}: {val.shape} | min={val.min():.3f}, max={val.max():.3f}, mean={val.mean():.3f}")
        elif isinstance(output, torch.Tensor):
            print(f"  Action tensor shape: {output.shape}")
            print(f"  Action range: min={output.min():.3f}, max={output.max():.3f}")
            print(f"  Action values (batch 0, first step):")
            print(f"    {output[0, 0, :].cpu().numpy()}")
            print()
            print(f"  ⚠️  Check action ranges:")
            print(f"    - Are values in reasonable range? (typically -1 to 1)")
            print(f"    - First 6 values: arm position/rotation")
            print(f"    - Last 6 values: other arm or gripper")
            print(f"    - Check against training data ranges")
        
    except Exception as e:
        print(f"✗ Inference failed: {type(e).__name__}: {e}")
        print()
        print("Troubleshooting:")
        print("  1. Check observation key names match policy config")
        print("  2. Check observation shapes match policy input_features")
        print("  3. Check observation data types (should be float32)")
        print("  4. Try with different checkpoint: checkpoints/190000/pretrained_model")
        import traceback
        traceback.print_exc()
        return False
    
    print()
    print("=" * 70)
    print("✓ Model test complete. Policy appears to be working correctly.")
    print()
    print("Next steps:")
    print("  1. If test passed: Check camera key names in test_bimanual_fixed.sh")
    print("  2. If actions look wrong: May need more training data or checkpoint adjustment")
    print("  3. Run actual test with --display_data=true to visualize observations")
    
    return True


if __name__ == "__main__":
    success = test_policy_inference()
    exit(0 if success else 1)
