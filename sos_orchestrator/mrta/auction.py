from dataclasses import dataclass
from typing import Dict, List


@dataclass
class Bid:
    robot_id: str
    task_id: str
    bid_value: float


def auction_allocate(robot_utilities: Dict[str, Dict[str, float]]) -> List[dict]:
    bids: List[Bid] = []
    for robot_id, task_map in robot_utilities.items():
        sorted_tasks = sorted(task_map.items(), key=lambda kv: kv[1], reverse=True)
        if not sorted_tasks:
            continue
        best_task, best_u = sorted_tasks[0]
        second_u = sorted_tasks[1][1] if len(sorted_tasks) > 1 else 0.0
        bids.append(Bid(robot_id=robot_id, task_id=best_task, bid_value=best_u - second_u))

    winners = {}
    for bid in bids:
        current = winners.get(bid.task_id)
        if current is None or bid.bid_value > current.bid_value:
            winners[bid.task_id] = bid

    return [
        {"task_id": b.task_id, "robot_id": b.robot_id, "bid_value": b.bid_value}
        for b in winners.values()
    ]
