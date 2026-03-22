#!/usr/bin/env python3

import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, PoseStamped
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry

def euler_from_quaternion(quaternion):
    """
    Converts quaternion (w in last place) to euler roll, pitch, yaw
    quaternion = [x, y, z, w]
    """
    x = quaternion.x
    y = quaternion.y
    z = quaternion.z
    w = quaternion.w

    sinr_cosp = 2 * (w * x + y * z)
    cosr_cosp = 1 - 2 * (x * x + y * y)
    roll = math.atan2(sinr_cosp, cosr_cosp)

    sinp = 2 * (w * y - z * x)
    pitch = math.asin(sinp)

    siny_cosp = 2 * (w * z + x * y)
    cosy_cosp = 1 - 2 * (y * y + z * z)
    yaw = math.atan2(siny_cosp, cosy_cosp)

    return roll, pitch, yaw

class ObstacleAvoidanceNode(Node):
    def __init__(self):
        super().__init__('obstacle_avoidance_node')

        # Publishers and Subscribers
        self.cmd_vel_pub = self.create_publisher(Twist, '/dynamixel_workbench/cmd_vel', 10)
        self.scan_sub = self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)
        self.odom_sub = self.create_subscription(Odometry, '/odom', self.odom_callback, 10)
        self.goal_sub = self.create_subscription(PoseStamped, '/goal_pose', self.goal_callback, 10)

        # State Variables
        self.state = 'IDLE' # IDLE, TURN_TO_GOAL, GO_TO_GOAL, AVOID_OBSTACLE
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_yaw = 0.0
        
        self.goal_x = None
        self.goal_y = None
        
        self.obstacle_detected = False
        
        # Parameters
        self.distance_tolerance = 0.1
        self.angle_tolerance = 0.1
        self.safe_distance = 0.4  # meters
        
        # Timer for control loop
        self.timer = self.create_timer(0.1, self.control_loop)
        self.get_logger().info("Obstacle Avoidance Node Started. Waiting for /goal_pose from RViz...")

    def goal_callback(self, msg):
        self.goal_x = msg.pose.position.x
        self.goal_y = msg.pose.position.y
        self.state = 'TURN_TO_GOAL'
        self.get_logger().info(f"New goal received: x={self.goal_x:.2f}, y={self.goal_y:.2f}")

    def odom_callback(self, msg):
        self.current_x = msg.pose.pose.position.x
        self.current_y = msg.pose.pose.position.y
        _, _, self.current_yaw = euler_from_quaternion(msg.pose.pose.orientation)

    def scan_callback(self, msg):
        # Look at the front 60 degrees (-30 to +30 degrees approx)
        # Laser ranges array maps to angles from angle_min to angle_max
        ranges = msg.ranges
        num_ranges = len(ranges)
        if num_ranges == 0:
            return

        # Assuming 360 degree Lidar starting from front
        # We check the first few and last few indices (front cone)
        front_cone_angle = math.radians(30)
        indices_to_check = int((front_cone_angle / msg.angle_increment))
        
        front_ranges = ranges[:indices_to_check] + ranges[-indices_to_check:]
        
        # Filter out inf and zero values
        valid_ranges = [r for r in front_ranges if r > msg.range_min and r < msg.range_max and not math.isinf(r) and not math.isnan(r)]
        
        if valid_ranges:
            min_front_distance = min(valid_ranges)
            if min_front_distance < self.safe_distance:
                self.obstacle_detected = True
            else:
                self.obstacle_detected = False
        else:
            self.obstacle_detected = False

    def control_loop(self):
        msg = Twist()

        if self.goal_x is None or self.goal_y is None:
            self.state = 'IDLE'
            self.cmd_vel_pub.publish(msg)
            return

        distance_to_goal = math.sqrt((self.goal_x - self.current_x)**2 + (self.goal_y - self.current_y)**2)
        angle_to_goal = math.atan2(self.goal_y - self.current_y, self.goal_x - self.current_x)

        # Handle State Transitions
        if distance_to_goal < self.distance_tolerance:
            self.get_logger().info("Goal Reached!")
            self.goal_x = None
            self.goal_y = None
            self.state = 'IDLE'
        
        elif self.obstacle_detected:
            self.state = 'AVOID_OBSTACLE'
            
        elif self.state == 'AVOID_OBSTACLE' and not self.obstacle_detected:
            self.state = 'NAVIGATING'
            
        elif self.state in ['TURN_TO_GOAL', 'GO_TO_GOAL']:
            # Upgrading old discrete states to smooth navigation
            self.state = 'NAVIGATING'

        # Execute Control based on State
        if self.state == 'IDLE':
            msg.linear.x = 0.0
            msg.angular.z = 0.0
            
        elif self.state == 'NAVIGATING':
            # Calculate heading error
            error_angle = angle_to_goal - self.current_yaw
            # Normalize angle to [-pi, pi]
            error_angle = math.atan2(math.sin(error_angle), math.cos(error_angle))
            
            # Smooth Proportional (P) Control
            # 1. Steer towards the goal (max 1.0 rad/s)
            msg.angular.z = max(min(1.0 * error_angle, 1.0), -1.0)
            
            # 2. Drive forward, but slow down linearly if we are facing the wrong way
            # If perfectly aligned (error=0), x = 0.2 m/s
            # If facing 90 deg away (error=1.57), x = ~0.0 m/s
            speed_multiplier = max(1.0 - (abs(error_angle) / (math.pi / 2.0)), 0.0)
            msg.linear.x = 0.2 * speed_multiplier
            
        elif self.state == 'AVOID_OBSTACLE':
            # Smooth avoidance: Curve backward and away
            msg.linear.x = -0.05
            msg.angular.z = 0.8

        self.cmd_vel_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = ObstacleAvoidanceNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
