import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class CircleTurtle(Node):

    def __init__(self):
        super().__init__('circle_turtle')
        self.publisher_ = self.create_publisher(Twist, 'turtle2/cmd_vel', 10)
        self.timer = self.create_timer(0.1, self.move)

    def move(self):
        msg = Twist()
        msg.linear.x = 2.0      # forward speed
        msg.angular.z = 1.0     # angular speed for circular motion
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = CircleTurtle()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
