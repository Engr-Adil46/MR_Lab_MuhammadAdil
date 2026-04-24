import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
import numpy as np

class LidarNavigator(Node):
    def __init__(self):
        super().__init__('robot')
        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10)
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # Safer thresholds
        self.front_threshold = 0.9
        self.side_threshold = 0.8
        
    def scan_callback(self, msg):
        ranges = np.array(msg.ranges)
        
        # Clean data
        ranges[np.isinf(ranges)] = 8
        ranges[np.isnan(ranges)] = 8
             
        # Define regions
        front = np.concatenate((ranges[:30], ranges[-10:]))
        left = ranges[60:120]
        right = ranges[240:300]
        
        # Minimum distances
        front_dist = np.min(front)
        left_dist = np.min(left)
        right_dist = np.min(right)
        
        twist = Twist()
        
        # Obstacle logic
        if front_dist < self.front_threshold:
            # Turn toward clearer side
            if left_dist > right_dist:
                twist.angular.z = 0.3
            else:
                twist.angular.z = -0.3
            
            twist.linear.x = 0.0
        else:
            # forward motion
            twist.linear.x = 0.08
            twist.angular.z = 0.0
            
        self.publisher.publish(twist)

def main(args=None):
    rclpy.init(args=args)
    node = LidarNavigator()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
