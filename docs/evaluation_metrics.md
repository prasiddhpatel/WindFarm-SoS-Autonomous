# Evaluation Metrics and Experiment Designs

## M1 — MRTA Allocation Quality

- **Metric:** Normalised assignment cost vs optimal (Hungarian baseline)
- **Protocol:** Generate random capability-matched scenarios (N=100), compare auction vs Hungarian cost
- **Target:** Auction within 5% of optimal for fleets ≤ 6 robots

## M2 — Defect Detection Performance

- **Metrics:** Per-class precision, recall, F1; macro-averaged mAP
- **Protocol:** Train/val/test split on annotated blade dataset; report on held-out test set
- **Target:** mAP ≥ 0.85 on crack and delamination classes

## M3 — RUL Estimation Accuracy

- **Metric:** Mean absolute error (MAE) of predicted RUL vs ground-truth fatigue test data
- **Protocol:** Compare Paris-law RUL against NREL/DTU fatigue coupon results
- **Target:** MAE < 15% of mean ground-truth RUL

## M4 — EVOC Decision Calibration

- **Metric:** Decision accuracy (dispatch/no-dispatch) vs retrospective ground truth
- **Protocol:** Simulate 500 inspection episodes; compare EVOC decision against post-hoc optimal
- **Target:** Decision accuracy ≥ 90%

## M5 — Coverage Path Efficiency

- **Metric:** Path length vs minimum bounding-box sweep; redundant overlap fraction
- **Protocol:** Benchmark on 5 synthetic blade shapes
- **Target:** Path length within 20% of theoretical minimum; overlap within [25%, 35%]

## M6 — Temporal Fusion Convergence Rate

- **Metric:** Number of observations to reach within 5% of true severity
- **Protocol:** Sweep α ∈ {0.1, 0.2, 0.3, 0.5} with synthetic constant-severity sequences
- **Target:** Convergence within 20 observations for α ≥ 0.2

## M7 — End-to-End Latency

- **Metric:** Time from image capture to EVOC dispatch decision (pipeline latency)
- **Protocol:** Profile perception_node tick at 2 Hz with mock inference
- **Target:** < 500 ms per decision cycle
