# Nomenclature and Symbol Table

This document defines every symbol, acronym, and subscript used across the system design.

---

## Greek Symbols

| Symbol | Definition | Units |
|--------|-----------|-------|
| α | Focal-loss weighting factor (class balance) | — |
| β | Blade surface inclination angle | rad |
| γ | Focal-loss focusing exponent | — |
| δx | Error-state vector (ESKF) | — |
| Δp | Suction pressure deficit (suction cup) | Pa |
| ΔK | Stress-intensity-factor range (Paris law) | MPa√m |
| Δσ | Cyclic stress range in blade laminate | MPa |
| ε | Auction optimality gap parameter | — |
| ζ | Damping ratio of control loop | — |
| η_FM | Figure of merit of rotor disc | — |
| η_es | Battery energy storage efficiency | — |
| η_wpt | Wireless power transfer efficiency | — |
| θ | Euler attitude angles (roll/pitch/yaw) | rad |
| κ | Cost-to-energy/time ratio (MRTA) | — |
| λ | Lagrange cost-weighting for MRTA penalty | — |
| λ_c | Cost multiplier for contact scan dispatch | — |
| µ | Pixel pitch of camera sensor | m/px |
| µ_f | Coefficient of friction (crawler adhesion) | — |
| ρ | Air density | kg/m³ |
| ρ_B | Bayes decision risk | — |
| σ_s | Predictive standard deviation of severity | — |
| σ²_s | Severity prediction variance | — |
| σ²_UT | UT sensor-limited severity variance | — |
| τ | Body torque vector on UAV | N·m |
| φ | Camera focal length | m |
| χ | Skid-steer slip/skid calibration factor | — |
| ψ | Heading/yaw angle | rad |
| ω_i | Rotor speed of motor i | rad/s |
| Ω_ij | Information matrix of SLAM edge (i,j) | — |

---

## Roman Symbols

| Symbol | Definition | Units |
|--------|-----------|-------|
| a | Crack length (Paris-law) | m |
| a_c | Critical crack length | m |
| a_0 | Initial crack length from UT scan | m |
| A | Total rotor disc area | m² |
| A_s | Suction footprint area (crawler) | m² |
| b_a | Accelerometer bias vector | m/s² |
| b_g | Gyroscope bias vector | rad/s |
| b | Track half-width (skid-steer UGV) | m |
| C | Paris-law material constant | — |
| c_L | Longitudinal ultrasonic wave speed | m/s |
| c_T | Rotor thrust coefficient | — |
| c_Q | Rotor torque coefficient | — |
| C_v | Battery cell capacity | Ah |
| d | Sensor-to-surface standoff distance | m |
| d* | Commanded standoff distance | m |
| D | Propeller diameter | m |
| D | Aerodynamic drag matrix (UAV) | kg/s |
| DoD | Battery depth of discharge | — |
| E_b | Usable battery energy | J |
| E_i | Energy budget for robot i | J |
| e_p | Position error vector | m |
| e_v | Velocity error vector | m/s |
| e_R | Geometric attitude error (SO(3)) | — |
| e_ω | Angular rate error vector | rad/s |
| e_ij | SLAM residual (edge i→j) | — |
| EVOC | Expected Value of Confirmation | — |
| f | Collective thrust (UAV) | N |
| F | ESKF state-transition matrix | — |
| g | Gravitational acceleration (9.81) | m/s² |
| G | Process-noise input matrix (ESKF) | — |
| GSD | Ground Sampling Distance | m/px |
| h_cg | Crawler centre-of-mass height | m |
| H | ESKF measurement Jacobian | — |
| H | MPC prediction horizon | steps |
| J | UAV inertia matrix | kg·m² |
| K | ESKF Kalman gain | — |
| k_f | Rotor thrust constant | N/(rad/s)² |
| k_m | Rotor torque constant | N·m/(rad/s)² |
| k_p, k_v | Position/velocity controller gains | — |
| k_R, k_ω | Attitude/rate controller gains | — |
| K_Ic | Mode-I fracture toughness | MPa√m |
| ℓ | UAV arm length (motor-to-centre) | m |
| m | UAV all-up mass | kg |
| m | Paris-law exponent | — |
| m_c | Crawler mass | kg |
| M_gust | Aerodynamic peel moment on crawler | N·m |
| M_gust | Gust moment on crawler | N·m |
| n | Number of scheduled tasks (RMS) | — |
| n_px | Minimum pixel span for defect detection | px |
| N | Normal preload force (suction adhesion) | N |
| N_RUL | Remaining useful life in load cycles | cycles |
| o_f, o_s | Forward and side image overlap fractions | — |
| p | World position vector | m |
| P | ESKF covariance matrix | — |
| P_av | Avionics power draw | W |
| P_chg | Charging power | W |
| P_hov | Hover power | W |
| P_r | Received RF power (Friis) | W |
| P_t | Transmitted RF power | W |
| Q | MPC state weighting matrix | — |
| Q | Process-noise covariance (ESKF) | — |
| Q_f | MPC terminal state weight | — |
| Q_i | Rotor drag torque | N·m |
| r | Inertial frame unit vector e₃ (body z) | — |
| r | Task reward (MRTA) | — |
| R | UAV rotation matrix (body→world) | SO(3) |
| R | ESKF measurement-noise covariance | — |
| R | MPC input weighting matrix | — |
| s | Defect severity score | ∈[0,1] |
| S | Swath width (coverage planner) | m |
| S | Friis link budget | — |
| SF | Safety factor (crawler adhesion) | — |
| SoC | Battery state of charge | — |
| t | Time-of-flight (UT pulse-echo) | s |
| t_chg | Recharge time | s |
| t_end | Flight endurance | s |
| T_i | Rotor thrust of motor i | N |
| T_max | Mission time budget | s |
| TWR | Thrust-to-weight ratio | — |
| u | Epistemic uncertainty of severity | — |
| u_ij | MRTA utility for robot i, task j | — |
| U | CPU utilisation (RMS schedulability) | — |
| v | UAV translational velocity | m/s |
| v_i | Rotor-induced velocity | m/s |
| v_nom | Battery nominal voltage | V |
| w_min | Minimum detectable defect width | m |
| W_px | Camera sensor width in pixels | px |
| x | Robot state vector | — |
| x_ij | MRTA assignment binary variable | {0,1} |
| Y | Stress-intensity geometry factor | — |
| z | Reflector depth (UT) | m |
| Z | Geofence zone polygon | — |

---

## Acronyms and Abbreviations

| Acronym | Expansion |
|---------|-----------|
| AE | Acoustic Emission |
| BT | Behaviour Tree |
| BVLOS | Beyond Visual Line of Sight |
| CBOR | Concise Binary Object Representation |
| CI | Continuous Integration |
| CONOPS | Concept of Operations |
| DDS | Data Distribution Service |
| DoD | Depth of Discharge |
| ESKF | Error-State Kalman Filter |
| EVOC | Expected Value of Confirmation |
| FCU | Flight Control Unit |
| FoM | Figure of Merit |
| GCS | Ground Control Station |
| GNSS | Global Navigation Satellite System |
| GSD | Ground Sampling Distance |
| HIL | Hardware-in-the-Loop |
| ICP | Iterative Closest Point |
| IMU | Inertial Measurement Unit |
| IoT | Internet of Things |
| IRT | Infrared Thermography |
| ISR | Interrupt Service Routine |
| LiDAR | Light Detection and Ranging |
| LWIR | Long-Wave Infrared |
| MPC | Model Predictive Control |
| MRTA | Multi-Robot Task Allocation |
| MQTT | Message Queuing Telemetry Transport |
| NDT | Normal Distributions Transform |
| NDE | Non-Destructive Evaluation |
| NIS | Normalised Innovation Squared |
| NEES | Normalised Estimation Error Squared |
| O&M | Operations and Maintenance |
| OTA | Over-the-Air (firmware update) |
| PID | Proportional-Integral-Derivative |
| QoS | Quality of Service |
| RMS | Rate-Monotonic Scheduling |
| RTK | Real-Time Kinematic (GNSS correction) |
| RUL | Remaining Useful Life |
| SE(3) | Special Euclidean group in 3D |
| SIL | Software-in-the-Loop |
| SLAM | Simultaneous Localisation and Mapping |
| SNR | Signal-to-Noise Ratio |
| SO(3) | Special Orthogonal group in 3D |
| SoC | State of Charge |
| SoS | System of Systems |
| TLS | Transport Layer Security |
| UAV | Unmanned Aerial Vehicle |
| UGV | Unmanned Ground Vehicle |
| UT | Ultrasonic Testing |
| UTM | Universal Transverse Mercator |
| UQ | Uncertainty Quantification |
| VIO | Visual-Inertial Odometry |
| WGS84 | World Geodetic System 1984 |
