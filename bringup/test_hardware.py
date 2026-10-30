#!/usr/bin/env python3
"""
SO-100 Hardware Diagnostic Test
Reads ports and camera settings directly from bringup/config.json.
Tests Leader Arm, Follower Arm, Wrist Camera, and Scene Camera.
"""

import os
import sys
from pathlib import Path
import cv2

# Import config_helper
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from config_helper import get_resolved_config

def main():
    print("==========================================================")
    print("        SO-100 HARDWARE & CAMERA DIAGNOSTIC TEST          ")
    print("==========================================================")
    
    cfg = get_resolved_config()
    
    leader_cfg = cfg.get("leader", {})
    follower_cfg = cfg.get("follower", {})
    cameras_cfg = cfg.get("cameras", {})
    
    leader_port = leader_cfg.get("resolved_port", "/dev/ttyACM1")
    follower_port = follower_cfg.get("resolved_port", "/dev/ttyACM0")
    
    # 1. Available Serial by-id Links
    by_id_dir = Path("/dev/serial/by-id")
    if by_id_dir.exists():
        links = list(by_id_dir.glob("*"))
        print(f"[INFO] Available serial by-id devices ({len(links)}): ")
        for l in links:
            print(f"   - {l.name} -> {l.resolve()}")
    
    # 2. Check Port Existence
    print(f"\n1. Checking Leader Arm port: {leader_port}")
    if not os.path.exists(leader_port):
        print(f"   [FAIL] Port {leader_port} not found on filesystem!")
    else:
        print(f"   [OK] Port {leader_port} exists.")
        
    print(f"2. Checking Follower Arm port: {follower_port}")
    if not os.path.exists(follower_port):
        print(f"   [FAIL] Port {follower_port} not found on filesystem!")
    else:
        print(f"   [OK] Port {follower_port} exists.")

    # 3. Test Feetech Communication - Leader
    print("\n3. Testing Leader Arm Feetech Communication...")
    try:
        from lerobot.teleoperators.so_leader import SOLeader, SOLeaderTeleopConfig
        leader = SOLeader(SOLeaderTeleopConfig(id=leader_cfg.get("id", "so100_leader"), port=leader_port))
        leader.connect(calibrate=False)
        action = leader.get_action()
        print("   [OK] Leader Arm connected successfully!")
        for k, v in action.items():
            print(f"      * {k:18s}: {v:6.2f}")
        leader.disconnect()
    except Exception as e:
        print(f"   [FAIL] Leader Arm error: {e}")

    # 4. Test Feetech Communication - Follower
    print("\n4. Testing Follower Arm Feetech Communication...")
    try:
        from lerobot.robots.so_follower import SOFollower, SOFollowerRobotConfig
        follower = SOFollower(SOFollowerRobotConfig(id=follower_cfg.get("id", "so100_follower"), port=follower_port))
        follower.connect(calibrate=False)
        obs = follower.get_observation()
        print("   [OK] Follower Arm connected successfully!")
        for k, v in obs.items():
            if not hasattr(v, "shape"):
                print(f"      * {k:18s}: {v:6.2f}")
        follower.disconnect()
    except Exception as e:
        print(f"   [FAIL] Follower Arm error: {e}")

    # 5. Test Cameras (Wrist and Scene)
    print("\n5. Testing Cameras configured in bringup/config.json...")
    cam_results = {}
    
    for cam_name in ["wrist", "scene"]:
        cinfo = cameras_cfg.get(cam_name, {})
        enabled = cinfo.get("enabled", True)
        target_path = cinfo.get("resolved_path", cinfo.get("index_or_path", ""))
        
        print(f"\n   --> [{cam_name.upper()} CAMERA] Target: {target_path} (Enabled: {enabled})")
        if not enabled:
            print(f"       [SKIPPED] {cam_name} camera is disabled in bringup/config.json")
            cam_results[cam_name] = "SKIPPED"
            continue
            
        if not target_path or (isinstance(target_path, str) and not os.path.exists(target_path) and not target_path.isdigit()):
            print(f"       [FAIL] Device path '{target_path}' does not exist on filesystem.")
            print("              Hint: Ensure camera is plugged into USB, or run 'python bringup/find_cameras.py' to locate it.")
            cam_results[cam_name] = "FAIL"
            continue
            
        # Try opening camera
        idx_or_path = int(target_path) if (isinstance(target_path, str) and target_path.isdigit()) else target_path
        cap = cv2.VideoCapture(idx_or_path, cv2.CAP_V4L2)
        if not cap.isOpened():
            cap = cv2.VideoCapture(idx_or_path)
            
        if not cap.isOpened():
            print(f"       [FAIL] Could not open camera at '{target_path}'.")
            print("              Hint: Check permissions (sudo chmod 666 /dev/video*) or run 'python bringup/find_cameras.py'.")
            cam_results[cam_name] = "FAIL"
        else:
            ret, frame = cap.read()
            if ret and frame is not None:
                h, w, c = frame.shape
                print(f"       [OK] Successfully captured frame! Resolution: {w}x{h}, Channels: {c}")
                cam_results[cam_name] = "OK"
            else:
                print(f"       [FAIL] Camera opened but failed to grab frame.")
                cam_results[cam_name] = "FAIL"
            cap.release()

    print("\n==========================================================")
    print("Diagnostic Summary:")
    print(f"   - Leader Port:   {leader_port}")
    print(f"   - Follower Port: {follower_port}")
    for cname, res in cam_results.items():
        print(f"   - {cname.capitalize()} Camera:  [{res}] ({cameras_cfg.get(cname, {}).get('resolved_path', 'N/A')})")
    print("\nConfiguration file: bringup/config.json")
    print("Run 'python bringup/find_cameras.py' to detect all plugged-in USB cameras.")
    print("==========================================================")

if __name__ == "__main__":
    main()
