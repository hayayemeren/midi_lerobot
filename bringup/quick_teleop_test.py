#!/usr/bin/env python3
"""
Quick Interactive Teleoperation Test (1 Leader -> 1 Follower)
Reads ports from bringup/config.json.
Runs a 10-second mirroring loop and prints positions.
"""
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from config_helper import get_resolved_config

from lerobot.teleoperators.so_leader import SOLeader, SOLeaderTeleopConfig
from lerobot.robots.so_follower import SOFollower, SOFollowerRobotConfig

def main():
    cfg = get_resolved_config()
    leader_port = cfg["leader"]["resolved_port"]
    follower_port = cfg["follower"]["resolved_port"]

    print(f"Connecting Leader ({leader_port}) and Follower ({follower_port})...")
    leader = SOLeader(SOLeaderTeleopConfig(id=cfg["leader"].get("id", "so100_leader"), port=leader_port))
    follower = SOFollower(SOFollowerRobotConfig(id=cfg["follower"].get("id", "so100_follower"), port=follower_port))

    leader.connect(calibrate=False)
    follower.connect(calibrate=False)

    print("\nBoth connected! Running 10-second mirror test (Move leader arm!)")
    start = time.time()
    try:
        while time.time() - start < 10.0:
            act = leader.get_action()
            follower.send_action(act)
            print(f"\rLeader Pan: {act['shoulder_pan.pos']:6.1f}° | Grip: {act['gripper.pos']:5.1f}%   ", end="", flush=True)
            time.sleep(0.02)
    finally:
        print("\nDisconnecting...")
        follower.disconnect()
        leader.disconnect()
        print("Done!")

if __name__ == "__main__":
    main()
