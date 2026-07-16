from dataclasses import dataclass
from typing import Iterable, List
import numpy as np
from scipy.optimize import linear_sum_assignment


@dataclass
class Robot:
    robot_id: str
    capabilities: set[str]
    energy_budget: float


@dataclass
class Task:
    task_id: str
    task_type: str
    reward: float
    execution_cost: float
    required_capability: str


def utility(robot: Robot, task: Task, lam: float = 1.0) -> float:
    if task.required_capability not in robot.capabilities:
        return -1e9
    return task.reward - lam * task.execution_cost


def hungarian_allocate(robots: Iterable[Robot], tasks: Iterable[Task], lam: float = 1.0):
    robots = list(robots)
    tasks = list(tasks)
    if not robots or not tasks:
        return []

    cost = np.zeros((len(robots), len(tasks)), dtype=np.float64)
    for i, r in enumerate(robots):
        for j, t in enumerate(tasks):
            cost[i, j] = -utility(r, t, lam)

    row_ind, col_ind = linear_sum_assignment(cost)
    assignments = []
    for i, j in zip(row_ind, col_ind):
        if cost[i, j] > 1e8:
            continue
        assignments.append({
            "robot_id": robots[i].robot_id,
            "task_id": tasks[j].task_id,
            "utility": -float(cost[i, j])
        })
    return assignments
