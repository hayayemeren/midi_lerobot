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

## 5. Arm Calibration Guide (Hugging Face LeRobot Method)

Calibration ensures that both the Leader arm and the Follower arm share the exact same physical reference coordinate system and joint angle values. This is critical for imitation learning so demonstrations collected by the leader map 1-to-1 to the follower.

### How LeRobot Calibration Works (2 Steps)

Hugging Face LeRobot calibrates Feetech STS3215 servos in two distinct steps:
1. **Half-Turn Homing Offset (Center Pose):**
   - You place the arm in the middle of its workspace.
   - LeRobot reads the current raw 12-bit encoder position (`0` to `4095`) and calculates a `Homing_Offset` so that this resting pose corresponds exactly to the center midpoint (`2047`).
2. **Range of Motion Limits (Min & Max):**
   - You gently move each joint through its physical end stops.
   - LeRobot records the minimum and maximum encoder positions and writes them to the servo EEPROM registers (`Min_Position_Limit` and `Max_Position_Limit`).
   - *(Note: Motor 5 `wrist_roll` is a 360° continuous rotation joint and is automatically assigned `[0, 4095]` without manual recording).*

---

### Running the Calibration Script

You can calibrate either arm interactively or with direct flags:

#### Option A: Interactive Menu
```bash
python bringup/calibrate_arm.py
# Or:
bash bringup/calibrate.sh
```
Choose:
- `[1]` Leader Arm
- `[2]` Follower Arm
- `[3]` Both Arms

#### Option B: Direct Shell Shortcuts
```bash
# Calibrate Leader Arm
bash bringup/calibrate_leader.sh

# Calibrate Follower Arm
bash bringup/calibrate_follower.sh
```

*(You can also run Hugging Face's raw CLI directly if preferred:)*
```bash
lerobot-calibrate --teleop.type=so100_leader --teleop.id=so100_leader --teleop.port=/dev/ttyACM1
lerobot-calibrate --robot.type=so100_follower --robot.id=so100_follower --robot.port=/dev/ttyACM0
```

---

### Step-by-Step Calibration Walkthrough

1. **Activate Conda Environment:**
   ```bash
   conda activate lerobot
   cd ~/lerobot
   ```

2. **Step 1 - Center Pose (Midpoint):**
   The script disables motor torque so you can move the arm freely. Place all joints in their neutral midpoint:
   - **Shoulder Pan:** Centered pointing directly forward (0°).
   - **Shoulder Lift:** Neutral upright position (~45° to 90°).
   - **Elbow Flex:** Bent at a 90° angle.
   - **Wrist Flex:** Centered straight in line with forearm.
   - **Wrist Roll:** Neutral / unrotated.
   - **Gripper:** Half-way open (~50%).
   - Press **`Enter`** in the terminal to lock in the midpoint homing offsets.

3. **Step 2 - Range of Motion:**
   A live encoder table will begin streaming on your screen. Slowly and gently move each joint to its physical limits:
   - Rotate **Shoulder Pan** fully to the left, then fully to the right.
   - Move **Shoulder Lift** fully back, then forward.
   - Move **Elbow Flex** fully in, then fully outstretched.
   - Move **Wrist Flex** fully up, then fully down.
   - Squeeze the **Gripper** completely closed, then pull it completely open.
   - Press **`Enter`** once all joints have reached their physical limits.

4. **Step 3 - Automatic Programming & Backup:**
   The script will:
   - Program the new limits directly into the servo EEPROM.
   - Save the calibration to `~/.cache/huggingface/lerobot/calibration/`.
   - Automatically back up the JSON file to `calibration/so100_leader.json` (or `so100_follower.json`) in the repository.
   - Display a summary table showing min, max, and degrees range for every joint.

5. **Verify Calibration:**
   Run the teleoperation script to verify smooth 1-to-1 mirroring:
   ```bash
   bash bringup/teleoperation.sh
   ```

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
