import rclpy
from rclpy.node import Node

class SimpleNode(Node):
    def __init__(self):
        super().__init__('simple_node')
        
        # Declare parameter with a default string value to avoid deprecation warning
        self.declare_parameter('student_name', 'PARAMETER NOT SET')
        
        # Get parameter value
        student_name = self.get_parameter('student_name').get_parameter_value().string_value
        
        if student_name == 'PARAMETER NOT SET':
            self.get_logger().info('student_name not set')
        else:
            self.get_logger().info(f'Student name: {student_name}')

def main(args=None):
    rclpy.init(args=args)
    node = SimpleNode()
    rclpy.spin_once(node, timeout_sec=0.1)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
