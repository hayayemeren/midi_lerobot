# SO-100 Robot Setup: Sock Tidying Task ("Tidy Up The Socks")

This repository is prepared for teleoperation, multi-view data collection, imitation learning, and autonomous policy deployment for the **Tidy Up The Socks** task using:
- **1 Leader arm** (SO-100 teleoperator)
- **1 Follower arm** (SO-100 robot)
- **2 Cameras**: **1 Wrist Camera** (mounted on robot wrist) + **1 Scene Camera** (workspace / table overview)

---

## 1. Central Configuration File (`bringup/config.json`)

All hardware ports, camera device paths, resolutions, and dataset hyperparameters are configured in a **single file**:
👉 **`bringup/config.json`**

Whenever you change USB ports, swap cameras, or adjust settings, edit **`bringup/config.json`**. All bringup scripts (`test_hardware.py`, `teleoperation.sh`, `data_collection.sh`, `evaluate_policy.sh`) automatically read from it!

```json
{
  "leader": {
    "type": "so100_leader",
    "id": "so100_leader",
    "port": "/dev/serial/by-id/usb-1a86_USB_Single_Serial_5AE6084621-if00",
    "fallback_port": "/dev/ttyACM1",
    "use_degrees": true
  },
  "follower": {
    "type": "so100_follower",
    "id": "so100_follower",
    "port": "/dev/serial/by-id/usb-1a86_USB_Single_Serial_5AE6084008-if00",
    "fallback_port": "/dev/ttyACM0",
    "use_degrees": true
  },
  "cameras": {
    "wrist": {
      "enabled": true,
      "type": "opencv",
      "index_or_path": "/dev/v4l/by-id/usb-Sonix_Technology_Co.__Ltd._USB2.0_CAM1_USB2.0_CAM1-video-index0",
      "fallback_path": "/dev/video0",
      "width": 640,
      "height": 480,
      "fps": 30,
      "fourcc": "MJPG"
    },
    "scene": {
      "enabled": true,
      "type": "opencv",
      "index_or_path": "/dev/video2",
      "fallback_path": "/dev/video2",
      "width": 640,
      "height": 480,
      "fps": 30,
      "fourcc": "MJPG"
    }
  },
  "dataset": {
    "repo_id": "hayayemeren/tidy_socks",
    "task": "Tidy up the socks.",
    "num_episodes": 50,
    "episode_time_s": 60,
    "reset_time_s": 15,
    "fps": 30,
    "push_to_hub": false
  }
}
```

---

## 2. Hardware Architecture & Port Mapping

| Component | Default Port Path | Persistent by-id Link | Protocol | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **Leader Arm** (Teleop) | `/dev/ttyACM1` | `/dev/serial/by-id/usb-1a86_USB_Single_Serial_5AE6084621-if00` | Feetech STS3215 (IDs 1-6) | Unpowered / Passive (Human control) |
| **Follower Arm** (Robot) | `/dev/ttyACM0` | `/dev/serial/by-id/usb-1a86_USB_Single_Serial_5AE6084008-if00` | Feetech STS3215 (IDs 1-6) | Powered (Mirrors Leader) |
| **Wrist Camera** | `/dev/video0` | `/dev/v4l/by-id/...` | V4L2 / OpenCV | End-effector closeup view |
| **Scene Camera** | `/dev/video2` | `/dev/v4l/by-id/...` | V4L2 / OpenCV | Table & workspace global view |

> **Calibration Files:** Pre-calibrated angle ranges and homing offsets are stored in:
> - `calibration/so100_leader.json`
> - `calibration/so100_follower.json`
>
> The scripts automatically copy these to `~/.cache/huggingface/lerobot/calibration/` if needed.

---

## 3. Detecting & Setting Up Your Cameras

When you plug in your two USB cameras:

1. Run the camera discovery utility:
   ```bash
   python bringup/find_cameras.py
   ```
2. The script will:
   - Scan all video device nodes.
   - Capture a sample frame from each working camera and save it to `outputs/camera_check/`.
   - Print the persistent `/dev/v4l/by-id/...` links and resolutions.
3. Check the images in `outputs/camera_check/` to see which camera is your **wrist** camera and which is your **scene** camera.
4. Copy the suggested paths into **`bringup/config.json`** under `"wrist"` and `"scene"`.
   *(If you only have one camera connected temporarily, set `"enabled": false` for the missing camera in `bringup/config.json`).*

---

## 4. Step-by-Step Workflow

### Step 1: Activate Environment
```bash
conda activate lerobot
cd ~/lerobot
```

Ensure device permissions (already configured for `maksimgorki` in `dialout` and `video` groups):
```bash
sudo chmod 666 /dev/ttyACM* /dev/video* 2>/dev/null || true
```

### Step 2: Run Hardware Diagnostic
Run this script to verify that both arms and both cameras are communicating cleanly:
```bash
python bringup/test_hardware.py
```
You should see:
- `[OK]` Leader Arm connected & joint positions read
- `[OK]` Follower Arm connected & joint positions read
- `[OK]` Wrist Camera: Successfully captured frame
- `[OK]` Scene Camera: Successfully captured frame

---

### Step 3: Test Teleoperation (Mirroring)
Test live teleoperation without recording to verify joint tracking:
```bash
bash bringup/teleoperation.sh
```
Move the Leader arm by hand. The Follower arm will mirror your movements in real-time.  
Press `Ctrl+C` in the terminal to stop teleoperation.

*(Alternatively, run `python bringup/quick_teleop_test.py` for a quick 10-second mirror test).*

---

### Step 4: Collect Data for "Tidy Up The Socks"
Place socks and the storage basket/container in the robot workspace.

Start recording demonstrations:
```bash
bash bringup/data_collection.sh
```

#### During Recording:
- Both the **wrist camera** and **scene camera** will record synchronized video frames.
- **`c` (Continue / Capture):**
  - Press `c` to start recording an episode demonstration.
  - Teleoperate the leader arm to grasp a sock and place/tidy it up.
  - Press `c` again once the sock is tidied to finish the episode early.
- **`r` (Redo):**
  - If you dropped the sock or made a mistake, press `r`. The current episode will be discarded and re-recorded immediately.
- **Reset time (15s):**
  - You have 15 seconds between episodes to reposition socks for the next demonstration.
- **Stopping session:**
  - Press `Ctrl+C` or type `exit` to stop recording. Your recorded episodes are safely saved locally in `~/.cache/huggingface/lerobot/`.

#### Overriding Parameters on the Fly:
You can override parameters without editing `config.json` via environment variables:
```bash
NUM_EPISODES=30 EPISODE_TIME_S=60 bash bringup/data_collection.sh
```

---

### Step 5: Visualize Recorded Dataset
Review your recorded demonstrations to inspect joint actions and multi-camera views (wrist + scene):
```bash
bash bringup/visualize_dataset.sh hayayemeren/tidy_socks 0
```
*(Replace `0` with any episode number to inspect)*

---

### Step 6: Train an Imitation Learning Policy (ACT or Diffusion)

#### Option A: Train ACT (Action Chunking with Transformers - Recommended)
```bash
bash bringup/train_act.sh hayayemeren/tidy_socks
```
- Trains on joint actions + both camera observations (wrist and scene).
- Checkpoints are saved in `outputs/train/tidy_socks_act/checkpoints/`.

#### Option B: Train Diffusion Policy
```bash
bash bringup/train_diffusion.sh hayayemeren/tidy_socks
```
- Trains a Diffusion policy with checkpoints saved in `outputs/train/tidy_socks_diffusion/checkpoints/`.

---

### Step 7: Deploy and Evaluate Autonomous Policy
Run the trained model autonomously on the follower arm:
```bash
bash bringup/evaluate_policy.sh outputs/train/tidy_socks_act/checkpoints/last/pretrained_model
```
The follower robot will stream frames from both the wrist and scene cameras and execute the learned policy autonomously!

---

## 5. Recalibration (If Ever Needed)

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
The scripts will automatically update the calibration files in `calibration/`.

---

## 6. Troubleshooting

- **"Could not open camera /dev/video0":**
  1. Plug in your USB cameras.
  2. Run `python bringup/find_cameras.py` to see which device nodes they were assigned.
  3. Update `bringup/config.json` with the detected paths.
- **Permissions:**
  Make sure your user has access to serial and video devices:
  `sudo usermod -aG dialout,video $USER`
- **Leader & Follower Ports Swapped:**
  The `bringup/config.json` uses persistent `/dev/serial/by-id/` paths (`5AE6084621` for Leader, `5AE6084008` for Follower) so they never swap even if unplugged and re-plugged.
