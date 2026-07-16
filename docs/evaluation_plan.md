# Evaluation Plan

## Metrics

The following metrics are suitable for turning this repository into a defensible dissertation or capstone artifact:

### Flight and Estimation
- RMS trajectory tracking error.
- Blade-relative standoff error.
- Hover stability under lateral gust disturbances.
- Pose drift over tower-proximal trajectories.

### Inspection Coverage
- Surface coverage percentage.
- Overlap compliance.
- Mission duration per blade.
- Energy consumed per inspection pass.

### Perception
- Patch detection precision and recall.
- Severity regression MAE.
- Uncertainty calibration error.
- Thermal-visual fusion gain over unimodal baselines.

### Fleet Coordination
- Mean task utility achieved.
- Task completion latency.
- Contact-validation dispatch rate.
- Percentage of high-risk patches escalated correctly.

### Maintenance Decision Support
- EVOC policy gain against fixed dispatch baselines.
- RUL ranking consistency.
- False defer / false escalate rates.

### Systems Engineering
- Backend API latency.
- Telemetry packet loss under link interruption.
- Dashboard refresh latency.
- Mean time to recover after service restart.

## Experimental Campaigns

1. Single-turbine inspection baseline.
2. Multi-turbine scheduling scenario.
3. GNSS degradation near structure.
4. Contact-NDE selective dispatch using EVOC.
5. Telemetry drop and recovery test.
6. Docking and recharge continuity scenario.

## Reporting Format

Each experiment chapter should include:
- Scenario description.
- Variables and assumptions.
- Quantitative results.
- Failure cases.
- Interpretation.
- Threats to validity.
