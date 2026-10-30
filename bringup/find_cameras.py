#!/usr/bin/env python3
"""
Interactive camera discovery and diagnostic tool for LeRobot.
Detects all connected USB cameras, tests frame capture, saves snapshot previews,
and displays configuration paths for bringup/config.json.
"""

import os
import glob
import subprocess
from pathlib import Path
import cv2

def get_v4l_mapping():
    """Maps /dev/videoX to persistent /dev/v4l/by-id or by-path names."""
    mapping = {}
    by_id_dir = Path("/dev/v4l/by-id")
    if by_id_dir.exists():
        for link in by_id_dir.glob("*"):
            try:
                target = str(link.resolve())
                if target not in mapping:
                    mapping[target] = []
                mapping[target].append(str(link))
            except Exception:
                pass
                
    by_path_dir = Path("/dev/v4l/by-path")
    if by_path_dir.exists():
        for link in by_path_dir.glob("*"):
            try:
                target = str(link.resolve())
                if target not in mapping:
                    mapping[target] = []
                mapping[target].append(str(link))
            except Exception:
                pass
    return mapping

def main():
    print("==========================================================")
    print("           LeRobot Camera Discovery Utility              ")
    print("==========================================================")
    
    video_devices = sorted(glob.glob("/dev/video*"))
    if not video_devices:
        print("\n[WARN] No /dev/video* devices found on this system!")
        print("Please check:")
        print("  1. Are your USB cameras plugged securely into the computer?")
        print("  2. Check 'lsusb' to verify physical connection.")
        print("  3. Check 'sudo dmesg -T | grep -i uvc' for kernel messages.")
        print("==========================================================")
        return

    v4l_map = get_v4l_mapping()
    output_dir = Path("outputs/camera_check")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\nScanning {len(video_devices)} video device node(s)...\n")
    
    working_cameras = []
    
    for dev in video_devices:
        cap = cv2.VideoCapture(dev, cv2.CAP_V4L2)
        if not cap.isOpened():
            # Try default backend
            cap = cv2.VideoCapture(dev)
            
        if not cap.isOpened():
            continue
            
        ret, frame = cap.read()
        if not ret or frame is None:
            cap.release()
            continue
            
        h, w, c = frame.shape
        fps = cap.get(cv2.CAP_PROP_FPS)
        cap.release()
        
        # Save snapshot
        dev_clean = dev.replace("/dev/", "")
        snapshot_path = output_dir / f"{dev_clean}.jpg"
        cv2.imwrite(str(snapshot_path), frame)
        
        persistent_links = v4l_map.get(dev, [])
        best_path = persistent_links[0] if persistent_links else dev
        
        working_cameras.append({
            "dev": dev,
            "best_path": best_path,
            "all_links": persistent_links,
            "width": w,
            "height": h,
            "fps": fps if fps > 0 else 30.0,
            "snapshot": str(snapshot_path)
        })
        
        print(f"[FOUND] Camera at: {dev}")
        print(f"   - Resolution: {w}x{h} ({c} channels)")
        print(f"   - Snapshot saved to: {snapshot_path}")
        if persistent_links:
            print("   - Persistent symlinks:")
            for link in persistent_links:
                print(f"       * {link}")
        print()

    print("==========================================================")
    print(f"Summary: Found {len(working_cameras)} active streaming camera(s).")
    print("==========================================================")
    
    if len(working_cameras) == 0:
        print("No active camera streams could be opened.")
        print("If cameras are plugged in, ensure permissions via: sudo chmod 666 /dev/video*")
    else:
        print("\nTo configure your wrist and scene cameras in bringup/config.json:")
        print("Open the saved snapshot images (in outputs/camera_check/) to confirm")
        print("which camera is at the robot wrist and which camera views the scene.\n")
        print("Then update the 'cameras' section in bringup/config.json:")
        print("{")
        print('  "cameras": {')
        for i, cam in enumerate(working_cameras):
            cam_name = "wrist" if i == 0 else ("scene" if i == 1 else f"cam_{i}")
            print(f'    "{cam_name}": {{')
            print(f'      "enabled": true,')
            print(f'      "type": "opencv",')
            print(f'      "index_or_path": "{cam["best_path"]}",')
            print(f'      "fallback_path": "{cam["dev"]}",')
            print(f'      "width": {cam["width"]},')
            print(f'      "height": {cam["height"]},')
            print(f'      "fps": 30,')
            print(f'      "fourcc": "MJPG"')
            print('    }' + ("," if i < len(working_cameras)-1 else ""))
        print("  }")
        print("}")
        print("==========================================================")

if __name__ == "__main__":
    main()
