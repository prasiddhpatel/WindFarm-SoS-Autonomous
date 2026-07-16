# WindFarm-SoS-Autonomous

> **Deployable Autonomous Multi-Robot System-of-Systems for Complete Wind Farm Operations & Maintenance**

[![ROS 2](https://img.shields.io/badge/ROS2-Humble-blue)](https://docs.ros.org/en/humble/)
[![License](https://img.shields.io/badge/License-Apache_2.0-green)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue)](docker/)
[![Python](https://img.shields.io/badge/Python-3.10+-yellow)](sos_orchestrator/)

---

## System Overview

This repository contains the **complete production codebase** for a heterogeneous Aerial–Ground System-of-Systems (SoS) designed for autonomous wind farm inspection, non-destructive evaluation (NDE), and maintenance decision-making.

### Constituent Systems

| ID | System | Role |
|----|--------|------|
| CS1 | Aerial Drone (UAV-A) | Multimodal triage: RGB + LWIR + LiDAR blade scanning |
| CS2 | Ground Robot (UGV-G) | Mobile dock/charger/relay + NDE crawler deployment |
| CS3 | Mission Server (M) | Digital twin, MRTA, RUL prognosis, fleet orchestration |
| CS4 | Human Supervisor (H) | Management-by-exception via operations dashboard |

---

## Repository Structure

```
 WindFarm-SoS-Autonomous/
 ├── docs/                          # Full technical report (LaTeX, 100+ pages)
 ├── ros2_ws/                       # ROS 2 workspace
 │   ├── src/
 │   │   ├── drone_bringup/         # UAV launch, URDF, config
 │   │   ├── drone_control/         # SE(3) geometric controller, mixer
 │   │   ├── drone_estimation/      # ESKF: GNSS/RTK+IMU+VIO+LiDAR
 │   │   ├── drone_perception/      # Detection, severity, calibrated UQ
 │   │   ├── drone_coverage/        # LiDAR-referenced standoff planner
 │   │   ├── ground_robot_bringup/  # UGV launch, URDF, config
 │   │   ├── ground_robot_nav/      # Pose-graph SLAM, MPC local planner
 │   │   ├── ground_robot_dock/     # Mobile docking, charging, relay
 │   │   ├── nde_crawler/           # Suction adhesion crawler + UT sizing
 │   │   ├── sos_interfaces/        # Custom ROS 2 msg/srv/action types
 │   │   └── safety_monitor/        # Watchdog, geofence, degraded modes
 ├── sos_orchestrator/              # Python: MRTA, RUL, EVOC, digital twin
 │   ├── mrta/                      # Multi-robot task allocation (Hungarian/auction)
 │   ├── digital_twin/              # Paris-law RUL, Bayesian belief fusion
 │   ├── telemetry/                 # MQTT broker client, store-and-forward
 │   ├── geospatial/                # UTM, geofence, R-tree spatial index
 │   └── api/                       # FastAPI operations REST + WebSocket
 ├── ops_dashboard/                 # React + Three.js live operations UI
 ├── infrastructure/                # Terraform, Docker Compose, k8s Helm charts
 ├── database/                      # TimescaleDB + PostGIS schema migrations
 ├── ml_models/                     # Training scripts, ONNX export, TensorRT
 ├── simulation/                    # Gazebo worlds, sensor plugins, CI launch
 ├── scripts/                       # Deployment, calibration, field-trial helpers
 └── tests/                         # Unit, SIL, HIL test suites
```

---

## Quick Start

### 1. Clone & pull submodules
```bash
git clone https://github.com/prasiddhpatel/WindFarm-SoS-Autonomous.git
cd WindFarm-SoS-Autonomous
git submodule update --init --recursive
```

### 2. Spin up the full stack with Docker Compose
```bash
cd infrastructure/
docker compose -f docker-compose.full.yml up -d
```
This brings up: ROS 2 bridge, MQTT broker, TimescaleDB + PostGIS, digital twin service, MRTA orchestrator, FastAPI operations API, and the React dashboard.

### 3. Run in simulation
```bash
# In the ROS 2 workspace
cd ros2_ws && colcon build --symlink-install
source install/setup.bash
ros2 launch simulation windfarm_full_sos.launch.py
```

### 4. Deploy to hardware
See `docs/deployment_guide.md` and `scripts/deploy_hardware.sh`.

---

## Key References
Full IEEE-cited technical report in `docs/Wind_Farm_SoS_Technical_Report_v2.pdf` (100+ pages).

## License
Apache 2.0 — see [LICENSE](LICENSE).
