import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import String

class ClosestElementInfo(Node):
    def __init__(self):
        super().__init__('closest_element_info')
        self.subscription = self.create_subscription(
            LaserScan,
            '/scan_filtered',
            self.callback,
            10  
        )
        self.publisher = self.create_publisher(
            String,
            '/closest_element_info',
            10  
        )
        self.get_logger().info('Closest element info controller started')

    def callback(self, msg):
        valid_ranges = [
            range_value
            for range_value in msg.ranges
            if math.isfinite(range_value)
            and msg.range_min <= range_value <= msg.range_max
        ]
        if not valid_ranges:
            return

        nearest_distance = min(valid_ranges)
        output = String()
        output.data = str(nearest_distance)
        self.publisher.publish(output)

def main(args=None):
    rclpy.init(args=args)
    
    closest_element_info = ClosestElementInfo()

    try:
        rclpy.spin(closest_element_info)
    except KeyboardInterrupt:
        pass
    finally:
        closest_element_info.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
