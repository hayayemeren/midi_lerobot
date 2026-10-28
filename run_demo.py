from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig
from lerobot.datasets.lerobot_dataset import LeRobotDataset
from lerobot.robots.so_follower import SOFollowerConfig
from lerobot.robots.bi_so_follower import BiSOFollower, BiSOFollowerConfig
from lerobot.policies.act.modeling_act import ACTPolicy
from lerobot.policies.factory import make_pre_post_processors
from lerobot.scripts.lerobot_record import record_loop
from lerobot.utils.control_utils import init_keyboard_listener
from lerobot.utils.utils import log_say
from lerobot.utils.visualization_utils import init_rerun

FPS = 30  # Must match the dataset and camera FPS (30fps)
EPISODE_TIME_SEC = 60
HF_MODEL_ID = "defneerkan/messy_towel_model"
HF_DATASET_ID = "maksimgorki/eval_towel_folding"

def main():
    # 1. Explicit Hardware Configuration
    camera_config = {"front": OpenCVCameraConfig(index_or_path=0, width=640, height=480, fps=FPS)}
    
    # Map the left and right arms to your specific Linux ports
    left_config = SOFollowerConfig(port="/dev/ttyACM3", id="left_follower", use_degrees=True)
    right_config = SOFollowerConfig(port="/dev/ttyACM2", id="right_follower", use_degrees=True)

    robot_config = BiSOFollowerConfig(
        left_arm_config=left_config,
        right_arm_config=right_config,
        cameras=camera_config
    )
    robot = BiSOFollower(robot_config)

    # 2. Load the Policy
    policy = ACTPolicy.from_pretrained(HF_MODEL_ID)

    # Override inference parameters (these don't affect model weights, only the action queue)
    # Use temporal ensembling: query the policy every step and blend action chunks smoothly
    policy.config.n_action_steps = 1
    policy.config.temporal_ensemble_coeff = 0.01
    policy.reset()  # Re-initialize the temporal ensembler with the new config

    # 3. Initialize Dataset Logger
    dataset = LeRobotDataset.create(
        repo_id=HF_DATASET_ID,
        fps=FPS,
        robot_type=robot.name,
        use_videos=True,
    )

    preprocessor, postprocessor = make_pre_post_processors(
        policy_cfg=policy,
        pretrained_path=HF_MODEL_ID,
        dataset_stats=dataset.meta.stats if hasattr(dataset, 'meta') else None,
    )

    # 4. Connect and Execute
    robot.connect()
    listener, events = init_keyboard_listener()
    init_rerun(session_name="bimanual_eval")

    try:
        if not robot.is_connected:
            raise ValueError("Robot is not connected!")

        print("Starting Bimanual evaluate loop...")
        record_loop(
            robot=robot,
            events=events,
            fps=FPS,
            policy=policy,
            preprocessor=preprocessor,
            postprocessor=postprocessor,
            dataset=dataset,
            control_time_s=EPISODE_TIME_SEC,
            display_data=True,
        )
    finally:
        log_say("Stop recording")
        robot.disconnect()
        listener.stop()

if __name__ == "__main__":
    main()
