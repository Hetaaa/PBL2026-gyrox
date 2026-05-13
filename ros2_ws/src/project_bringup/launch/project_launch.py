#!/usr/bin/env python3
"""Main system bringup orchestrator with all subsystems and health checks."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription, OpaqueFunction, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def launch_setup(context, *args, **kwargs):
    # Include slam_bringup with health checks
    slam_bringup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("slam_bringup"), "launch", "slam_bringup_launch.py"]
            )
        ),
        launch_arguments={
            "camera_config": LaunchConfiguration("camera_config"),
            "madgwick_config": LaunchConfiguration("madgwick_config"),
            "stereo_odometry_config": LaunchConfiguration("stereo_odometry_config"),
            "rgbd_sync_config": LaunchConfiguration("rgbd_sync_config"),
            "rtabmap_config": LaunchConfiguration("rtabmap_config"),
        }.items(),
    )

    # Wait for SLAM to be ready (health check)
    wait_for_slam_ready = ExecuteProcess(
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

    # Launch rplidar via its launch file
    rplidar_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("rplidar_ros"), "launch", "rplidar_a1_launch.py"]
            )
        ),
    )

    # Launch closest_element_info node
    closest_element_launch = Node(
        package="closest_element_info",
        executable="closest_element_info",
        name="closest_element_info",
        output="screen",
    )

    # Launch scan_filter node
    scan_filter_launch = Node(
        package="scan_filter",
        executable="scan_filter",
        name="scan_filter",
        output="screen",
    )

    # Launch ultrasonic_driver collector node
    ultrasonic_collector_launch = Node(
        package="ultrasonic_driver",
        executable="collector",
        name="ultrasonic_collector",
        output="screen",
    )

    # Health check: wait for ultrasonic collector echo
    wait_for_ultrasonic_ready = ExecuteProcess(
        cmd=[
            "ros2",
            "topic",
            "echo",
            "--once",
            "ultrasonic/echo",
        ],
        output="screen",
    )

    # Launch ultrasonic_driver monitor node (triggered after health check)
    ultrasonic_monitor_launch = Node(
        package="ultrasonic_driver",
        executable="monitor",
        name="ultrasonic_monitor",
        output="screen",
    )

    # Launch zones_manager node
    zones_manager_launch = Node(
        package="zones_manager",
        executable="zones_manager",
        name="zones_manager",
        output="screen",
    )

    return [
        slam_bringup_launch,
        rplidar_launch,
        closest_element_launch,
        scan_filter_launch,
        ultrasonic_collector_launch,
        # Health check - czeka na echo od collectora
        wait_for_ultrasonic_ready,
        # Monitor startuje po sukcesie health checku
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=wait_for_ultrasonic_ready,
                on_exit=[ultrasonic_monitor_launch],
            )
        ),
        zones_manager_launch,
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
            DeclareLaunchArgument(
                "rgbd_sync_config",
                default_value=PathJoinSubstitution(
                    [
                        FindPackageShare("slam_bringup"),
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
                        FindPackageShare("slam_bringup"),
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
