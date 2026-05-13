import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import String, ColorRGBA
from visualization_msgs.msg import Marker, MarkerArray
from geometry_msgs.msg import Point

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
        self.marker_publisher = self.create_publisher(
            Marker,
            '/zones_marker',
            10
        )
        self.color_panel_publisher = self.create_publisher(
            Marker,
            '/zones_color_panel',
            10
        )
        self.get_logger().info('Zones manager started')

    def callback(self, msg):
        nearest_distance = float(msg.data)
        
        # Determine zone and color
        if nearest_distance < 1:
            zone = 'Strefa 1'
            # Red (RGB)
            r, g, b = 1.0, 0.0, 0.0
        elif nearest_distance < 2.0:
            zone = 'Strefa 2'
            # Yellow (RGB)
            r, g, b = 1.0, 1.0, 0.0
        elif nearest_distance < 5.0:
            zone = 'Strefa 3'
            # Green (RGB)
            r, g, b = 0.0, 1.0, 0.0
        else:
            zone = 'Poza strefami'
            # Gray (RGB)
            r, g, b = 0.5, 0.5, 0.5
        
        # Publish zone info as string
        output = String()
        output.data = zone
        self.publisher.publish(output)
        
        # Publish marker for visualization
        marker = Marker()
        marker.header.frame_id = "base_link"
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = "zones"
        marker.id = 0
        marker.type = Marker.SPHERE  # Or use CYLINDER for zone boundaries
        marker.action = Marker.ADD
        
        # Position at the robot base
        marker.pose.position.x = 0.0
        marker.pose.position.y = 0.0
        marker.pose.position.z = 0.0
        marker.pose.orientation.w = 1.0
        
        # Scale - sphere radius in meters
        marker.scale.x = nearest_distance * 2  # diameter
        marker.scale.y = nearest_distance * 2
        marker.scale.z = 0.1
        
        # Color with transparency
        marker.color.r = r
        marker.color.g = g
        marker.color.b = b
        marker.color.a = 0.3  # Transparency
        
        # Lifetime
        marker.lifetime.sec = 1
        marker.lifetime.nanosec = 0
        
        self.marker_publisher.publish(marker)
        
        # Publish 2D color panel
        panel = Marker()
        panel.header.frame_id = "base_link"
        panel.header.stamp = self.get_clock().now().to_msg()
        panel.ns = "zones_panel"
        panel.id = 1
        panel.type = Marker.CUBE
        panel.action = Marker.ADD
        
        # Position panel above/below the robot
        panel.pose.position.x = 0.0
        panel.pose.position.y = 0.0
        panel.pose.position.z = -0.05  # Slight offset
        panel.pose.orientation.w = 1.0
        
        # Large flat panel
        panel.scale.x = 4.0  # width
        panel.scale.y = 4.0  # depth
        panel.scale.z = 0.01  # very thin
        
        # Color with transparency
        panel.color.r = r
        panel.color.g = g
        panel.color.b = b
        panel.color.a = 0.5  # Transparency
        
        # Lifetime
        panel.lifetime.sec = 1
        panel.lifetime.nanosec = 0
        
        self.color_panel_publisher.publish(panel)

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

if __name__ == '__main__':
    main()
