#!/usr/bin/env python3
"""
Quick Interactive Teleoperation Test (1 Leader -> 1 Follower)
Runs a simple 10-second mirroring loop and prints positions.
"""
import time
from lerobot.teleoperators.so_leader import SOLeader, SOLeaderTeleopConfig
from lerobot.robots.so_follower import SOFollower, SOFollowerRobotConfig

def main():
    print("Connecting Leader (/dev/ttyACM1) and Follower (/dev/ttyACM0)...")
    leader = SOLeader(SOLeaderTeleopConfig(id="so100_leader", port="/dev/ttyACM1"))
    follower = SOFollower(SOFollowerRobotConfig(id="so100_follower", port="/dev/ttyACM0"))

    leader.connect(calibrate=False)
    follower.connect(calibrate=False)

    print("\nBoth connected! Running 10-second mirror test (Move leader arm!)")
    start = time.time()
    try:
        while time.time() - start < 10.0:
            act = leader.get_action()
            # Send action directly to follower
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
