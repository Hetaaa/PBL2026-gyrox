from __future__ import annotations

from typing import Iterable

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan

from .utils import filter_scan


class ScanFilter(Node):
    """ROS2 node that filters LaserScan messages by angle range."""

    def __init__(self) -> None:
        super().__init__('scan_filter')
        self.declare_parameter('min_angle_deg', 20.0)
        self.declare_parameter('max_angle_deg', 160.0)
        self.declare_parameter('input_topic', '/scan')
        self.declare_parameter('output_topic', '/scan_filtered')

        input_topic = self.get_parameter('input_topic').value
        output_topic = self.get_parameter('output_topic').value

        self._publisher = self.create_publisher(LaserScan, output_topic, 10)
        self._subscription = self.create_subscription(
            LaserScan,
            input_topic,
            self._callback,
            10,
        )
        self.get_logger().info(
            f'Scan filter listening on {input_topic} and publishing to {output_topic}.'
        )

    def _callback(self, msg: LaserScan) -> None:
        min_angle_deg = float(self.get_parameter('min_angle_deg').value)
        max_angle_deg = float(self.get_parameter('max_angle_deg').value)
        filtered_msg = filter_scan(msg, min_angle_deg, max_angle_deg)
        self._publisher.publish(filtered_msg)


def main(args: Iterable[str] | None = None) -> None:
    """Run the scan filter node."""
    rclpy.init(args=args)
    node = ScanFilter()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
