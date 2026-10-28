# SO-100 Robot Setup: Sock Tidying Task ("Tidy Up The Socks")

This repository is prepared for data collection, imitation learning, and autonomous evaluation using a **1 Leader arm** and **1 Follower arm** (SO-100) setup with a USB camera.

---

## 1. Hardware Architecture & Port Mapping

| Component | Port Path | Persistent by-id Link | Motor Protocol | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Leader Arm** (Teleop) | `/dev/ttyACM1` | `/dev/serial/by-id/usb-1a86_USB_Single_Serial_5AE6084621-if00` | Feetech STS3215 (IDs 1-6) | Passive / Teleoperator (Human-driven) |
| **Follower Arm** (Robot) | `/dev/ttyACM0` | `/dev/serial/by-id/usb-1a86_USB_Single_Serial_5AE6084008-if00` | Feetech STS3215 (IDs 1-6) | Actuated (Mirrors Leader) |
| **Camera** (Overhead/Front) | `/dev/video0` | `/dev/v4l/by-id/usb-Sonix_Technology_Co.__Ltd._USB2.0_CAM1_USB2.0_CAM1-video-index0` | V4L2 / OpenCV | 640x480 @ 30 FPS (MJPG) |

> **Calibration Files:** Pre-calibrated angle ranges and homing offsets are stored in:
> - `calibration/so100_leader.json`
> - `calibration/so100_follower.json`
>
> The scripts automatically copy these to `~/.cache/huggingface/lerobot/calibration/` if needed.

---

## 2. Environment Activation

Always activate the `lerobot` conda environment:

```bash
conda activate lerobot
cd ~/lerobot
```

Ensure serial and camera permissions (if needed):
```bash
sudo chmod 666 /dev/ttyACM* /dev/video*
```

---

## 3. Step-by-Step Workflow

### Step 1: Run Hardware Diagnostic
Run this script to verify that both arms and the camera are communicating cleanly:
```bash
python bringup/test_hardware.py
```
You should see `[OK]` for Leader arm, Follower arm, and Camera.

---

### Step 2: Test Teleoperation (Mirroring)
Test live teleoperation without recording:
```bash
bash bringup/teleoperation.sh
```
Move the Leader arm by hand. The Follower arm will mirror your movements in real-time.  
Press `Ctrl+C` in the terminal to stop teleoperation.

---

### Step 3: Collect Data for "Tidy Up The Socks"
Place socks and the storage basket/container in the robot workspace.

Start recording episodes:
```bash
bash bringup/data_collection.sh
```

#### During Recording:
- **`c` (Continue / Capture):**
  - Press `c` to start recording an episode.
  - Teleoperate the leader arm to grasp a sock and place/tidy it up.
  - Press `c` again once the sock is tidied to finish the episode early.
- **`r` (Redo):**
  - If you dropped the sock or made a mistake, press `r`. The current episode will be discarded, and you can re-record it immediately.
- **Reset time (15s):**
  - You have 15 seconds between episodes to reposition socks for the next demonstration.
- **Stopping session:**
  - Press `Ctrl+C` or type `exit` to stop recording. Your recorded episodes are safely saved locally.

#### Customizing Dataset Parameters:
You can change the number of episodes or repository ID by passing environment variables:
```bash
REPO_ID="hayayemeren/tidy_socks" NUM_EPISODES=50 EPISODE_TIME_S=60 bash bringup/data_collection.sh
```

---

### Step 4: Visualize Recorded Dataset
Review your recorded demonstrations to inspect joint actions, camera frames, and timings:
```bash
bash bringup/visualize_dataset.sh hayayemeren/tidy_socks 0
```
*(Replace `0` with any episode number to inspect)*

---

### Step 5: Train an Imitation Learning Policy (ACT or Diffusion)

#### Option A: Train ACT (Action Chunking with Transformers - Recommended)
```bash
bash bringup/train_act.sh hayayemeren/tidy_socks
```
- By default trains for 100,000 steps with checkpoints saved in `outputs/train/tidy_socks_act/checkpoints/`.

#### Option B: Train Diffusion Policy
```bash
bash bringup/train_diffusion.sh hayayemeren/tidy_socks
```
- Trains a Diffusion policy with checkpoints saved in `outputs/train/tidy_socks_diffusion/checkpoints/`.

---

### Step 6: Deploy and Evaluate Autonomous Policy
Run the trained model autonomously on the follower arm:
```bash
bash bringup/evaluate_policy.sh outputs/train/tidy_socks_act/checkpoints/last/pretrained_model
```
The follower robot will observe the workspace through `/dev/video0` and execute the sock tidying policy autonomously!

---

## 4. Recalibration (If Ever Needed)

If an arm is mechanically adjusted or rebuilt, recalibrate using:

- **Calibrate Leader Arm:**
  ```bash
  bash bringup/calibrate_leader.sh
  ```
- **Calibrate Follower Arm:**
  ```bash
  bash bringup/calibrate_follower.sh
  ```

Follow the prompts on screen:
1. Move the arm to the center / resting position and press Enter.
2. Move each joint through its full range of motion.
The scripts will automatically update the calibration files.

---

## 5. Troubleshooting

- **Permission Denied on `/dev/ttyACM*`:**
  Run `sudo usermod -aG dialout,video maksimgorki` and log out/in, or run `sudo chmod 666 /dev/ttyACM*`.
- **Port Inversion (Leader moving Follower backwards):**
  The scripts use persistent `/dev/serial/by-id/` paths (`5AE6084621` for Leader, `5AE6084008` for Follower) to ensure ports are never swapped even after reboots.
- **Communication Timeout:**
  Our drivers in `src/lerobot/motors/motors_bus.py` and `so_follower.py` include automatic retries (`num_retry=5`) and camera reconnection logic to prevent dropouts during long collection runs.
