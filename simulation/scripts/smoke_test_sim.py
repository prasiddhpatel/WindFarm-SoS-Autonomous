#!/usr/bin/env python3
"""Simulation smoke test: checks that Gazebo topics are bridged and live.

Usage (with running stack):
  python3 simulation/scripts/smoke_test_sim.py

Usage (CI / no Gazebo):
  python3 simulation/scripts/smoke_test_sim.py --no-ros
"""
import argparse, sys, time

PASS = '\033[92mPASS\033[0m'
FAIL = '\033[91mFAIL\033[0m'
SKIP = '\033[93mSKIP\033[0m'

EXPECTED_TOPICS = [
    '/imu/data',
    '/uav/ground_truth/odom',
    '/ugv/odom',
    '/camera/rgb',
    '/clock',
]


def check(label, cond, detail=''):
    print(f"  [{PASS if cond else FAIL}] {label}" + (f' — {detail}' if detail else ''))
    return cond


def check_ros_topics() -> bool:
    try:
        import rclpy
        from rclpy.node import Node
        rclpy.init()
        node = Node('smoke_test_node')
        time.sleep(1.0)
        active = [n for n, _ in node.get_topic_names_and_types()]
        ok = True
        for t in EXPECTED_TOPICS:
            ok &= check(f'topic {t}', t in active)
        node.destroy_node()
        rclpy.shutdown()
        return ok
    except Exception as e:
        print(f'  [{FAIL}] ROS topic check failed: {e}')
        return False


def check_bridge_config() -> bool:
    """Validate the bridge launch file can be imported without Gazebo running."""
    ok = True
    try:
        import importlib.util, os
        spec = importlib.util.spec_from_file_location(
            'sim_bridge',
            os.path.join(os.path.dirname(__file__), '..', 'launch', 'sim_bridge.launch.py')
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        ok &= check('sim_bridge.launch.py importable', hasattr(mod, 'generate_launch_description'))
    except Exception as e:
        ok &= check('sim_bridge.launch.py importable', False, str(e))
    try:
        spec2 = importlib.util.spec_from_file_location(
            'full_sim',
            os.path.join(os.path.dirname(__file__), '..', 'launch', 'full_sim.launch.py')
        )
        mod2 = importlib.util.module_from_spec(spec2)
        spec2.loader.exec_module(mod2)
        ok &= check('full_sim.launch.py importable', hasattr(mod2, 'generate_launch_description'))
    except Exception as e:
        ok &= check('full_sim.launch.py importable', False, str(e))
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--no-ros', action='store_true', help='Skip live ROS topic checks')
    args = ap.parse_args()

    print('=== Simulation Smoke Test ===')

    print('\n--- Bridge config check (no Gazebo needed) ---')
    ok = check_bridge_config()

    if not args.no_ros:
        print('\n--- Live ROS topic check ---')
        ok &= check_ros_topics()
    else:
        print('\n--- Live ROS topic check skipped (--no-ros) ---')

    print(f'\n=== {"ALL PASSED" if ok else "FAILURES DETECTED"} ===')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
