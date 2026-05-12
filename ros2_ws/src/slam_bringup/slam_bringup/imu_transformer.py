#!/usr/bin/env python3
"""Transform IMU vectors into the target frame before Madgwick."""

import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import Imu
from geometry_msgs.msg import Vector3Stamped
import tf2_geometry_msgs  # noqa: F401
import tf2_ros


class ImuTransformer(Node):
    def __init__(self) -> None:
        super().__init__("imu_transformer")

        self.declare_parameter("input_topic", "/camera1/camera/imu")
        self.declare_parameter("output_topic", "/camera1/camera/imu_in_base")
        self.declare_parameter("target_frame", "base_link")
        self.declare_parameter("invert_x", False)
        self.declare_parameter("invert_y", False)
        self.declare_parameter("invert_z", False)

        self.input_topic = self.get_parameter("input_topic").value
        self.output_topic = self.get_parameter("output_topic").value
        self.target_frame = self.get_parameter("target_frame").value
        self.invert_x = bool(self.get_parameter("invert_x").value)
        self.invert_y = bool(self.get_parameter("invert_y").value)
        self.invert_z = bool(self.get_parameter("invert_z").value)

        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        sub_qos = QoSProfile(
            depth=10,
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
        )
        pub_qos = QoSProfile(
            depth=10,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.VOLATILE,
        )

        self.subscription = self.create_subscription(
            Imu,
            self.input_topic,
            self.imu_callback,
            sub_qos,
        )
        self.publisher = self.create_publisher(Imu, self.output_topic, pub_qos)

        self.get_logger().info(
            "ImuTransformer: %s -> %s -> %s"
            % (self.input_topic, self.target_frame, self.output_topic)
        )

    def _apply_axis_inversion(self, vector):
        if self.invert_x:
            vector.x = -vector.x
        if self.invert_y:
            vector.y = -vector.y
        if self.invert_z:
            vector.z = -vector.z
        return vector

    def _transform_vector3(self, vector, source_frame, stamp):
        stamped_vector = Vector3Stamped()
        stamped_vector.header.frame_id = source_frame
        stamped_vector.header.stamp = stamp
        stamped_vector.vector = vector

        try:
            transformed = self.tf_buffer.transform(
                stamped_vector,
                self.target_frame,
                timeout=rclpy.duration.Duration(seconds=0.05),
            )
            return transformed.vector
        except Exception as exc:
            self.get_logger().warn(f"TF transform failed: {exc}", throttle_duration_sec=5.0)
            return None

    def imu_callback(self, msg: Imu) -> None:
        source_frame = msg.header.frame_id
        stamp = msg.header.stamp

        accel_transformed = self._transform_vector3(
            msg.linear_acceleration,
            source_frame,
            stamp,
        )
        gyro_transformed = self._transform_vector3(
            msg.angular_velocity,
            source_frame,
            stamp,
        )

        if accel_transformed is None or gyro_transformed is None:
            return

        accel_transformed = self._apply_axis_inversion(accel_transformed)
        gyro_transformed = self._apply_axis_inversion(gyro_transformed)

        output_msg = Imu()
        output_msg.header.stamp = stamp
        output_msg.header.frame_id = self.target_frame
        output_msg.linear_acceleration = accel_transformed
        output_msg.angular_velocity = gyro_transformed
        output_msg.linear_acceleration_covariance = msg.linear_acceleration_covariance
        output_msg.angular_velocity_covariance = msg.angular_velocity_covariance
        output_msg.orientation = msg.orientation
        output_msg.orientation_covariance = msg.orientation_covariance

        self.publisher.publish(output_msg)


def main(args=None):
    rclpy.init(args=args)
    node = ImuTransformer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
