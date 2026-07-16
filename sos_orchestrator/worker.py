import time
from mrta.hungarian import Robot, Task, hungarian_allocate
from telemetry.mqtt_client import telemetry_client


def main():
    telemetry_client.connect()

    while True:
        robots = [
            Robot(robot_id="uav_a_01", capabilities={"triage", "relay"}, energy_budget=1000.0),
            Robot(robot_id="ugv_g_01", capabilities={"dock", "transport", "nde"}, energy_budget=3000.0),
        ]
        tasks = [
            Task(task_id="task_triage_wtg07_b0", task_type="triage", reward=8.5, execution_cost=2.0, required_capability="triage"),
            Task(task_id="task_nde_wtg07_patch21", task_type="contact_nde", reward=9.5, execution_cost=4.0, required_capability="nde"),
        ]
        assignments = hungarian_allocate(robots, tasks, lam=1.2)
        telemetry_client.publish_json("fleet/orchestrator/assignments", {"assignments": assignments}, qos=1)
        telemetry_client.flush()
        time.sleep(5)


if __name__ == "__main__":
    main()
