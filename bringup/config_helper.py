#!/usr/bin/env python3
"""
Helper utility to load and resolve LeRobot hardware configurations from config.json.
Used by both bash scripts (via --export-env) and python bringup scripts.
"""

import os
import sys
import json
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parent / "config.json"

def load_raw_config():
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Configuration file not found at: {CONFIG_PATH}")
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def resolve_device_path(primary_path: str, fallback_path: str = "") -> str:
    """Return primary_path if it exists, otherwise fallback_path if it exists, else primary_path."""
    if primary_path and os.path.exists(primary_path):
        return primary_path
    if fallback_path and os.path.exists(fallback_path):
        return fallback_path
    return primary_path if primary_path else fallback_path

def get_resolved_config():
    cfg = load_raw_config()
    
    # Resolve leader port
    leader = cfg.get("leader", {})
    leader_port = resolve_device_path(leader.get("port", ""), leader.get("fallback_port", ""))
    leader["resolved_port"] = leader_port
    
    # Resolve follower port
    follower = cfg.get("follower", {})
    follower_port = resolve_device_path(follower.get("port", ""), follower.get("fallback_port", ""))
    follower["resolved_port"] = follower_port
    
    # Resolve cameras
    cameras = cfg.get("cameras", {})
    for cam_name, cam_cfg in cameras.items():
        if isinstance(cam_cfg, dict):
            idx_or_path = str(cam_cfg.get("index_or_path", ""))
            fallback = str(cam_cfg.get("fallback_path", ""))
            resolved = resolve_device_path(idx_or_path, fallback)
            cam_cfg["resolved_path"] = resolved
            
    return cfg

def get_cameras_json_payload(cfg=None):
    """Generates the JSON camera payload required by lerobot-record for all enabled cameras."""
    if cfg is None:
        cfg = get_resolved_config()
    cams = cfg.get("cameras", {})
    payload = {}
    for cam_name, cam_cfg in cams.items():
        if cam_cfg.get("enabled", True):
            # If path is an integer string, convert to int for OpenCV index
            path_val = cam_cfg.get("resolved_path", cam_cfg.get("index_or_path"))
            if isinstance(path_val, str) and path_val.isdigit():
                path_val = int(path_val)
            payload[cam_name] = {
                "type": cam_cfg.get("type", "opencv"),
                "index_or_path": path_val,
                "width": cam_cfg.get("width", 640),
                "height": cam_cfg.get("height", 480),
                "fps": cam_cfg.get("fps", 30),
                "fourcc": cam_cfg.get("fourcc", "MJPG"),
            }
    return json.dumps(payload)

def export_env():
    """Prints bash export statements so bash scripts can evaluate them."""
    cfg = get_resolved_config()
    
    leader = cfg.get("leader", {})
    follower = cfg.get("follower", {})
    cams = cfg.get("cameras", {})
    dataset = cfg.get("dataset", {})
    policy = cfg.get("policy", {})
    training = cfg.get("training", {})
    
    wrist = cams.get("wrist", {})
    scene = cams.get("scene", {})
    
    cams_json_str = get_cameras_json_payload(cfg)
    
    # Quote safely for bash
    def bquote(val):
        s = str(val).replace("'", "'\''")
        return f"'{s}'"

    print(f"export LEADER_PORT={bquote(leader.get('resolved_port', ''))}")
    print(f"export LEADER_TYPE={bquote(leader.get('type', 'so100_leader'))}")
    print(f"export LEADER_ID={bquote(leader.get('id', 'so100_leader'))}")
    
    print(f"export FOLLOWER_PORT={bquote(follower.get('resolved_port', ''))}")
    print(f"export FOLLOWER_TYPE={bquote(follower.get('type', 'so100_follower'))}")
    print(f"export FOLLOWER_ID={bquote(follower.get('id', 'so100_follower'))}")
    
    print(f"export WRIST_CAM_ENABLED={bquote(str(wrist.get('enabled', True)).lower())}")
    print(f"export WRIST_CAM_PATH={bquote(wrist.get('resolved_path', ''))}")
    
    print(f"export SCENE_CAM_ENABLED={bquote(str(scene.get('enabled', True)).lower())}")
    print(f"export SCENE_CAM_PATH={bquote(scene.get('resolved_path', ''))}")
    
    print(f"export CAMERAS_JSON={bquote(cams_json_str)}")
    
    print(f"export DATASET_REPO_ID={bquote(dataset.get('repo_id', 'hayayemeren/tidy_socks'))}")
    print(f"export TASK={bquote(dataset.get('task', 'Tidy up the socks.'))}")
    print(f"export NUM_EPISODES={bquote(dataset.get('num_episodes', 50))}")
    print(f"export EPISODE_TIME_S={bquote(dataset.get('episode_time_s', 60))}")
    print(f"export RESET_TIME_S={bquote(dataset.get('reset_time_s', 15))}")
    print(f"export FPS={bquote(dataset.get('fps', 30))}")
    print(f"export PUSH_TO_HUB={bquote(str(dataset.get('push_to_hub', False)).lower())}")
    
    print(f"export POLICY_PATH={bquote(policy.get('path', 'outputs/train/tidy_socks_act/checkpoints/last/pretrained_model'))}")
    print(f"export EVAL_REPO_ID={bquote(policy.get('eval_repo_id', 'hayayemeren/eval_tidy_socks'))}")
    print(f"export POLICY_DEVICE={bquote(policy.get('device', 'cuda'))}")
    print(f"export POLICY_N_ACTION_STEPS={bquote(policy.get('n_action_steps', 30))}")
    print(f"export POLICY_USE_AMP={bquote(str(policy.get('use_amp', True)).lower())}")

if __name__ == "__main__":
    if "--export-env" in sys.argv:
        export_env()
    elif "--cameras-json" in sys.argv:
        print(get_cameras_json_payload())
    else:
        cfg = get_resolved_config()
        print(json.dumps(cfg, indent=2))
