#!/usr/bin/env python3
"""Launch one RealSense camera from a YAML config."""

import yaml

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo, OpaqueFunction
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def _flatten_params(data, parent_key="", sep="."):
    items = []
    for key, value in data.items():
        new_key = parent_key + sep + key if parent_key else key
        if isinstance(value, dict):
            items.extend(_flatten_params(value, new_key, sep=sep).items())
        else:
            items.append((new_key, value))
    return dict(items)


def _load_primary_camera(config_file):
    with open(config_file, "r", encoding="utf-8") as file_handle:
        config = yaml.safe_load(file_handle) or {}

    cameras = config.get("cameras", {})
    for camera_name, camera_data in cameras.items():
        if camera_data.get("enabled", True):
            return camera_name, camera_data
    return None, None


def launch_setup(context, *args, **kwargs):
    config_file = LaunchConfiguration("config_file").perform(context)
    camera_name, camera_data = _load_primary_camera(config_file)

    if camera_name is None:
        print(f"⚠️  No enabled cameras found in {config_file}")
        return []

    ros_params = camera_data.get("ros__parameters", {}).copy()
    ros_params["serial_no"] = str(camera_data.get("serial_number", ""))
    ros_params["camera_name"] = camera_name

    flat_params = _flatten_params(ros_params)

    return [
        Node(
            package="realsense2_camera",
            executable="realsense2_camera_node",
            name="camera",
            namespace=camera_name,
            parameters=[flat_params],
            remappings=[
                ("/tf", "/tf"),
                ("/tf_static", "/tf_static"),
            ],
            output="screen",
            emulate_tty=True,
        )
    ]


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "config_file",
                default_value=PathJoinSubstitution(
                    [FindPackageShare("slam"), "config", "cameras.yaml"]
                ),
                description="Path to the camera configuration YAML file",
            ),
            LogInfo(msg="Starting one RealSense D435i camera"),
            OpaqueFunction(function=launch_setup),
        ]
    )
