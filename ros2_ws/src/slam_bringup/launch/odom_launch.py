#!/usr/bin/env python3
"""Launch IMU preprocessing, Madgwick and stereo odometry."""

import yaml

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction, TimerAction
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def _load_primary_camera(config_file):
    with open(config_file, "r", encoding="utf-8") as file_handle:
        config = yaml.safe_load(file_handle) or {}

    for camera_name, camera_data in config.get("cameras", {}).items():
        if camera_data.get("enabled", True):
            return camera_name, camera_data
    return None, None


def launch_setup(context, *args, **kwargs):
    camera_config_file = LaunchConfiguration("camera_config").perform(context)
    madgwick_config = LaunchConfiguration("madgwick_config")
    stereo_odometry_config = LaunchConfiguration("stereo_odometry_config")

    camera_name, _camera_data = _load_primary_camera(camera_config_file)
    if camera_name is None:
        print(f"⚠️  No enabled cameras found in {camera_config_file}")
        return []

    camera_imu_topic = f"/{camera_name}/camera/imu"
    imu_in_base_topic = f"/{camera_name}/camera/imu_in_base"

    imu_transformer_node = Node(
        package="slam_bringup",
        executable="imu_transformer",
        name="imu_transformer",
        output="log",
        parameters=[
            {
                "target_frame": "base_link",
                "input_topic": camera_imu_topic,
                "output_topic": imu_in_base_topic,
                "invert_x": False,
                "invert_y": False,
                "invert_z": False,
            }
        ],
    )

    madgwick_node = Node(
        package="imu_filter_madgwick",
        executable="imu_filter_madgwick_node",
        name="imu_filter_madgwick",
        output="log",
        parameters=[madgwick_config],
        remappings=[
            ("imu/data_raw", imu_in_base_topic),
            ("imu/data", "/imu/data"),
        ],
    )

    stereo_odometry_node = Node(
        package="rtabmap_odom",
        executable="stereo_odometry",
        name="stereo_odometry",
        namespace="rtabmap",
        output="log",
        parameters=[stereo_odometry_config],
        remappings=[
            ("/tf", "/tf"),
            ("/tf_static", "/tf_static"),
            ("imu", "/imu/data"),
            ("left/image_rect", f"/{camera_name}/camera/infra1/image_rect_raw"),
            ("left/camera_info", f"/{camera_name}/camera/infra1/camera_info"),
            ("right/image_rect", f"/{camera_name}/camera/infra2/image_rect_raw"),
            ("right/camera_info", f"/{camera_name}/camera/infra2/camera_info"),
        ],
        arguments=["--ros-args", "--log-level", "INFO"],
    )

    # Avoid spawning ros2 CLI helper processes (can trigger FastDDS SHM lock errors).
    # Start nodes in sequence with short delays instead.
    start_madgwick_after_imu = TimerAction(period=1.0, actions=[madgwick_node])
    start_stereo_after_filtered_imu = TimerAction(period=2.0, actions=[stereo_odometry_node])

    return [
        imu_transformer_node,
        start_madgwick_after_imu,
        start_stereo_after_filtered_imu,
    ]


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "camera_config",
                default_value=PathJoinSubstitution(
                    [FindPackageShare("slam_bringup"), "config", "cameras.yaml"]
                ),
                description="Path to the camera configuration YAML file",
            ),
            DeclareLaunchArgument(
                "madgwick_config",
                default_value=PathJoinSubstitution(
                    [
                        FindPackageShare("slam_bringup"),
                        "config",
                        "odom",
                        "madgwick_params.yaml",
                    ]
                ),
                description="Path to the Madgwick configuration YAML file",
            ),
            DeclareLaunchArgument(
                "stereo_odometry_config",
                default_value=PathJoinSubstitution(
                    [
                        FindPackageShare("slam_bringup"),
                        "config",
                        "odom",
                        "stereo_odometry_params.yaml",
                    ]
                ),
                description="Path to the stereo odometry configuration YAML file",
            ),
            OpaqueFunction(function=launch_setup),
        ]
    )
