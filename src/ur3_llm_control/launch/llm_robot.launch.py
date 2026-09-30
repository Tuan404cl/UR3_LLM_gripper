"""Launch the UR3e MoveIt demo and the task environment.

The default mode opens MoveIt in RViz for manual planning and execution with
the configured fake ros2_control system. Set start_skill_executor:=true to
also enable the interactive natural-language CLI.
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    moveit_demo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory("moveit2_ur3e_config"),
                "launch",
                "demo.launch.py",
            )
        )
    )

    zone_transforms = [
        Node(
            package="tf2_ros",
            executable="static_transform_publisher",
            name="zone_a_tf",
            arguments=["0.3", "0.2", "0.0", "0", "0", "0", "base_link", "zone_a"],
        ),
        Node(
            package="tf2_ros",
            executable="static_transform_publisher",
            name="zone_b_tf",
            arguments=["0.3", "0.0", "0.0", "0", "0", "0", "base_link", "zone_b"],
        ),
        Node(
            package="tf2_ros",
            executable="static_transform_publisher",
            name="zone_c_tf",
            arguments=["0.3", "-0.2", "0.0", "0", "0", "0", "base_link", "zone_c"],
        ),
    ]

    zone_visualizer = Node(
        package="ur3_llm_control",
        executable="zone_visualizer",
        name="zone_visualizer_node",
        output="screen",
    )

    skill_executor = Node(
        package="ur3_llm_control",
        executable="skill_executor",
        name="skill_executor",
        output="screen",
        emulate_tty=True,
        condition=IfCondition(LaunchConfiguration("start_skill_executor")),
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "start_skill_executor",
                default_value="false",
                description=(
                    "Start the interactive LLM CLI as well as MoveIt/RViz. "
                    "It waits for USER COMMAND after initialization."
                ),
            ),
            moveit_demo,
            *zone_transforms,
            zone_visualizer,
            skill_executor,
        ]
    )
