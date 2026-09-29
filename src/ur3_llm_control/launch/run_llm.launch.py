import os
import yaml
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from moveit_configs_utils import MoveItConfigsBuilder

def load_yaml(package_name, file_path):
    package_path = get_package_share_directory(package_name)
    absolute_file_path = os.path.join(package_path, file_path)
    try:
        with open(absolute_file_path, 'r') as file:
            return yaml.safe_load(file)
    except OSError:
        return None

def generate_launch_description():
    # Tải các thông số cấu hình cốt lõi của MoveIt 2
    moveit_config = (
        MoveItConfigsBuilder("ur3e_bot", package_name="moveit2_ur3e_config")
        .trajectory_execution(file_path="config/moveit_controllers.yaml")
        .to_moveit_configs()
    )

    # Đọc trực tiếp file OMPL
    ompl_planning_yaml = load_yaml("moveit2_ur3e_config", "config/ompl_planning.yaml")

    # Tạo một dictionary mới chứa cấu hình ompl
    ompl_config = {"ompl": ompl_planning_yaml}

    # Bắt buộc các cấu hình để MoveItPy nhận diện pipeline
    pipeline_config = {
        "planning_pipelines": ["ompl"],
        "default_planning_pipeline": "ompl"
    }

    # Tổng hợp tất cả các thông số
    parameters_list = [
        moveit_config.to_dict(),
        ompl_config,
        pipeline_config,
        {'use_sim_time': False}
    ]

    llm_controller_node = Node(
        package="ur3_llm_control",
        executable="skill_executor",
        name="skill_executor",
        parameters=parameters_list,
        output="screen",
        emulate_tty=True
    )

    return LaunchDescription([llm_controller_node])