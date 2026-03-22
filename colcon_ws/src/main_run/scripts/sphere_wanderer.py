#!/usr/bin/env python3
"""
Sphere Wanderer: moves the green sphere around the apartment as a mobile goal.
 - Holds a heading for 3.0s then picks a new random heading
 - Bounces away from apartment boundary walls so it stays inside
 - Press 's' to stop, Ctrl-C to exit cleanly
"""
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import random
import math
import threading
import sys
import select

try:
    import termios, tty
    HAS_TERMIOS = True
except ImportError:
    HAS_TERMIOS = False

# Apartment soft boundary (slightly inside outer walls)
X_MIN, X_MAX = -5.3, 5.3
Y_MIN, Y_MAX = -4.3, 4.3

SPEED = 0.7          # m/s linear speed
HEADING_HOLD = 3.0   # seconds per heading


class SphereWanderer(Node):
    def __init__(self):
        super().__init__('sphere_wanderer')

        self._pub = self.create_publisher(Twist, '/sphere/cmd_vel', 10)
        self._sub = self.create_subscription(Odometry, '/sphere/odom',
                                             self._odom_cb, 10)

        self.stopped   = False
        self._heading  = random.uniform(-math.pi, math.pi)  # radians
        self._hold_t   = 0.0
        self._pos_x    = 2.0
        self._pos_y    = 0.0
        self._bounce_cd = 0

        # Timer: runs at 10 Hz, updates velocity cmd
        self.create_timer(0.1, self._step)
        # Timer: change heading every HEADING_HOLD seconds
        self.create_timer(HEADING_HOLD, self._pick_heading)

        self.get_logger().info("Sphere Wanderer started. Press 's' to stop.")

    def _odom_cb(self, msg: Odometry):
        self._pos_x = msg.pose.pose.position.x
        self._pos_y = msg.pose.pose.position.y

    def _pick_heading(self):
        """Choose a new random heading, biased away from any nearby wall."""
        if self.stopped:
            return
        bounce = self._wall_bounce_angle()
        if bounce is not None:
            self._heading = bounce
            self._bounce_cd = 20
        else:
            self._heading = random.uniform(-math.pi, math.pi)

    def _wall_bounce_angle(self):
        """If near a boundary return an angle pointing inward, else None."""
        margin = 1.2
        x, y = self._pos_x, self._pos_y
        
        # Handle corners by returning an angle that escapes both X and Y
        if x < X_MIN + margin and y < Y_MIN + margin:
            return random.uniform(0.1, math.pi/2 - 0.1)    # face +X, +Y
        if x > X_MAX - margin and y < Y_MIN + margin:
            return random.uniform(math.pi/2 + 0.1, math.pi - 0.1)  # face -X, +Y
        if x < X_MIN + margin and y > Y_MAX - margin:
            return random.uniform(-math.pi/2 + 0.1, -0.1)  # face +X, -Y
        if x > X_MAX - margin and y > Y_MAX - margin:
            return random.uniform(-math.pi + 0.1, -math.pi/2 - 0.1) # face -X, -Y
            
        if x < X_MIN + margin:
            return random.uniform(-math.pi * 0.4, math.pi * 0.4)   # face +X
        if x > X_MAX - margin:
            return random.uniform(math.pi * 0.6, math.pi * 1.4)    # face -X
        if y < Y_MIN + margin:
            return random.uniform(math.pi * 0.1, math.pi * 0.9)    # face +Y
        if y > Y_MAX - margin:
            return random.uniform(-math.pi * 0.9, -math.pi * 0.1)  # face -Y
        return None

    def _step(self):
        msg = Twist()
        if not self.stopped:
            # Force bounce override if very close to edge
            if self._bounce_cd > 0:
                self._bounce_cd -= 1
            elif self._wall_bounce_angle() is not None:
                self._heading = self._wall_bounce_angle()
                self._bounce_cd = 30  # Hold the escape trajectory for 3.0s
                
            msg.linear.x  = SPEED
            msg.angular.z = 0.0
            # Express desired heading as angular velocity (simple proportional)
            # We send planar velocity in body frame via libgazebo_ros_planar_move
            # which treats linear.x as forward, angular.z as turn rate in world
            vx = SPEED * math.cos(self._heading)
            vy = SPEED * math.sin(self._heading)
            msg.linear.x = vx
            msg.linear.y = vy
        self._pub.publish(msg)

    def stop_sphere(self):
        self.stopped = True
        self.get_logger().info('Sphere stopped!')
        self._pub.publish(Twist())

    def resume_sphere(self):
        self.stopped = False
        self._pick_heading()
        self.get_logger().info('Sphere resuming.')


def main(args=None):
    rclpy.init(args=args)
    node = SphereWanderer()

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
                if key == 's':
                    if node.stopped:
                        node.resume_sphere()
                    else:
                        node.stop_sphere()
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
