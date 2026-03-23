import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class SquareTurtle(Node):

    def __init__(self):
        super().__init__('square_turtle')
        self.publisher_ = self.create_publisher(Twist, 'turtle1/cmd_vel', 10)
        self.timer = self.create_timer(1.0, self.move)
        self.step = 0

    def move(self):
        msg = Twist()
        # Move forward for even steps
        if self.step % 2 == 0:
            msg.linear.x = 2.0
            msg.angular.z = 0.0
        # Turn 90 degrees for odd steps
        else:
            msg.linear.x = 0.0
            msg.angular.z = 1.57

        self.publisher_.publish(msg)
        self.step += 1

def main(args=None):
    rclpy.init(args=args)
    node = SquareTurtle()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
