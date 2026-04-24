#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry

class OdomSubscriber(Node):
    def __init__(self):
        super().__init__('odom_subscriber')
        
        # Create subscriber for /odom topic
        # QoS profile uses sensor_data for reliable odometry data [citation:3]
        self.subscription = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            rclpy.qos.qos_profile_sensor_data
        )
        
        self.message_count = 0
        self.get_logger().info('Odom Subscriber Node Started')

    def odom_callback(self, msg):
        self.message_count += 1
        
        # Extract position from pose [citation:4]
        position = msg.pose.pose.position
        orientation = msg.pose.pose.orientation
        
        # Extract velocity from twist
        linear_vel = msg.twist.twist.linear
        angular_vel = msg.twist.twist.angular
        
        # Print formatted output
        self.get_logger().info(f'\n--- Odometry Message #{self.message_count} ---')
        self.get_logger().info(f'Frame ID: {msg.header.frame_id}')
        self.get_logger().info(f'Child Frame ID: {msg.child_frame_id}')
        self.get_logger().info(f'Position (x, y, z): ({position.x:.3f}, {position.y:.3f}, {position.z:.3f})')
        self.get_logger().info(f'Orientation (x, y, z, w): ({orientation.x:.3f}, {orientation.y:.3f}, {orientation.z:.3f}, {orientation.w:.3f})')
        self.get_logger().info(f'Linear Velocity (x, y, z): ({linear_vel.x:.3f}, {linear_vel.y:.3f}, {linear_vel.z:.3f})')
        self.get_logger().info(f'Angular Velocity (x, y, z): ({angular_vel.x:.3f}, {angular_vel.y:.3f}, {angular_vel.z:.3f})')
        self.get_logger().info(f'Timestamp: {msg.header.stamp.sec}.{msg.header.stamp.nanosec}')

def main(args=None):
    rclpy.init(args=args)
    node = OdomSubscriber()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down odom subscriber...')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
