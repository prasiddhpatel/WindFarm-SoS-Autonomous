# WindFarm SoS Autonomous Inspection and Repair

## Executive Summary

This repository now contains a full-stack research-and-engineering scaffold for a wind-farm system-of-systems that combines an aerial vehicle, a mothership ground vehicle, and a blade-crawling NDE robot. The objective is to automate blade inspection, uncertainty-aware diagnosis, maintenance triage, and contact validation while reducing downtime, improving worker safety, and increasing repeatability. The platform integrates ROS 2 Humble packages, backend orchestration services, telemetry pipelines, digital-twin analytics, and operator-facing dashboards.

The architecture is derived from the project report and expanded into an implementation-oriented repository. It is organized so that perception, control, estimation, planning, task allocation, telemetry, storage, and deployment can evolve independently while remaining interoperable through clearly separated interfaces.

## Problem Context

Wind turbine blades accumulate erosion, lightning damage, cracks, debonds, adhesive failures, and other structural anomalies that reduce performance and create safety risks. Conventional inspection approaches are expensive, weather constrained, and labor intensive. Rope access methods expose technicians to hazards, and manual visual inspection often produces inconsistent documentation. Pure aerial inspection improves coverage speed but is limited when the defect requires confirmation of subsurface damage or ultrasonic inspection.

A system-of-systems approach addresses this gap by combining: (1) a UAV that performs rapid coverage inspection, (2) a UGV that acts as a mobile logistics, docking, compute, and communications hub, and (3) a crawler that performs local contact NDE. Instead of treating these robots as isolated assets, the repository models them as a coordinated fleet governed by shared utility, operational constraints, and common mission state.

## Research Objectives

The repository supports the following technical goals:

1. Accurate aerial inspection and georeferenced defect detection.
2. Robust relative localization near large turbine structures where GNSS can degrade.
3. Risk-aware task allocation between heterogeneous robots.
4. Digital-twin-based prioritization of blade defects using degradation and uncertainty metrics.
5. Reliable telemetry, storage, orchestration, and operator visualization.
6. Scalable deployment from local testing to cloud-backed edge operation.

## System Overview

The implemented scaffold uses three cooperating robotic subsystems:

### UAV Layer

The UAV provides RGB and LWIR sensing, close-proximity blade inspection, trajectory following, and rapid defect triage. The ROS 2 packages include a geometric controller, estimation stack, coverage planner, and perception node shell. These components reflect the report architecture in which the aerial robot first identifies probable anomalies and estimates severity together with uncertainty.

### UGV Layer

The UGV serves as a mobile docking, charging, networking, compute, and logistics platform. In the repository, the UGV-related stack includes navigation, docking, and orchestration integration. The ground vehicle is intended to position itself advantageously relative to turbine assets and support the crawler and UAV over long-duration missions.

### Crawler Layer

The crawler provides contact-based sensing such as ultrasonic inspection and acoustic or structural health measurements. Within the repository scaffold, the crawler package captures the software insertion point for adhesion-aware locomotion, target approach, and contact validation workflows. This role is important because many severe blade faults cannot be fully characterized from vision alone.

## ROS 2 Workspace Design

The ROS 2 workspace is arranged around packages that separate flight-critical functions, estimation, perception, planning, and supervisory logic.

### drone_control

This package contains the SE(3) geometric control implementation, actuator allocation logic, and mixer node for translating high-level control outputs into motor speed commands. The controller structure aligns with nonlinear rigid-body control methods and is suitable for aggressive flight and disturbance rejection near blade surfaces.

### drone_estimation

This package introduces an error-state Kalman filter scaffold that fuses IMU propagation with delayed correction from absolute and relative measurements. The estimator is intended to support GNSS, RTK, VIO, and LiDAR-relative pose streams. Near turbines, this fusion approach is preferable to pure GNSS because metallic structures and line-of-sight disruptions can degrade satellite-based localization.

### drone_coverage

This package covers geometric blade-surface planning and trajectory generation. The included boustrophedon planner and minimum-snap trajectory interfaces follow the inspection pattern described in the report: maintain standoff, satisfy image overlap and ground-sampling constraints, and generate smooth trajectories that the flight controller can track.

### drone_perception

This package is the insertion point for multimodal blade defect analytics. The current implementation scaffold assumes fused RGB and thermal evidence, severity regression, uncertainty estimation, and downstream publication of defect hypotheses. In a complete product system, this package would also support model export, batching, and patch-level temporal fusion.

### ground_robot_nav and ground_robot_dock

These packages support skid-steer local motion control, route following, and docking behavior. The docking role is central to the SoS concept because the UAV and crawler become more useful when the ground asset can move the recharge, relay, and compute node close to each worksite.

### nde_crawler and safety_monitor

The crawler package captures the control entry point for contact inspection execution, while the safety monitor package centralizes watchdog, geofence, and degraded-mode management. Safety isolation is especially important in inspection systems operating close to blades, towers, and valuable infrastructure.

### windfarm_bringup

This package aggregates launch descriptions so that the system can be composed as a coherent operational graph instead of a collection of disconnected nodes. As the repository matures, this package becomes the canonical entry point for simulation, lab bringup, and field trials.

## Backend and Orchestration Architecture

The backend stack complements the ROS 2 workspace and provides persistence, mission state, telemetry, digital-twin analytics, and operator access.

### FastAPI Services

The API layer exposes health, patch, task, turbine, RUL, and EVOC endpoints. This allows a dashboard or external orchestration service to inspect current fleet state and invoke decision-support analytics without directly coupling to ROS 2 internals.

### Relational and Spatial Storage

PostGIS is used for structured mission and asset data such as turbines, blade patches, inspections, and task records. Spatial indexing supports future queries involving geofences, turbine locations, and defect coordinates. This is essential when field deployments span multiple turbines and repeated missions.

### Telemetry Storage

TimescaleDB is introduced for time-series telemetry and health events. Separation between mission-state storage and high-rate telemetry is useful because it allows different retention, indexing, and analytics strategies while avoiding schema overload.

### Redis and MQTT

Redis supports fast state handling and queue-oriented patterns, while MQTT supports lightweight robot-to-backend messaging with a store-and-forward client. The repository’s telemetry client is designed so that temporary network interruptions do not immediately lose mission data.

### MRTA and Utility-Based Allocation

The repository contains both Hungarian-style assignment and auction-style task allocation skeletons. The general design assumption is that tasks such as aerial triage, docking support, and contact NDE should be assigned according to expected utility, compatibility, and cost instead of fixed robot-role mappings.

## Digital Twin and Maintenance Decision Logic

A central design theme is that defect triage should be risk aware rather than purely confidence based.

### Paris-Law-Based RUL

The repository includes a Paris-law-inspired remaining useful life module. This provides a starting point for linking observed crack extent or inferred defect metrics to maintenance urgency. Even when exact material parameters vary by blade make and damage mode, the scaffold is valuable because it formalizes how defect size can map to engineering consequence.

### EVOC Scoring

The EVOC module captures the expected value of additional contact inspection. In operational terms, it answers whether sending the crawler for contact validation is worth the cost, delay, and resource consumption. This is one of the most important concepts in the repository because it converts uncertain perception output into mission-action decisions.

### Patch-Centric Fleet Reasoning

The schema treats blade patches as the durable coordination unit across inspections. This is useful because perception, RUL estimation, uncertainty, recommendations, and follow-up actions can all attach to the same patch abstraction over time.

## Dashboard and Operator Interface

The React/Vite dashboard is a deliberately simple but important layer in the repository. It demonstrates how backend data can be exposed in a way that supports field supervision.

The interface includes turbine counts, tracked patch counts, task counts, severity plots, task utility plots, a patch table, and a simple 3D twin-style visualization. Even though the current implementation is lightweight, it establishes the structure required for future operator workflows such as maintenance approval, mission re-tasking, and fleet health auditing.

## Simulation Strategy

Simulation is essential for safe iteration because many failure modes near wind turbines are difficult and expensive to test directly in the field.

The repository now includes a Gazebo-style world, a simplified wind-farm scene, and initial UAV and UGV models. These are not yet a full fidelity aeroelastic environment, but they provide the first executable substrate for validating package interactions, messaging, and system composition.

A full simulation roadmap should include:

1. Turbine blade geometry with collision meshes and inspection surfaces.
2. Wind disturbance models and gust injection.
3. Sensor noise and delay models for IMU, GNSS, LiDAR, RGB, LWIR, and ultrasound.
4. Docking and contact-inspection scenarios.
5. Multi-robot mission scripts and failure injection.

## Testing and Verification

The repository now contains unit tests for task allocation, digital-twin logic, and API endpoints. This is a necessary step toward moving from concept scaffold to maintainable software system.

The current test philosophy is layered:

- Unit tests validate numerical and decision modules such as Hungarian allocation, auctions, RUL calculations, and EVOC scoring.
- API tests validate basic service behavior independently of live database deployments.
- Smoke tests validate that a local stack can expose health endpoints and basic process integration.
- CI workflows validate backend installation, dashboard build behavior, and partial ROS 2 build checks.

Over time, verification should expand to include hardware-in-the-loop testing, rosbag replay, deterministic simulation scenarios, and fault-containment tests for safety logic.

## Deployment Model

The repository now spans local, edge, and cloud-oriented deployment layers.

### Local Compose Stack

Docker Compose is used for local integration of MQTT, databases, Redis, the API, the orchestrator worker, and the dashboard. This is the fastest route for developer iteration and end-to-end smoke testing.

### Terraform and Infrastructure as Code

Terraform files define a cloud-edge server pattern on GCP. This captures the intended evolution from local experimentation to reproducible field infrastructure.

### Kubernetes Manifests

Kubernetes deployment files are included for API and dashboard services. These are early-stage manifests, but they establish the pattern for containerized scale-out and secret-backed runtime configuration.

## Safety and Operational Constraints

Any fieldable version of this system must treat safety as a first-class engineering concern.

Important safety domains include:

- Geofence enforcement around turbine structures and no-fly/no-drive zones.
- Loss-of-link recovery and store-and-forward telemetry resilience.
- Low-battery and docking contingency handling.
- Blade proximity management and contact-force constraints.
- Task preemption and fail-safe mission abort behavior.
- Human override and maintenance approval workflows.

The current repository establishes these themes in package structure and monitoring nodes, but a certifiable implementation would require substantially deeper hazard analysis, formal safety cases, and validation records.

## Gaps and Future Work

Although the repository is now much more substantial, it is still a scaffold rather than a complete production system. The most important next steps are:

1. Make the ROS 2 workspace colcon-clean across all packages with full dependency declarations.
2. Add real message definitions, action servers, and complete launch parameterization.
3. Integrate actual learned perception models and data pipelines.
4. Improve the Gazebo models, bridges, and scenario launch orchestration.
5. Add ingestion of rosbag telemetry and mission playback.
6. Expand dashboard interactivity and mission editing.
7. Add stronger auth, secrets handling, and deployment hardening.
8. Create benchmark scenarios and quantitative evaluation scripts.
9. Add documentation that traces report claims to repository modules.
10. Introduce reproducible demo missions for reviewers and supervisors.

## Suggested Dissertation-Style Chapter Mapping

To support the goal of expanding the project toward a near-100-page report, the repository contents can be mapped into dissertation-style chapters:

1. Introduction and motivation.
2. Wind turbine O&M problem framing.
3. Related work in aerial inspection, field robotics, and NDE.
4. System-of-systems architecture.
5. UAV control and estimation.
6. Coverage planning and blade-relative navigation.
7. Multimodal perception and uncertainty quantification.
8. UGV docking and logistics support.
9. Crawler contact inspection and validation workflows.
10. MRTA and utility-based fleet coordination.
11. Digital twin, RUL, and EVOC-based maintenance decisions.
12. Backend, telemetry, and operator interfaces.
13. Simulation, verification, and testing.
14. Field deployment strategy and limitations.
15. Conclusions and future work.

## Conclusion

This repository now functions as an implementation-oriented companion to the project report. It expresses the key thesis that wind turbine maintenance automation is most effective when aerial inspection, contact inspection, mission planning, uncertainty reasoning, and fleet orchestration are unified inside a coherent robotic software architecture.

The codebase does not yet prove all of the research claims experimentally, but it now provides a meaningful technical substrate on which those claims can be evaluated, extended, and defended.
