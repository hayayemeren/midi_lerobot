# 🧦 SO-100 Robot Learning: Tidy Up The Socks

An end-to-end physical AI and imitation learning robotics project built on top of [Hugging Face LeRobot](https://github.com/huggingface/lerobot). This repository is custom-configured for an **SO-100 6-DOF dual-arm setup (1 Leader + 1 Follower)** equipped with **synchronized multi-camera vision (Wrist + Scene)** to learn the autonomous manipulation task: **"Tidy Up The Socks"**.

---

## 📌 Project Overview & System Setup

The goal of this project is to collect human teleoperation demonstrations and train deep imitation learning policies (such as **ACT** and **Diffusion Policy**) so that the robot can autonomously identify, grasp, and tidy socks into a target container.

### 🤖 Hardware Architecture

| Component | Default Port | Persistent Link | Description |
| :--- | :--- | :--- | :--- |
| **Leader Arm** | `/dev/ttyACM1` | `/dev/serial/by-id/usb-1a86_USB_Single_Serial_5AE6084621-if00` | Passive teleoperator arm manipulated by human demonstrator |
| **Follower Arm** | `/dev/ttyACM0` | `/dev/serial/by-id/usb-1a86_USB_Single_Serial_5AE6084008-if00` | Powered 6-DOF robot arm with Feetech STS3215 servos |
| **Wrist Camera** | `/dev/video0` | `/dev/v4l/by-id/...` | End-effector closeup view mounted directly on the gripper |
| **Scene Camera** | `/dev/video2` | `/dev/v4l/by-id/...` | Static overhead / overview perspective of the entire table |

---

## 🛠️ What We Did in This Project

We extended and hardened the baseline LeRobot system for real-world SO-100 deployment:

1. **Centralized Configuration System (`bringup/config.json`):**
   - Created a single, unified JSON configuration file controlling all hardware ports, camera device paths, dataset metadata, and training parameters.
   - Built `bringup/config_helper.py` to dynamically resolve persistent `/dev/serial/by-id/` links, eliminating port swapping bugs.

2. **Synchronized Multi-Camera Vision (Wrist + Scene):**
   - Configured dual-stream camera capture (`observation.images.wrist` and `observation.images.scene`) at 30 FPS.
   - Created `bringup/find_cameras.py` to auto-detect video devices, inspect resolutions, and save preview snapshots.

3. **Live Camera Web Streamer & Focus Tool (`bringup/view_camera.py`):**
   - Developed a lightweight HTTP MJPEG stream server with dynamic network IP detection.
   - Integrated a real-time **Laplacian Focus Sharpness Score** allowing easy physical adjustment of M12 manual-focus camera lenses via a browser on any phone or laptop.

4. **Guided Interactive Calibration Assistant (`bringup/calibrate_arm.py`):**
   - Designed a guided assistant implementing LeRobot's official 2-step calibration (half-turn midpoint homing + physical range-of-motion discovery).
   - Automatically programs servo EEPROM registers and backs up calibration JSON profiles to `calibration/`.

5. **Driver Hardening & Robustness Fixes (`src/`):**
   - Added automatic serial retries (`num_retry=5`) in `motors_bus.py`, `so_follower.py`, and `so_leader.py` to prevent communication dropouts during long recording sessions.
   - Enhanced camera error-handling and reconnect routines in `camera_opencv.py`.
   - Fixed tensor detachment for Rerun visualization in `visualization_utils.py`.

6. **Automated End-to-End Bringup Pipeline:**
   - Complete suite of reproducible scripts for diagnostic checks, interactive teleoperation, recording with keyboard redo/fast-forward controls, policy training, and autonomous evaluation.

---

## 📂 Repository Structure

```text
├── bringup/
│   ├── config.json             # Central configuration (ports, cameras, dataset, policy)
│   ├── config_helper.py        # Config parser & bash environment exporter
│   ├── test_hardware.py        # Diagnostic script checking arms, servos & cameras
│   ├── find_cameras.py         # Auto-detection utility for USB video devices
│   ├── view_camera.py          # Web streaming server with real-time focus sharpness HUD
│   ├── view_camera.sh          # Quick launch script for camera viewer
│   ├── calibrate_arm.py        # Interactive guided calibration assistant
│   ├── calibrate.sh            # Calibration wrapper script
│   ├── calibrate_leader.sh     # Shortcut to calibrate leader arm
│   ├── calibrate_follower.sh   # Shortcut to calibrate follower arm
│   ├── teleoperation.sh        # Live teleoperation (mirroring) script
│   ├── quick_teleop_test.py    # 10-second mirroring verification test
│   ├── data_collection.sh      # Dual-camera dataset recording pipeline
│   ├── visualize_dataset.sh    # Replay demonstrations in Rerun visualizer
│   ├── train_act.sh            # Train Action Chunking with Transformers (ACT)
│   ├── train_diffusion.sh      # Train Diffusion Policy
│   └── evaluate_policy.sh      # Autonomous evaluation on the follower arm
├── calibration/                # Tracked JSON calibration profiles for leader & follower
├── src/lerobot/                # Core LeRobot library with driver improvements
└── HOW_TO_USE_SO100_SOCKS.md   # Extended step-by-step operating manual
```

---

## 🚀 How to Use the Codes

### 1. Environment & Permissions
Activate the Conda environment and verify serial / video group permissions:
```bash
conda activate lerobot
cd ~/lerobot

# Ensure dialout and video permissions (if not already added)
sudo usermod -aG dialout,video $USER
```

---

### 2. Configure Hardware (`bringup/config.json`)
Edit [`bringup/config.json`](bringup/config.json) if you need to adjust ports, camera paths, or dataset parameters:
```json
{
  "leader": {
    "port": "/dev/serial/by-id/usb-1a86_USB_Single_Serial_5AE6084621-if00",
    "fallback_port": "/dev/ttyACM1"
  },
  "follower": {
    "port": "/dev/serial/by-id/usb-1a86_USB_Single_Serial_5AE6084008-if00",
    "fallback_port": "/dev/ttyACM0"
  },
  "cameras": {
    "wrist": {
      "enabled": true,
      "index_or_path": "/dev/v4l/by-id/usb-Sonix_Technology_Co.__Ltd._USB2.0_CAM1_USB2.0_CAM1-video-index0",
      "fallback_path": "/dev/video0"
    },
    "scene": {
      "enabled": true,
      "index_or_path": "/dev/video2",
      "fallback_path": "/dev/video2"
    }
  }
}
```

---

### 3. Check & Adjust Camera Focus
Most robot camera modules have a **manual focus ring**. To view the live video and adjust focus:
```bash
bash bringup/view_camera.sh
```
1. Open the URL shown in your terminal (e.g., `http://<YOUR_ROBOT_IP>:8080`) in a browser on your phone or laptop.
2. Slowly twist the physical lens barrel on the camera.
3. Watch the live **Focus Sharpness Score** HUD on screen — stop when the score hits its peak and the socks are crisp.
4. Press `Ctrl+C` to stop the viewer.

---

### 4. Run Hardware Diagnostic
Verify that both arms and both cameras communicate cleanly:
```bash
python bringup/test_hardware.py
```
*Expected: `[OK]` for Leader, Follower, Wrist Camera, and Scene Camera.*

---

### 5. Calibrate the Arms (If Rebuilt or Adjusted)
If servo horns or mounts have been moved, run the calibration assistant:
```bash
python bringup/calibrate_arm.py
# Or:
bash bringup/calibrate.sh
```
- **Step 1:** Place the arm in the **center/neutral resting pose** and press `Enter` to set homing offsets.
- **Step 2:** Gently move each joint through its **physical range limits** and press `Enter`.
- The script automatically writes limits to the servo EEPROMs and saves backups in `calibration/`.

---

### 6. Practice Teleoperation (Mirroring)
Before recording, test live mirroring to ensure smooth joint response:
```bash
bash bringup/teleoperation.sh
```
- Move the Leader arm by hand; the Follower arm follows in real-time.
- Press `Ctrl+C` in the terminal to stop teleoperation.

---

### 7. Collect Demonstrations ("Tidy Up The Socks")
Arrange socks on the workspace table with the target container, then start recording:
```bash
bash bringup/data_collection.sh
```

#### Controls During Recording:
- **`c` (Continue / Capture):**
  - Press `c` to start recording an episode.
  - Teleoperate the arm to grasp and place the sock in the basket.
  - Press `c` again as soon as the sock is placed to end the episode early (avoids idle padding).
- **`r` (Redo):**
  - If you fumble, drop a sock, or make a mistake, press `r` to immediately discard the episode and re-record it.
- **Reset period (15s):**
  - Reposition socks with varied placements, rotations, and folds for the next episode.
- **Stop / Resume:**
  - Press `Ctrl+C` or type `exit` anytime. Demonstrations are safely stored in `~/.cache/huggingface/lerobot/`. Running the script again will resume seamlessly.

---

### 8. Visualize Recorded Dataset
Inspect your multi-camera recordings and joint trajectory data:
```bash
bash bringup/visualize_dataset.sh hayayemeren/tidy_socks 0
```

---

### 9. Train the Imitation Learning Policy

#### Option A: Train ACT (Action Chunking with Transformers - Recommended)
```bash
bash bringup/train_act.sh hayayemeren/tidy_socks
```
- Trains on joint states and both camera perspectives (`wrist` + `scene`).
- Checkpoints are saved under `outputs/train/tidy_socks_act/checkpoints/`.

#### Option B: Train Diffusion Policy
```bash
bash bringup/train_diffusion.sh hayayemeren/tidy_socks
```
- Trains a Diffusion policy saved under `outputs/train/tidy_socks_diffusion/checkpoints/`.

---

### 10. Deploy Autonomous Evaluation
Run the trained policy to control the follower arm autonomously:
```bash
bash bringup/evaluate_policy.sh outputs/train/tidy_socks_act/checkpoints/last/pretrained_model
```
The robot will stream inputs from both cameras and execute the sock tidying policy autonomously!

---

## 📖 Citation

This project is built upon the open-source **LeRobot** library:

```bibtex
@misc{cadene2024lerobot,
    author = {Cadene, Remi and Alibert, Simon and Soare, Alexander and Gallouedec, Quentin and Zouitine, Adil and Palma, Steven and Kooijmans, Pepijn and Aractingi, Michel and Shukor, Mustafa and Aubakirova, Dana and Russi, Martino and Capuano, Francesco and Pascal, Caroline and Choghari, Jade and Moss, Jess and Wolf, Thomas},
    title = {LeRobot: State-of-the-art Machine Learning for Real-World Robotics in Pytorch},
    howpublished = "\url{https://github.com/huggingface/lerobot}",
    year = {2024}
}
```

```bibtex
@inproceedings{cadenelerobot,
  title={LeRobot: An Open-Source Library for End-to-End Robot Learning},
  author={Cadene, Remi and Alibert, Simon and Capuano, Francesco and Aractingi, Michel and Zouitine, Adil and Kooijmans, Pepijn and Choghari, Jade and Russi, Martino and Pascal, Caroline and Palma, Steven and Shukor, Mustafa and Moss, Jess and Soare, Alexander and Aubakirova, Dana and Lhoest, Quentin and Gallou\'edec, Quentin and Wolf, Thomas},
  booktitle={The Fourteenth International Conference on Learning Representations},
  year={2026},
  url={https://arxiv.org/abs/2602.22818}
}
```
