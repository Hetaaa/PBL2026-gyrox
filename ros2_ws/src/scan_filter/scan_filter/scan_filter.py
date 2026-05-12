from .utils import filter_scan

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan

class ScanFilter(Node):
    def __init__(self) -> None:
        super().__init__('scan_filter')
        self._scan_publisher = self.create_publisher(LaserScan, 'scan_filtered', 10)
        self.create_subscription(LaserScan, 'scan', self._callback, 10)

    def _callback(self, msg: LaserScan) -> None:
        filtered_msg = filter_scan(msg, min_angle_deg=20.0, max_angle_deg=160.0)
        self._scan_publisher.publish(filtered_msg)

def main(args=None):
    rclpy.init(args=args)
    node = ScanFilter()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
