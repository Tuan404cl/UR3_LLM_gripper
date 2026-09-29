import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_llm_control = get_package_share_directory('ur3_llm_control')
    
    # 1. Gọi file demo.launch.py từ moveit2_ur3e_config
    ur3e_moveit_demo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('moveit2_ur3e_config'), 'launch', 'demo.launch.py')
        )
    )

    # 2. Khai báo tọa độ tĩnh (Static TFs) cho 3 Zone
    zone_a_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='zone_a_tf',
        arguments=['0.3', '0.2', '0.0', '0', '0', '0', 'base_link', 'zone_a']
    )
    
    zone_b_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='zone_b_tf',
        arguments=['0.3', '0.0', '0.0', '0', '0', '0', 'base_link', 'zone_b']
    )
    
    zone_c_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='zone_c_tf',
        arguments=['0.3', '-0.2', '0.0', '0', '0', '0', 'base_link', 'zone_c']
    )

    # 3. Khai báo Node vẽ hình Marker (Zone Visualizer)
    visualizer_node = Node(
        package='ur3_llm_control',
        executable='zone_visualizer',
        name='zone_visualizer_node'
    )

    # 4. Trả về mảng Launch
    return LaunchDescription([
        ur3e_moveit_demo,
        zone_a_tf,
        zone_b_tf,
        zone_c_tf,
        visualizer_node
    ])