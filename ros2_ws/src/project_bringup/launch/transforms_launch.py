#!/usr/bin/env python3
"""Publish robot TFs for the single-camera setup."""

import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo, OpaqueFunction
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def launch_setup(context, *args, **kwargs):
    urdf_file = PathJoinSubstitution(
        [FindPackageShare("slam"), "urdf", "phoenix.urdf"]
    ).perform(context)

    if not os.path.exists(urdf_file):
        raise FileNotFoundError(f"URDF file not found: {urdf_file}")

    with open(urdf_file, "r", encoding="utf-8") as file_handle:
        robot_description = file_handle.read()

    use_sim_time = LaunchConfiguration("use_sim_time")

    return [
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            name="robot_state_publisher",
            output="screen",
            parameters=[
                {
                    "use_sim_time": use_sim_time,
                    "robot_description": robot_description,
                }
            ],
        ),
        Node(
            package="tf2_ros",
            executable="static_transform_publisher",
            name="camera_to_imu_optical_tf",
            arguments=[
                "0",
                "0",
                "0",
                "-1.5708",
                "0",
                "-1.5708",
                "camera1_link",
                "camera1_imu_optical_frame",
            ],
        ),
    ]


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "use_sim_time",
                default_value="false",
                description="Use simulation time",
            ),
            OpaqueFunction(function=launch_setup),
            LogInfo(msg="Static TFs for single-camera bringup started"),
        ]
    )
