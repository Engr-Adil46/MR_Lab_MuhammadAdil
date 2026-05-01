import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import FollowWaypoints
from geometry_msgs.msg import PoseStamped
import time

def make_pose(x, y, yaw_w):
    """Create a PoseStamped message with given x, y, and orientation w."""
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

class WaypointNavigator(Node):
    def __init__(self):
        super().__init__('waypoint_navigator')
        self.action_client = ActionClient(self, FollowWaypoints, '/follow_waypoints')
        self.get_logger().info('WaypointNavigator node initialized')

    def send_waypoints(self, waypoints):
        """Send a list of waypoints to the FollowWaypoints action server."""
        if not self.action_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error('FollowWaypoints action server not available!')
            return False

        goal_msg = FollowWaypoints.Goal()
        goal_msg.poses = waypoints

        self.get_logger().info(f'Sending {len(waypoints)} waypoints...')
        future = self.action_client.send_goal_async(goal_msg)

        # Wait for result
        rclpy.spin_once(self, timeout_sec=0.1)
        result = future.result()
        if result.accepted:
            self.get_logger().info('Goal accepted, waiting for completion...')
            result_future = result.get_result_async()
            rclpy.spin_until_future_complete(self, result_future)
            final_result = result_future.result()
            self.get_logger().info(f'Mission complete. Result: {final_result.result}')
            return True
        else:
            self.get_logger().error('Goal rejected')
            return False

def main():
    rclpy.init()
    navigator = WaypointNavigator()
    
    waypoints = [
        make_pose(0.0, 0.0, 1.0),      # Waypoint 1: origin
        make_pose(1.0, 0.0, 1.0),      # Waypoint 2
        make_pose(1.0, 1.0, 1.0),      # Waypoint 3
        make_pose(0.0, 1.0, 1.0),      # Waypoint 4
        make_pose(0.0, 0.0, 1.0),      # Waypoint 5: return to origin
    ]
    
    navigator.send_waypoints(waypoints)
    
    navigator.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
