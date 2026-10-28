#!/usr/bin/env python3
import os
import sys
import cv2
from pathlib import Path

def test_ports():
    print("=========================================")
    print("   SO-100 HARDWARE DIAGNOSTIC TEST       ")
    print("=========================================")
    
    leader_port = "/dev/ttyACM1"
    follower_port = "/dev/ttyACM0"
    
    # Check by-id links if available
    by_id_dir = Path("/dev/serial/by-id")
    if by_id_dir.exists():
        links = list(by_id_dir.glob("*"))
        print(f"[INFO] Available serial by-id devices ({len(links)}): ")
        for l in links:
            print(f"   - {l.name} -> {l.resolve()}")
    
    print(f"\n1. Checking Leader Arm port: {leader_port}")
    if not os.path.exists(leader_port):
        print(f"   [FAIL] Port {leader_port} not found!")
    else:
        print(f"   [OK] Port {leader_port} exists.")
        
    print(f"2. Checking Follower Arm port: {follower_port}")
    if not os.path.exists(follower_port):
        print(f"   [FAIL] Port {follower_port} not found!")
    else:
        print(f"   [OK] Port {follower_port} exists.")

    # Test Feetech communication
    print("\n3. Testing Leader Arm Feetech Communication...")
    try:
        from lerobot.teleoperators.so_leader import SOLeader, SOLeaderTeleopConfig
        leader = SOLeader(SOLeaderTeleopConfig(id="so100_leader", port=leader_port))
        leader.connect(calibrate=False)
        action = leader.get_action()
        print("   [OK] Leader Arm connected successfully!")
        for k, v in action.items():
            print(f"      * {k}: {v:6.2f}")
        leader.disconnect()
    except Exception as e:
        print(f"   [FAIL] Leader Arm error: {e}")

    print("\n4. Testing Follower Arm Feetech Communication...")
    try:
        from lerobot.robots.so_follower import SOFollower, SOFollowerRobotConfig
        follower = SOFollower(SOFollowerRobotConfig(id="so100_follower", port=follower_port))
        follower.connect(calibrate=False)
        obs = follower.get_observation()
        print("   [OK] Follower Arm connected successfully!")
        for k, v in obs.items():
            print(f"      * {k}: {v:6.2f}")
        follower.disconnect()
    except Exception as e:
        print(f"   [FAIL] Follower Arm error: {e}")

    # Test Camera
    cam_device = "/dev/video0"
    print(f"\n5. Testing Camera: {cam_device}...")
    try:
        cap = cv2.VideoCapture(cam_device)
        if not cap.isOpened():
            print(f"   [FAIL] Could not open camera {cam_device}")
        else:
            ret, frame = cap.read()
            if ret:
                h, w, c = frame.shape
                print(f"   [OK] Camera captured frame successfully! Resolution: {w}x{h}, Channels: {c}")
            else:
                print(f"   [FAIL] Could not grab frame from {cam_device}")
            cap.release()
    except Exception as e:
        print(f"   [FAIL] Camera error: {e}")

    print("=========================================")
    print("Diagnostic complete.")
    print("=========================================")

if __name__ == "__main__":
    test_ports()
