import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import cv2
import numpy as np

class Lab9(Node):
    def __init__(self):
        super().__init__('lab9')

        # Subscriptions and Publishers
        self.subscription = self.create_subscription(Image, '/camera/image_raw', self.image_callback, 10)
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.bridge = CvBridge()

        # --- Control Parameters ---
        self.kp = 0.0005
        self.center_threshold = 50
        self.stop_area_threshold = 1000000

        # --- Search Parameters ---
        self.state = 'TRACKING'  # States: 'TRACKING', 'SEARCHING', 'SEARCH_FAILED'
        self.search_start_time = None
        self.search_angular_speed = 0.5  # radians per second
        self.current_target = None  # Track which target we're following: 'cylinder' or 'cube'

        base_time = (3 * np.pi) / self.search_angular_speed
        self.search_duration = base_time - 0.05

        self.get_logger().info("Lab9 Node Active - Prioritizing Pink Cylinder, then Blue Cube")

    def detect_targets(self, hsv_image):
        """Detect both pink cylinder and blue cube, return prioritized target info"""
        
        # --- Pink Cylinder Detection (Priority Target) ---
        lower_pink = np.array([140, 50, 50])
        upper_pink = np.array([170, 255, 255])
        pink_mask = cv2.inRange(hsv_image, lower_pink, upper_pink)
        
        # Clean up pink mask
        kernel = np.ones((5, 5), np.uint8)
        pink_mask = cv2.morphologyEx(pink_mask, cv2.MORPH_OPEN, kernel)
        pink_mask = cv2.morphologyEx(pink_mask, cv2.MORPH_CLOSE, kernel)
        
        # --- Blue Cube Detection (Secondary Target) ---
        lower_blue = np.array([100, 150, 0])
        upper_blue = np.array([140, 255, 255])
        blue_mask = cv2.inRange(hsv_image, lower_blue, upper_blue)
        
        # Clean up blue mask
        blue_mask = cv2.morphologyEx(blue_mask, cv2.MORPH_OPEN, kernel)
        blue_mask = cv2.morphologyEx(blue_mask, cv2.MORPH_CLOSE, kernel)
        
        # Calculate moments for both targets
        pink_M = cv2.moments(pink_mask)
        blue_M = cv2.moments(blue_mask)
        
        # PRIORITIZE: Check for pink cylinder first
        if pink_M["m00"] > 0:
            self.current_target = 'cylinder'
            return {
                'type': 'cylinder',
                'mask': pink_mask,
                'moments': pink_M,
                'color': (0, 255, 255),  # Yellow circle for cylinder
                'label': 'Pink Cylinder'
            }
        
        # If no pink cylinder, check for blue cube
        elif blue_M["m00"] > 0:
            self.current_target = 'cube'
            return {
                'type': 'cube',
                'mask': blue_mask,
                'moments': blue_M,
                'color': (255, 0, 0),    # Blue circle for cube
                'label': 'Blue Cube'
            }
        
        # No targets detected
        else:
            self.current_target = None
            return None

    def image_callback(self, msg):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        except Exception as e:
            self.get_logger().error(f"Image conversion failed: {e}")
            return

        hsv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
        
        # Detect prioritized targets
        target_info = self.detect_targets(hsv_image)
        
        # Initialize Twist message for motion commands
        twist = Twist()
        
        # --- TARGET IN VIEW ---
        if target_info is not None:
            # If we were searching, announce we found it
            if self.state != 'TRACKING':
                self.get_logger().info(f"Target acquired: {target_info['label']}! Resuming tracking.")
            
            # Reset state to tracking
            self.state = 'TRACKING'
            self.search_start_time = None
            
            # Calculate centroid and area
            M = target_info['moments']
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            pixel_area = M["m00"] / 255
            
            # Draw tracking information on image
            cv2.circle(cv_image, (cx, cy), 10, target_info['color'], -1)
            cv2.putText(cv_image, f"{target_info['label']}", (cx - 50, cy - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, target_info['color'], 2)
            cv2.putText(cv_image, f"Area: {int(pixel_area)}", (cx - 50, cy + 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, target_info['color'], 2)
            
            # Proportional Control (Alignment)
            height, width, _ = cv_image.shape
            image_center_x = width / 2
            
            error_x = image_center_x - cx
            twist.angular.z = self.kp * error_x
            
            # Move forward and stop at close range
            if abs(error_x) < self.center_threshold:
                if pixel_area < self.stop_area_threshold:
                    twist.linear.x = 0.25
                    cv2.putText(cv_image, "MOVING FORWARD", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                else:
                    twist.linear.x = 0.0
                    cv2.putText(cv_image, "TARGET REACHED", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            else:
                twist.linear.x = 0.0
                cv2.putText(cv_image, "ALIGNING...", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        # --- TARGET LOST (SEARCH PROTOCOL) ---
        else:
            twist.linear.x = 0.0  # Never drive forward if we can't see anything
            
            if self.state == 'TRACKING':
                # We just lost the target. Start the timer and begin spinning.
                self.state = 'SEARCHING'
                self.search_start_time = self.get_clock().now()
                self.get_logger().warn(f"Target lost! {self.current_target if self.current_target else 'No target'} - Initiating 360-degree search sweep...")
                cv2.putText(cv_image, "SEARCHING FOR TARGET...", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            elif self.state == 'SEARCHING':
                # Calculate how long we have been spinning
                elapsed_time = (self.get_clock().now() - self.search_start_time).nanoseconds / 1e9
                
                if elapsed_time < self.search_duration:
                    # Keep spinning
                    twist.angular.z = self.search_angular_speed
                    cv2.putText(cv_image, f"SEARCHING: {int(elapsed_time)}s", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                else:
                    # Timer expired. We did a full 360 and found nothing.
                    self.state = 'SEARCH_FAILED'
                    self.get_logger().error("360-degree sweep complete. No target found. Stopping.")
                    cv2.putText(cv_image, "SEARCH FAILED - NO TARGET", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            elif self.state == 'SEARCH_FAILED':
                # Stay completely still
                twist.angular.z = 0.0
                cv2.putText(cv_image, "ROBOT STOPPED - NO TARGET", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Display current status
        status_text = f"State: {self.state} | Target: {self.current_target if self.current_target else 'None'}"
        cv2.putText(cv_image, status_text, (10, cv_image.shape[0] - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Publish the motion command
        self.publisher.publish(twist)
        
        # Show the camera feed with targeting information
        cv2.imshow("Multi-Target Tracking System (Pink Cylinder Priority)", cv_image)
        cv2.waitKey(1)

def main(args=None):
    rclpy.init(args=args)
    node = Lab9()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        cv2.destroyAllWindows()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
