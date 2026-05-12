import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import String

class ZonesManager(Node):
    def __init__(self):
        super().__init__('zones_manager')
        self.subscription = self.create_subscription(
            String,
            '/closest_element_info',
            self.callback,
            10  
        )
        self.publisher = self.create_publisher(
            String,
            '/zones_info',
            10  
        )
        self.get_logger().info('Zones manager started')

    def callback(self, msg):
        nearest_distance = float(msg.data)
        if nearest_distance < 1:
            zone = 'Strefa 1'
        elif nearest_distance < 2.0:
            zone = 'Strefa 2'
        elif nearest_distance < 5.0:
            zone = 'Strefa 3'
        output = String()
        output.data = zone
        self.publisher.publish(output)

def main(args=None):
    rclpy.init(args=args)
    zones_manager = ZonesManager()
    try:
        rclpy.spin(zones_manager)
    except KeyboardInterrupt:
        pass
    finally:
        zones_manager.destroy_node()
        rclpy.shutdown()
