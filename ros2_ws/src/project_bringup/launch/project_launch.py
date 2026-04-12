#!/usr/bin/env python3
"""Main bringup launch for the single-camera SLAM stack."""

import yaml

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription, OpaqueFunction, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
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
    camera_name, _camera_data = _load_primary_camera(camera_config_file)

    if camera_name is None:
        print(f"⚠️  No enabled cameras found in {camera_config_file}")
        return []

    transforms_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("slam"), "launch", "transforms_launch.py"]
            )
        ),
    )

    cameras_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("slam"), "launch", "cameras_launch.py"]
            )
        ),
        launch_arguments={"config_file": camera_config_file}.items(),
    )

    odom_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("slam"), "launch", "odom_launch.py"]
            )
        ),
        launch_arguments={
            "camera_config": camera_config_file,
            "madgwick_config": LaunchConfiguration("madgwick_config"),
            "stereo_odometry_config": LaunchConfiguration("stereo_odometry_config"),
        }.items(),
    )

    slam_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("slam"), "launch", "slam_launch.py"]
            )
        ),
        launch_arguments={
            "camera_config": camera_config_file,
            "rgbd_sync_config": LaunchConfiguration("rgbd_sync_config"),
            "rtabmap_config": LaunchConfiguration("rtabmap_config"),
        }.items(),
    )

    wait_for_camera_imu = ExecuteProcess(
        cmd=[
            "ros2",
            "topic",
            "echo",
            "--once",
            f"/{camera_name}/camera/imu",
            "sensor_msgs/msg/Imu",
        ],
        output="screen",
    )

    wait_for_rtabmap_odom = ExecuteProcess(
        cmd=[
            "ros2",
            "topic",
            "echo",
            "--once",
            "/rtabmap/odom",
            "nav_msgs/msg/Odometry",
        ],
        output="screen",
    )

    start_odom_after_camera_imu = RegisterEventHandler(
        OnProcessExit(target_action=wait_for_camera_imu, on_exit=[odom_launch, wait_for_rtabmap_odom])
    )

    start_slam_after_rtabmap_odom = RegisterEventHandler(
        OnProcessExit(target_action=wait_for_rtabmap_odom, on_exit=[slam_launch])
    )

    return [
        transforms_launch,
        cameras_launch,
        wait_for_camera_imu,
        start_odom_after_camera_imu,
        start_slam_after_rtabmap_odom,
    ]


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "camera_config",
                default_value=PathJoinSubstitution(
                    [FindPackageShare("slam"), "config", "cameras.yaml"]
                ),
                description="Path to the camera configuration YAML file",
            ),
            DeclareLaunchArgument(
                "madgwick_config",
                default_value=PathJoinSubstitution(
                    [
                        FindPackageShare("slam"),
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
                        FindPackageShare("slam"),
                        "config",
                        "odom",
                        "stereo_odometry_params.yaml",
                    ]
                ),
                description="Path to the stereo odometry configuration YAML file",
            ),
            DeclareLaunchArgument(
                "rgbd_sync_config",
                default_value=PathJoinSubstitution(
                    [
                        FindPackageShare("slam"),
                        "config",
                        "slam",
                        "rgbd_sync_params.yaml",
                    ]
                ),
                description="Path to the RGBD sync configuration YAML file",
            ),
            DeclareLaunchArgument(
                "rtabmap_config",
                default_value=PathJoinSubstitution(
                    [
                        FindPackageShare("slam"),
                        "config",
                        "slam",
                        "rtabmap_params.yaml",
                    ]
                ),
                description="Path to the RTAB-Map configuration YAML file",
            ),
            OpaqueFunction(function=launch_setup),
        ]
    )
