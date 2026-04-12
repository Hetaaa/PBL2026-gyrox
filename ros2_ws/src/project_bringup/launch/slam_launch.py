#!/usr/bin/env python3
"""Launch RGBD sync and RTAB-Map for a single camera."""

import yaml

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
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
    rtabmap_config = LaunchConfiguration("rtabmap_config")
    rgbd_sync_config = LaunchConfiguration("rgbd_sync_config")

    camera_name, _camera_data = _load_primary_camera(camera_config_file)
    if camera_name is None:
        print(f"⚠️  No enabled cameras found in {camera_config_file}")
        return []

    rgbd_sync_node = Node(
        package="rtabmap_sync",
        executable="rgbd_sync",
        name="rgbd_sync",
        namespace=camera_name,
        output="screen",
        parameters=[rgbd_sync_config],
        remappings=[
            ("rgb/image", f"/{camera_name}/camera/color/image_raw"),
            ("rgb/camera_info", f"/{camera_name}/camera/color/camera_info"),
            ("depth/image", f"/{camera_name}/camera/aligned_depth_to_color/image_raw"),
            ("rgbd_image", f"/{camera_name}/rgbd_image"),
        ],
    )

    rtabmap_node = Node(
        package="rtabmap_slam",
        executable="rtabmap",
        name="rtabmap",
        output="screen",
        parameters=[rtabmap_config, {"rgbd_cameras": 1}],
        remappings=[
            ("/tf", "/tf"),
            ("/tf_static", "/tf_static"),
            ("odom", "/rtabmap/odom"),
            ("odom_info", "/rtabmap/odom_info"),
            ("rgbd_image", f"/{camera_name}/rgbd_image"),
        ],
        arguments=["--delete_db_on_start"],
    )

    return [rgbd_sync_node, rtabmap_node]


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
