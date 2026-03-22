#!/usr/bin/env python3
"""
Mobile Goal Tracker: Subscribes to the green sphere's odometry and sends
NavigateToPose goals to Nav2 so the robot chases the sphere using Dijkstra.
Press 'h' in the terminal to pause sphere tracking and return to (0, 0).
"""
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.action.client import ClientGoalHandle
from nav_msgs.msg import Odometry
from nav2_msgs.action import NavigateToPose
import math
import sys
import select
import threading

try:
    import termios, tty
    HAS_TERMIOS = True
except ImportError:
    HAS_TERMIOS = False


class MobileGoalTracker(Node):
    def __init__(self):
        super().__init__('mobile_goal_tracker')

        self._action_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

        self.subscription = self.create_subscription(
            Odometry,
            '/sphere/odom',
            self.odom_callback,
            10)

        self.robot_subscription = self.create_subscription(
             Odometry,
             '/odom',
             self.robot_odom_callback,
             10)

        self.robot_x = 0.0
        self.robot_y = 0.0
        self.last_goal_x = None
        self.last_goal_y = None
        self.goal_distance_threshold = 0.5
        self._current_goal_handle: ClientGoalHandle = None
        self._nav2_ready = False
        self.returning_home = False

        # Wait for Nav2 action server once at startup (non-blocking timer)
        self._wait_timer = self.create_timer(2.0, self._check_nav2_ready)
        self.get_logger().info("Tracker started. Press 'h' to RETURN HOME or RESUME chasing.")

    def _check_nav2_ready(self):
        if self._action_client.wait_for_server(timeout_sec=0.5):
            self._nav2_ready = True
            self._wait_timer.cancel()
            self.get_logger().info('Nav2 action server is ready! Tracking sphere.')
        else:
            self.get_logger().info('Waiting for Nav2 action server...')

    def robot_odom_callback(self, msg):
        self.robot_x = msg.pose.pose.position.x
        self.robot_y = msg.pose.pose.position.y

    def odom_callback(self, msg):
        if not self._nav2_ready or self.returning_home:
            return

        target_x = msg.pose.pose.position.x
        target_y = msg.pose.pose.position.y

        # Only send a new goal if the sphere has moved significantly
        if self.last_goal_x is not None:
            distance = math.sqrt(
                (target_x - self.last_goal_x) ** 2 +
                (target_y - self.last_goal_y) ** 2
            )
            if distance < self.goal_distance_threshold:
                return

        self.send_goal(target_x, target_y)

    def send_goal(self, x, y):
        # Calculate yaw to face the sphere from the robot's current position
        yaw = math.atan2(y - self.robot_y, x - self.robot_x)
        
        # OFFSET THE GOAL: Send the robot to a point 0.5m away from the center of the sphere
        offset_distance = 0.5
        goal_x = x - (offset_distance * math.cos(yaw))
        goal_y = y - (offset_distance * math.sin(yaw))

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = goal_x
        goal_msg.pose.pose.position.y = goal_y
        
        goal_msg.pose.pose.orientation.z = math.sin(yaw / 2.0)
        goal_msg.pose.pose.orientation.w = math.cos(yaw / 2.0)

        self.get_logger().info(
            f'Sending Nav2 goal → X: {goal_x:.2f}, Y: {goal_y:.2f} (Facing sphere at {x:.2f}, {y:.2f})'
        )

        send_goal_future = self._action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )
        send_goal_future.add_done_callback(self.goal_response_callback)

        self.last_goal_x = x
        self.last_goal_y = y

    def return_home(self):
        self.get_logger().info('Sending robot back to origin (0.0, 0.0)...')
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = 0.0
        goal_msg.pose.pose.position.y = 0.0
        goal_msg.pose.pose.orientation.w = 1.0

        send_goal_future = self._action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )
        send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().warn('Goal REJECTED by Nav2!')
            return
        self.get_logger().info('Goal ACCEPTED by Nav2 — Dijkstra planning...')
        self._current_goal_handle = goal_handle

        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.result_callback)

    def feedback_callback(self, feedback_msg):
        pass

    def result_callback(self, future):
        result = future.result()
        status = result.status
        if status == 4:  # SUCCEEDED
            self.get_logger().info('Goal REACHED!')
        elif status == 6:  # ABORTED
            self.get_logger().warn('Goal ABORTED by Nav2 (no valid path?)')
        elif status == 5:  # CANCELED
            self.get_logger().info('Goal was cancelled (new goal incoming)')
        self._current_goal_handle = None


def main(args=None):
    rclpy.init(args=args)
    node = MobileGoalTracker()

    settings = termios.tcgetattr(sys.stdin) if HAS_TERMIOS else None

    t = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    t.start()

    try:
        while rclpy.ok():
            if HAS_TERMIOS:
                try:
                    tty.setraw(sys.stdin.fileno())
                    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
                    key = sys.stdin.read(1) if rlist else ''
                    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
                except KeyboardInterrupt:
                    break
                if key == 'h':
                    if node.returning_home:
                        node.returning_home = False
                        node.get_logger().info('RESUMING sphere chase!')
                        node.last_goal_x = None  # Force immediate update
                    else:
                        node.returning_home = True
                        node.return_home()
                elif key == '\x03':
                    break
    except KeyboardInterrupt:
        pass
    finally:
        if settings:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        node.destroy_node()
        try:
            rclpy.shutdown()
        except Exception:
            pass
        sys.exit(0)


if __name__ == '__main__':
    main()
