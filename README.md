# WindFarm-SoS-Autonomous

[![CI](https://github.com/prasiddhpatel/WindFarm-SoS-Autonomous/actions/workflows/ci.yml/badge.svg)](https://github.com/prasiddhpatel/WindFarm-SoS-Autonomous/actions/workflows/ci.yml)

Autonomous wind turbine inspection and maintenance using a heterogeneous System-of-Systems:
a quadrotor **UAV** (aerial imaging + coverage), a wheeled **UGV** mothership (logistics + recharging),
and a magnetic-adhesion **NDE crawler** (contact ultrasonic testing).

## Repository map

| Area | Path | Description |
|---|---|---|
| ROS 2 packages | `ros2_ws/src/` | Control, estimation, coverage, perception, nav, dock, crawler, safety, interfaces, bringup |
| SoS orchestrator | `sos_orchestrator/` | FastAPI, MRTA, digital twin (Paris RUL + EVOC), telemetry, database |
| Operator dashboard | `ops_dashboard/` | React/Vite, WebSocket, Leaflet, severity charts |
| Database | `database/` | PostGIS + TimescaleDB schema, seed script |
| Infrastructure | `infrastructure/` | Docker Compose, Kubernetes, Terraform, MQTT |
| Simulation | `simulation/` | Gazebo Harmonic SDF world, ROS–GZ bridge launch, smoke test |
| Training | `training/` | BladeDefectDataset, EfficientNet-B0 train script, synthetic data generator |
| Tests | `tests/` | pytest suite (backend, perception, dataset, sim, E2E orchestration) |
| Docs | `docs/` | Dissertation draft, results tables, architecture notes, evaluation plan |

## CI jobs

| Job | What it runs |
|---|---|
| `backend-unit` | pytest — API, MRTA, RUL, EVOC + integration validator |
| `perception-unit` | pytest — fusion, ModelRunner, MCDropout, dataset, sim config |
| `e2e-orchestration` | pytest — full MRTA → RUL → EVOC → perception → API pipeline |
| `dashboard-build` | `npm install && npm run build` |
| `ros2-build-check` | 5-step ordered colcon build inside `ros:humble-ros-base` container |

## Quick start

### Backend stack

```bash
cd infrastructure
docker compose -f docker-compose.full.yml up -d --build
python3 database/seed_demo.py          # insert 2 turbines + 6 blade patches
```

### ROS 2 build

```bash
cd ros2_ws
bash build.sh                          # 4-stage ordered colcon build
source install/setup.bash
ros2 launch windfarm_bringup full_system.launch.py
```

### Simulation

```bash
# Requires gz-harmonic + ros-humble-ros-gz-bridge
ros2 launch simulation/launch/full_sim.launch.py
```

### Training

```bash
python3 training/generate_synthetic_data.py --output-dir data/ --n-per-class 50
python3 training/train.py --data-root data/ --epochs 10 --output-dir weights/
python3 -m drone_perception.model_export --checkpoint weights/blade_defect_best.pt
```

### Tests

```bash
pip install pytest httpx numpy scipy pillow
PYTHONPATH=sos_orchestrator:ros2_ws/src/drone_perception pytest tests/ -v
```

### Integration validator

```bash
# No live stack:
PYTHONPATH=sos_orchestrator python3 tests/integration_validation.py --no-live
# With live stack:
PYTHONPATH=sos_orchestrator python3 tests/integration_validation.py --base http://localhost:8080
```

## Key subsystems

### Perception pipeline

```
RGB + Thermal  →  _preprocess (224×224, 4-ch normalise)
               →  ONNX Runtime (GPU/CPU) or mock logits
               →  InferenceResult (class, severity, aleatoric, epistemic)
               →  SeverityTemporalFusion (EMA α=0.3)
               →  DEFECT ALERT if severity > threshold
```

### EVOC dispatch decision

```
EVOC = Δrisk · (σ²_sev + σ²_ut) / (σ²_sev + σ²_ut + ε)
Dispatch NDE crawler if  EVOC / scan_cost > λ
```

### Paris-law RUL

```
da/dN = C · (Y·Δσ·√(πa))^m
Integrate a0 → a_c = (K_IC / (Y·σ_max·√π))²  →  RUL in days
```

## Status

This is a research prototype / dissertation artefact. All subsystems are implemented and CI-tested.
Real trained weights, full Gazebo physics, and hardware integration are future work.

## Documentation

- [`docs/dissertation_draft.md`](docs/dissertation_draft.md) — full dissertation (Chapters 1–7)
- [`docs/results_tables.md`](docs/results_tables.md) — all quantitative results tables
- [`docs/architecture_notes.md`](docs/architecture_notes.md) — deep-dive architecture
- [`docs/evaluation_plan.md`](docs/evaluation_plan.md) — evaluation framework
- [`docs/evaluation_metrics.md`](docs/evaluation_metrics.md) — metric definitions and protocols
- [`docs/integration_validation_guide.md`](docs/integration_validation_guide.md) — validation guide
- [`docs/perception_pipeline.md`](docs/perception_pipeline.md) — perception pipeline detail
- [`docs/build_hardening_notes.md`](docs/build_hardening_notes.md) — ROS 2 build notes
