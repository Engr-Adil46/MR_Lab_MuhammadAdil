import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class TriangleTurtle(Node):

    def __init__(self):
        super().__init__('triangle_turtle')
        self.publisher_ = self.create_publisher(Twist, 'turtle3/cmd_vel', 10)
        self.timer = self.create_timer(1.0, self.move)
        self.step = 0

    def move(self):
        msg = Twist()
        # Move forward for even steps
        if self.step % 2 == 0:
            msg.linear.x = 2.0
            msg.angular.z = 0.0
        # Turn 120 degrees for odd steps
        else:
            msg.linear.x = 0.0
            msg.angular.z = 2.09  # 120 degrees in radians

        self.publisher_.publish(msg)
        self.step += 1

def main(args=None):
    rclpy.init(args=args)
    node = TriangleTurtle()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
