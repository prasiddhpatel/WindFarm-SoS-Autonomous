import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'sos_orchestrator'))


def test_hungarian_basic():
    from mrta.hungarian import Robot, Task, hungarian_allocate
    robots = [
        Robot('uav_a', {'triage'}, 1000.0),
        Robot('ugv_g', {'nde'}, 2000.0),
    ]
    tasks = [
        Task('t1', 'triage', 8.0, 2.0, 'triage'),
        Task('t2', 'nde', 9.0, 3.0, 'nde'),
    ]
    assignments = hungarian_allocate(robots, tasks, lam=1.0)
    assert len(assignments) == 2
    robot_ids = {a['robot_id'] for a in assignments}
    assert 'uav_a' in robot_ids
    assert 'ugv_g' in robot_ids


def test_hungarian_no_compatible_robot():
    from mrta.hungarian import Robot, Task, hungarian_allocate
    robots = [Robot('ugv_g', {'nde'}, 2000.0)]
    tasks = [Task('t1', 'triage', 8.0, 2.0, 'triage')]
    assignments = hungarian_allocate(robots, tasks, lam=1.0)
    assert assignments == []


def test_hungarian_empty():
    from mrta.hungarian import Robot, Task, hungarian_allocate
    assert hungarian_allocate([], [], 1.0) == []


def test_auction_basic():
    from mrta.auction import auction_allocate
    robot_utilities = {
        'uav_a': {'t1': 6.0, 't2': 3.0},
        'ugv_g': {'t1': 2.0, 't2': 7.0},
    }
    result = auction_allocate(robot_utilities)
    assigned = {r['task_id']: r['robot_id'] for r in result}
    assert assigned.get('t1') == 'uav_a'
    assert assigned.get('t2') == 'ugv_g'
