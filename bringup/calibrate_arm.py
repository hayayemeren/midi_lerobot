#!/usr/bin/env python3
"""
Interactive Guided Calibration Script for SO-100 Leader and Follower Arms.
Uses LeRobot's official Feetech calibration procedure, loads ports from bringup/config.json,
and automatically backs up calibration JSON files into calibration/.
"""

import sys
import os
import time
import argparse
import shutil
from pathlib import Path

# Add bringup directory to path for config_helper
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

from config_helper import get_resolved_config
from lerobot.motors import MotorCalibration
from lerobot.motors.feetech import OperatingMode
from lerobot.teleoperators.so_leader import SOLeader, SOLeaderTeleopConfig
from lerobot.robots.so_follower import SOFollower, SOFollowerRobotConfig

def print_banner(text):
    print("\n" + "=" * 65)
    print(f" {text}")
    print("=" * 65)

def print_step(step_num, title, instructions):
    print(f"\n>>> [STEP {step_num}] {title}")
    print("-" * 50)
    for line in instructions:
        print(f"  * {line}")
    print("-" * 50)

def calibrate_device(device_type: str, force_fresh: bool = True):
    """
    device_type: 'leader' or 'follower'
    """
    cfg = get_resolved_config()
    is_leader = (device_type.lower() == "leader")
    dev_name = "Leader Arm (Teleoperator)" if is_leader else "Follower Arm (Robot)"
    
    dev_cfg = cfg.get("leader" if is_leader else "follower", {})
    port = dev_cfg.get("resolved_port") or dev_cfg.get("port")
    dev_id = dev_cfg.get("id", "so100_leader" if is_leader else "so100_follower")
    
    print_banner(f"STARTING CALIBRATION: {dev_name.upper()}")
    print(f"Port: {port}")
    print(f"Device ID: {dev_id}")
    
    if not os.path.exists(port):
        print(f"\n[ERROR] Serial port '{port}' not found on the system!")
        print("Please check that the USB cable is securely connected, or check 'bringup/config.json'.")
        return False

    # Instantiate device
    if is_leader:
        teleop_config = SOLeaderTeleopConfig(id=dev_id, port=port)
        device = SOLeader(teleop_config)
    else:
        robot_config = SOFollowerRobotConfig(id=dev_id, port=port)
        device = SOFollower(robot_config)

    # If force_fresh, temporarily backup existing cache so lerobot doesn't just reload the old file
    cache_fpath = device.calibration_fpath
    cache_backup = None
    if force_fresh and cache_fpath.is_file():
        cache_backup = cache_fpath.with_suffix(".json.bak")
        shutil.copyfile(cache_fpath, cache_backup)
        # Clear device calibration in memory
        device.calibration = None

    print("\nConnecting to arm motors (torque will be disabled)...")
    device.connect(calibrate=False)
    
    try:
        bus = device.bus
        bus.disable_torque()
        for motor in bus.motors:
            bus.write("Operating_Mode", motor, OperatingMode.POSITION.value)

        # ---------------------------------------------------------
        # STEP 1: Center / Midpoint Pose (Half-Turn Homing)
        # ---------------------------------------------------------
        print_step(
            1,
            "SET CENTER / RESTING POSITION (HOMING OFFSETS)",
            [
                "Move the arm by hand to the CENTER of its workspace:",
                "  1. Shoulder Pan: Center facing forward (0°)",
                "  2. Shoulder Lift: Upright / Neutral working posture (~45°-90°)",
                "  3. Elbow Flex: Bent at roughly ~90° angle",
                "  4. Wrist Flex: Centered straight in line with forearm",
                "  5. Wrist Roll: Neutral rotation",
                "  6. Gripper: Opened halfway (~50% open)",
            ]
        )
        input(">> Place the arm in the CENTER pose and press [ENTER] to record homing offsets... ")
        
        print("\nRecording midpoint positions and setting homings...")
        homing_offsets = bus.set_half_turn_homings()
        print("[OK] Homing offsets recorded successfully!")

        # ---------------------------------------------------------
        # STEP 2: Range of Motion
        # ---------------------------------------------------------
        full_turn_motor = "wrist_roll"
        unknown_range_motors = [motor for motor in bus.motors if motor != full_turn_motor]
        
        print_step(
            2,
            "RECORD PHYSICAL RANGE OF MOTION (MIN & MAX LIMITS)",
            [
                "Move each joint gently by hand through its entire physical range:",
                "  * Shoulder Pan: Full left -> Full right",
                "  * Shoulder Lift: Full back -> Full forward",
                "  * Elbow Flex: Full curl in -> Full stretch out",
                "  * Wrist Flex: Full tilt up -> Full tilt down",
                "  * Gripper: Squeeze fully closed -> Open fully wide",
                f"  (Note: '{full_turn_motor}' is a full 360° motor and is handled automatically: 0 to 4095)",
            ]
        )
        input(">> Press [ENTER] when ready to start moving joints... ")
        
        print("\n>>> LIVE ENCODER STREAMING (Move joints now!). Press [ENTER] when all joints reached limits...")
        range_mins, range_maxes = bus.record_ranges_of_motion(unknown_range_motors)
        range_mins[full_turn_motor] = 0
        range_maxes[full_turn_motor] = 4095

        # ---------------------------------------------------------
        # STEP 3: Save and Program Motors
        # ---------------------------------------------------------
        print_step(
            3,
            "PROGRAMMING MOTORS & SAVING CALIBRATION",
            [
                "Writing limits and offsets to motor EEPROM / RAM...",
                "Saving calibration JSON to cache and repository backup..."
            ]
        )
        calibration = {}
        for motor, m in bus.motors.items():
            calibration[motor] = MotorCalibration(
                id=m.id,
                drive_mode=0,
                homing_offset=homing_offsets[motor],
                range_min=range_mins[motor],
                range_max=range_maxes[motor],
            )

        bus.write_calibration(calibration)
        device.calibration = calibration
        device._save_calibration()

        # Also save to repo calibration directory
        repo_calib_dir = REPO_ROOT / "calibration"
        repo_calib_dir.mkdir(parents=True, exist_ok=True)
        repo_calib_file = repo_calib_dir / f"{dev_id}.json"
        shutil.copyfile(device.calibration_fpath, repo_calib_file)
        
        # Remove backup if calibration succeeded
        if cache_backup and cache_backup.is_file():
            cache_backup.unlink()

        print(f"[OK] Calibration written to motor EEPROM!")
        print(f"[OK] Cache file:   {device.calibration_fpath}")
        print(f"[OK] Repo backup:  {repo_calib_file}")

        # Print summary table
        print("\n" + "=" * 65)
        print(f" CALIBRATION SUMMARY: {dev_name}")
        print("=" * 65)
        print(f"{'MOTOR NAME':<16} | {'HOMING':>8} | {'MIN':>6} | {'MAX':>6} | {'RANGE':>7}")
        print("-" * 65)
        for mname, mcal in calibration.items():
            deg_range = (mcal.range_max - mcal.range_min) * 360.0 / 4096.0
            print(f"{mname:<16} | {mcal.homing_offset:8d} | {mcal.range_min:6d} | {mcal.range_max:6d} | {deg_range:6.1f}°")
        print("=" * 65)

        return True

    except Exception as e:
        print(f"\n[FAIL] Calibration failed with error: {e}")
        # Restore backup if failed
        if cache_backup and cache_backup.is_file():
            shutil.copyfile(cache_backup, cache_fpath)
            cache_backup.unlink()
        return False
    finally:
        device.disconnect()
        print("Disconnected cleanly.")

def main():
    parser = argparse.ArgumentParser(description="SO-100 Robot Calibration Utility")
    parser.add_argument(
        "--arm",
        choices=["leader", "follower", "both"],
        default=None,
        help="Specify which arm to calibrate: leader, follower, or both"
    )
    args = parser.parse_args()

    arm_choice = args.arm
    if not arm_choice:
        print_banner("SO-100 INTERACTIVE CALIBRATION ASSISTANT")
        print("Select which arm to calibrate:")
        print("  [1] Leader Arm   (Teleoperator - Passive / Human-driven)")
        print("  [2] Follower Arm (Robot - Powered)")
        print("  [3] Both Arms    (Leader first, then Follower)")
        print("  [q] Quit")
        choice = input("\nEnter choice (1, 2, 3, or q): ").strip().lower()
        if choice == "1":
            arm_choice = "leader"
        elif choice == "2":
            arm_choice = "follower"
        elif choice == "3":
            arm_choice = "both"
        else:
            print("Exiting.")
            return

    if arm_choice in ["leader", "both"]:
        success = calibrate_device("leader", force_fresh=True)
        if not success:
            print("[WARN] Leader calibration was not completed successfully.")
            if arm_choice == "both":
                cont = input("\nContinue to Follower arm anyway? (y/n): ").strip().lower()
                if cont != "y":
                    return

    if arm_choice in ["follower", "both"]:
        calibrate_device("follower", force_fresh=True)

    print("\n[DONE] Calibration process complete!")
    print("You can verify movement now using: bash bringup/teleoperation.sh")

if __name__ == "__main__":
    main()
