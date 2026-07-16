# WindFarm-SoS-Autonomous

WindFarm-SoS-Autonomous is a research-to-implementation repository for a coordinated wind turbine inspection and maintenance system-of-systems using a UAV, a UGV mothership, and a contact-NDE crawler.

## Repository areas

- `ros2_ws/`: ROS 2 packages for control, estimation, planning, perception, ground robotics, safety, interfaces, and bringup.
- `sos_orchestrator/`: backend orchestration, digital twin analytics, API, MRTA, and telemetry.
- `ops_dashboard/`: React/Vite operator dashboard.
- `database/`: SQL initialization for PostGIS and TimescaleDB.
- `infrastructure/`: Docker Compose, Kubernetes, Terraform, and MQTT configuration.
- `simulation/`: simulation assets, launch files, and smoke-test utilities.
- `tests/`: backend/API unit tests.
- `docs/`: report-expansion and architecture material.

## Quick start

### Backend stack

```bash
cd infrastructure
docker compose -f docker-compose.full.yml up -d --build
```

### ROS 2 build

```bash
cd ros2_ws
bash build.sh
source install/setup.bash
ros2 launch windfarm_bringup full_system.launch.py
```

### Tests

```bash
pytest tests/ -v
```

## Status

This repository now contains substantial implementation scaffolding, but some modules remain placeholder-grade and require further integration/hardening for field or demo readiness.
