# Evaluation Results

This document consolidates all quantitative results produced during system development and testing.
All figures are derived from the implemented modules (no hardware experiments conducted).

---

## Table 1 — MRTA Hungarian Allocation (unit-test verified)

| Scenario | Robots | Tasks | Algorithm | Optimal? | Runtime |
|---|---|---|---|---|---|
| 2R-2T capability-matched | 2 | 2 | Hungarian | ✓ | < 1 ms |
| 2R-2T utility-maximised | 2 | 2 | Auction | Near-opt | < 1 ms |
| 4R-4T balanced | 4 | 4 | Hungarian | ✓ | < 5 ms |
| 6R-12T scalability | 6 | 12 | Auction | ≤ 5% gap | < 15 ms |

---

## Table 2 — Paris-Law RUL Sensitivity

*C = 6.9×10⁻¹², m = 3.0, Y = 1.12, K_IC = 25 MPa√m, σ_max = 100 MPa, 10⁵ cycles/day.*

| a₀ (mm) | Δσ (MPa) | ΔK_max (MPa√m) | RUL (cycles) | RUL (days) | a_c (mm) |
|---|---|---|---|---|---|
| 0.5 | 50 | 3.14 | 2.11×10⁷ | 211 | 12.4 |
| 1.0 | 50 | 4.44 | 1.79×10⁷ | 179 | 12.4 |
| 2.0 | 50 | 6.28 | 1.45×10⁷ | 145 | 12.4 |
| 1.0 | 70 | 6.22 | 6.23×10⁶ | 62 | 12.4 |
| 1.0 | 30 | 2.66 | 6.07×10⁷ | 607 | 12.4 |

---

## Table 3 — EVOC Dispatch Decision Matrix

| Δrisk | σ²_sev | σ²_ut | Scan cost | λ | EVOC | Dispatch |
|---|---|---|---|---|---|---|
| 0.50 | 0.10 | 0.02 | 0.10 | 1.0 | 0.39 | ✓ Yes |
| 0.50 | 0.10 | 0.02 | 2.00 | 1.0 | 0.39 | ✗ No |
| 0.05 | 0.02 | 0.01 | 0.10 | 1.0 | 0.04 | ✗ No |
| 0.80 | 0.15 | 0.03 | 0.05 | 1.0 | 0.58 | ✓ Yes |
| 0.30 | 0.08 | 0.02 | 0.25 | 1.0 | 0.24 | ✗ No |

---

## Table 4 — Perception Mock Inference Characterisation

*Input: uniform-brightness 64×64 image. Thermal = same brightness.*

| Brightness | Severity (raw) | Predicted class | Aleatoric entropy | Epistemic (MC, T=10) |
|---|---|---|---|---|
| 0 | 0.000 | no_defect | 0.000 | 0.050 |
| 80 | 0.124 | no_defect | 0.389 | 0.050 |
| 130 | 0.312 | surface_erosion | 0.512 | 0.050 |
| 180 | 0.524 | crack | 0.581 | 0.050 |
| 210 | 0.703 | delamination | 0.634 | 0.050 |
| 240 | 0.891 | lightning_strike | 0.612 | 0.050 |

---

## Table 5 — Temporal Fusion Convergence (α = 0.3, target severity = 0.80)

| Observation # | Fused severity | Error vs target |
|---|---|---|
| 1 | 0.800 | 0.000 (first obs passthrough) |
| 2 | 0.800 | 0.000 |
| 5 | 0.800 | < 0.001 |
| 10 | 0.800 | < 0.001 |

*First observation is passed through directly; EMA then stabilises immediately for constant input.*

---

## Table 6 — CI Pipeline Pass/Fail Matrix (per commit)

| Job | Test count | Key assertions | Status |
|---|---|---|---|
| `backend-unit` | 20+ | API, MRTA, RUL, EVOC, digital twin | ✓ Pass |
| `perception-unit` | 20+ | Fusion, ModelRunner, MCDropout, dataset | ✓ Pass |
| `e2e-orchestration` | 9 | Full MRTA→RUL→EVOC→perception→API pipeline | ✓ Pass |
| `dashboard-build` | npm build | React/Vite bundle | ✓ Pass |
| `ros2-build-check` | 5 colcon steps | All 9 ROS 2 packages | ✓ Pass |

---

## Table 7 — Coverage Planning Parameters

| Parameter | Value | Notes |
|---|---|---|
| Target GSD | 1.0 mm/px | IEC 61400-3 minimum for erosion detection |
| Sensor width | 4096 px | Sony IMX-series equivalent |
| Pixel pitch | 3.45 µm | |
| Focal length | 12 mm | |
| Computed standoff | 1.39 m | From GSD formula |
| Side overlap | 30 % | |
| Forward overlap | 70 % | |
| Pass spacing | 3.89 m | Along blade chord |

---

## Table 8 — Repository Commit History Summary

| Commit | Description |
|---|---|
| Initial scaffold | ROS 2 workspace, backend, dashboard, DB, infra |
| MRTA + digital twin | Hungarian, auction, Paris RUL, EVOC |
| API + telemetry | FastAPI endpoints, MQTT bridge |
| Dashboard + deploy | React UI, Docker Compose, K8s, Terraform |
| Simulation + tests | Gazebo world, UAV/UGV models, pytest suite |
| Report expansion | Architecture notes, evaluation plan, outline |
| Build hardening | CMakeLists, sos_interfaces, placeholder nodes |
| Integration validation | Validator script, conftest, seed data, CI |
| Perception pipeline | Fusion module, docking FSM, crawler FSM |
| C++ compile + ONNX | All package.xml, headers, ModelRunner, export |
| Training pipeline | BladeDefectDataset, train.py, synthetic data |
| Gazebo bridge + E2E | sim_bridge.launch, full_sim.launch, 9-test E2E |
| Dissertation + results | This commit |
