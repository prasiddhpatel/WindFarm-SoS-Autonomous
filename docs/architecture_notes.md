# Architecture and Implementation Notes

## Purpose

This note explains how the repository is structured so that reviewers can connect report-level claims to executable modules. It is intended to bridge the gap between a conceptual systems report and the current implementation scaffold.

## Traceability Matrix

| Report Theme | Repository Area | Current Status |
| --- | --- | --- |
| UAV nonlinear control | `ros2_ws/src/drone_control` | Core structure present |
| Multi-sensor fusion | `ros2_ws/src/drone_estimation` | Scaffold present |
| Inspection path planning | `ros2_ws/src/drone_coverage` | Scaffold present |
| Defect analytics | `ros2_ws/src/drone_perception` | Python shell present |
| UGV logistics and docking | `ros2_ws/src/ground_robot_nav`, `ground_robot_dock` | Partial scaffold |
| Crawler NDE execution | `ros2_ws/src/nde_crawler` | Entry-point scaffold |
| Safety supervision | `ros2_ws/src/safety_monitor` | Partial scaffold |
| Fleet orchestration | `sos_orchestrator` | Core scaffold present |
| Digital twin analytics | `sos_orchestrator/digital_twin` | Initial analytical modules present |
| Dashboard and operator UI | `ops_dashboard` | Initial working frontend scaffold |
| Databases and telemetry | `database`, `infrastructure`, `sos_orchestrator/telemetry` | Core stack present |
| Simulation and tests | `simulation`, `tests`, `.github/workflows` | Initial executable baseline present |

## Package Relationships

The intended interaction flow is:

1. The UAV estimates state and executes blade-relative trajectories.
2. Perception produces patch-level defect hypotheses and uncertainty.
3. The backend stores patch observations and computes RUL or EVOC-derived prioritization.
4. MRTA modules assign follow-up work to the best-suited robot.
5. The dashboard exposes resulting mission and maintenance state to the operator.

## What is Real vs Placeholder

Several parts of the repository are executable today, including the backend service skeleton, database schema, dashboard build, and a subset of algorithmic modules. Several other parts are intentionally placeholders, including some ROS 2 nodes, simulation fidelity, and full robot hardware integration. This distinction matters because the repository is intended to demonstrate architecture and implementation momentum rather than claim complete field readiness.

## Evidence Strategy for Final Report

A strong final report built on top of this repository should include:

- Build status for ROS 2 packages and backend services.
- Unit and integration test pass rates.
- Example mission scenarios in simulation.
- Case studies of patch prioritization using EVOC and RUL.
- Quantitative discussion of latency, allocation quality, and mission throughput.
- Explicit limitations where modules are still scaffold-grade.
