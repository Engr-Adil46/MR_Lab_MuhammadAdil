import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import FollowWaypoints
from geometry_msgs.msg import PoseStamped
import sys

def make_pose(x, y, yaw_w):
    pose = PoseStamped()
    pose.header.frame_id = 'map'
    pose.header.stamp = rclpy.time.Time().to_msg()
    pose.pose.position.x = x
    pose.pose.position.y = y
    pose.pose.position.z = 0.0
    pose.pose.orientation.x = 0.0
    pose.pose.orientation.y = 0.0
    pose.pose.orientation.z = 0.0
    pose.pose.orientation.w = yaw_w
    return pose

def parse_waypoints(args):
    waypoints = []
    for arg in args:
        try:
            x, y, w = map(float, arg.split(','))
            waypoints.append(make_pose(x, y, w))
        except:
            print(f"Invalid waypoint format: {arg}")
    return waypoints

class WaypointNavigator(Node):
    def __init__(self):
        super().__init__('waypoint_navigator')
        self.action_client = ActionClient(self, FollowWaypoints, '/follow_waypoints')

    def send_waypoints(self, waypoints):
        if not self.action_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error('Action server not available')
            return False

        goal_msg = FollowWaypoints.Goal()
        goal_msg.poses = waypoints

        self.get_logger().info(f'Sending {len(waypoints)} waypoints')
        future = self.action_client.send_goal_async(goal_msg)

        rclpy.spin_until_future_complete(self, future)
        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().error('Goal rejected')
            return False

        self.get_logger().info('Goal accepted')

        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)

        result = result_future.result().result
        self.get_logger().info(f'Result: {result}')
        return True

def main():
    rclpy.init()

    if len(sys.argv) < 2:
        print("Usage: ros2 run lab7_nav2 dynamic_waypoints x,y,w x,y,w ...")
        print("Example: ros2 run lab7_nav2 dynamic_waypoints 0,0,1 1,0,1 1,1,1 0,1,1 0,0,1")
        return

    waypoints = parse_waypoints(sys.argv[1:])

    if not waypoints:
        print("No valid waypoints provided")
        return

    navigator = WaypointNavigator()
    navigator.send_waypoints(waypoints)

    navigator.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
