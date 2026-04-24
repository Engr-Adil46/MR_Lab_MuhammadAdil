#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class CmdVelPublisher(Node):
    def __init__(self):
        super().__init__('cmd_vel_publisher')
        
        # Create publisher for /cmd_vel topic
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # Create timer that calls timer_callback every 2 seconds
        self.timer = self.create_timer(2.0, self.timer_callback)
        
        # State variable to alternate between moving and stopping
        self.move_forward = True
        
        self.get_logger().info('CmdVel Publisher Node Started')

    def timer_callback(self):
        msg = Twist()
        
        if self.move_forward:
            # Move forward at 0.2 m/s
            msg.linear.x = 0.2
            msg.angular.z = 0.0
            self.get_logger().info('Publishing: Move Forward (linear.x = 0.2)')
        else:
            # Stop the robot
            msg.linear.x = 0.0
            msg.angular.z = 0.0
            self.get_logger().info('Publishing: Stop (linear.x = 0.0)')
        
        # Publish the message
        self.publisher.publish(msg)
        
        # Alternate the state for next callback
        self.move_forward = not self.move_forward

def main(args=None):
    rclpy.init(args=args)
    node = CmdVelPublisher()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        # Ensure robot stops on shutdown
        stop_msg = Twist()
        stop_msg.linear.x = 0.0
        stop_msg.angular.z = 0.0
        node.publisher.publish(stop_msg)
        node.get_logger().info('Published stop command on shutdown')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
