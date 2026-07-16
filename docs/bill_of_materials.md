# Bill of Materials — Industrial Grade Components

All components selected for **IP54+ sealing**, operation in **−20 °C to +55 °C**, wind up to **12 m/s** for UAV and **20 m/s** ground ops, and **offshore salt-spray** environments.

---

## CS1 — Aerial Drone (UAV-A)

### Airframe & Propulsion

| # | Component | Manufacturer / Model | Spec | Qty | Unit Cost (€) |
|---|-----------|---------------------|------|-----|---------------|
| 1 | Carbon-fibre X-frame 500mm | Tarot / T-18 octo adapted to X550 | 550 mm diagonal, 3K CF, 420 g | 1 | 180 |
| 2 | Brushless motor | T-Motor MN505-S KV320 | 320 KV, 14-pole, IP44, 200 g | 4 | 85 |
| 3 | Propeller pair | T-Motor P15×5.0 CF | 15" 2-blade CF, CW+CCW pair | 2 pair | 35 |
| 4 | ESC 40A FOC | T-Motor FLAME 40A | 40 A, BLHeli32, telemetry, 38 g | 4 | 45 |
| 5 | Battery pack | Tattu Plus 22000 mAh 6S | 22 Ah, 6S LiHV, 22.2 V, 1760 g | 2 | 310 |
| 6 | Battery management board | Furious FPV Smart 6S BMS | Cell balancing, over-temp cut-off | 2 | 28 |
| 7 | Power distribution board | Matek FCHUB-9V | 9× pads, 5V/9V BEC, 35 g | 1 | 22 |
| 8 | Vibration isolation mount | Tarot TL2955 damping plate | Anti-vibration, 4× M3 standoffs | 1 | 18 |

### Flight Control & Compute

| # | Component | Manufacturer / Model | Spec | Qty | Unit Cost (€) |
|---|-----------|---------------------|------|-----|---------------|
| 9 | Flight Control Unit | Hex Cube Orange+ | STM32H7, FMUv6, dual IMU, CAN | 1 | 290 |
| 10 | Redundant IMU | ADIS16448 (external) | ±2000 °/s, ±18 g, SPI, IP67 | 1 | 340 |
| 11 | Mission computer | NVIDIA Orin NX 16 GB | 100 TOPS, 8-core ARM, 10W–25W | 1 | 620 |
| 12 | NVMe SSD | WD Red SN700 1TB | 1 TB NVMe, –40 to +85 °C | 1 | 95 |
| 13 | ROS 2 / DDS bridge | micro-ROS on FCU | Serial/UDP bridge to Orin | 1 | — |
| 14 | CAN bus isolator | Kvaser Leaf Light v2 | USB-CAN, 1 Mbit/s | 1 | 145 |

### Sensing — Navigation

| # | Component | Manufacturer / Model | Spec | Qty | Unit Cost (€) |
|---|-----------|---------------------|------|-----|---------------|
| 15 | GNSS/RTK module | u-blox ZED-F9P | RTK ±1 cm, multi-constellation | 1 | 195 |
| 16 | RTK corrections radio | Holybro SiK 915 MHz | 915 MHz, 500 mW, 30 km LOS | 1 | 55 |
| 17 | Solid-state LiDAR | Livox Mid-360 | 40 m, 200k pts/s, 360° FOV | 1 | 820 |
| 18 | Visual-inertial cam | Intel RealSense T265 | 2×OV9282, IMU, SLAM firmware | 1 | 215 |
| 19 | Magnetometer | RM3100 | SPI, 75 μT range, IP65 | 1 | 32 |
| 20 | Barometer | MS5611-01BA03 | 0.012 mbar resolution | 1 | 12 |

### Sensing — Payload

| # | Component | Manufacturer / Model | Spec | Qty | Unit Cost (€) |
|---|-----------|---------------------|------|-----|---------------|
| 21 | RGB global-shutter cam | FLIR Blackfly S GigE | 20 MP, Sony IMX183, GigE, IP52 | 1 | 1150 |
| 22 | LWIR microbolometer | FLIR Lepton 3.5 module | 160×120, 8–14 µm, ±5 °C, 8.7 g | 1 | 245 |
| 23 | 2-axis gimbal | Gremsy Pixy WE | ±300° pan, ±140° tilt, brushless | 1 | 780 |
| 24 | Gimbal interface board | Gremsy COM-1 | UART/CAN control, vibration iso | 1 | 55 |
| 25 | Hardware time-sync board | SparkFun GPS-RTK-SMA | PPS signal router to all sensors | 1 | 65 |

### Communications

| # | Component | Manufacturer / Model | Spec | Qty | Unit Cost (€) |
|---|-----------|---------------------|------|-----|---------------|
| 26 | Data link radio | Doodle Labs Mesh Rider Mini | 900 MHz MIMO, AES256, 100 Mbps | 1 | 420 |
| 27 | RC safety link | FrSky R9 MM | 900 MHz, SBUS, 10 km | 1 | 35 |
| 28 | 4G/LTE modem | Sixfab Raspberry Pi 4G/LTE | CAT4, SIM slot, fallback link | 1 | 78 |
| 29 | Antenna (data) | TrueRC X-AIR 900 | 9 dBi RHCP omnidirectional | 2 | 45 |

### Power & Integration

| # | Component | Manufacturer / Model | Spec | Qty | Unit Cost (€) |
|---|-----------|---------------------|------|-----|---------------|
| 30 | Smart BEC 12V/5A | Matek UBEC DUO | 5V + 12V dual output, 97% eff | 1 | 18 |
| 31 | Smart BEC 5V/10A | Holybro Micro Power Module | Current + voltage sensing | 1 | 22 |
| 32 | IP54 enclosure (FCU) | Hammond 1594 series polycarbonate | Vibration-isolated tray, IP54 | 1 | 35 |
| 33 | IP54 enclosure (compute) | Bud Industries CN-6706 | Vented, EMI shielded | 1 | 42 |
| 34 | Cable harness (custom) | Molex Micro-Fit 3.0 | CAN, PWM, power looms | 1 set | 85 |

**UAV Subtotal (excl. spares): ~€6,480**

---

## CS2 — Ground Robot (UGV-G)

### Tracked Base

| # | Component | Manufacturer / Model | Spec | Qty | Unit Cost (€) |
|---|-----------|---------------------|------|-----|---------------|
| 35 | Tracked UGV chassis | SuperDroid Robots IG52-DB4 | 4WD differential, 60 kg payload | 1 | 3,200 |
| 36 | Drive motors | REV Robotics NEO brushless | 6000 RPM, 40 A, IP52 | 4 | 95 |
| 37 | Motor controllers | SPARK MAX (REV) | FOC, CAN bus, current limiting | 4 | 120 |
| 38 | Battery pack (UGV) | Battleborn LiFePO4 100Ah 24V | 24 V, 100 Ah, 2.4 kWh, IP67 | 2 | 890 |
| 39 | BMS (UGV) | Daly 24V 200A smart BMS | Cell protection, Bluetooth mon | 1 | 145 |
| 40 | DC-DC converter 24→12V | Vicor DCM 300W | 24→12 V, 300 W, ±1% regulation | 2 | 185 |
| 41 | DC-DC converter 24→5V | Vicor DCM 100W | 5 V logic rail, 100 W | 1 | 110 |
| 42 | E-stop module | Pilz PNOZ s5 safety relay | SIL 3, dual-channel, IP20 | 1 | 280 |
| 43 | Suspension bumper | AndyMark AM-Bumper | Foam-core polycarb impact rail | 4 | 35 |

### Navigation Sensors (UGV)

| # | Component | Manufacturer / Model | Spec | Qty | Unit Cost (€) |
|---|-----------|---------------------|------|-----|---------------|
| 44 | 3D LiDAR (SLAM) | RPLIDAR A3M1 (primary) / Ouster OS0-32 (upgrade) | 25 m, 32 ch, 10 Hz, IP54 | 1 | 1,200 |
| 45 | GNSS/RTK (UGV) | u-blox ZED-F9P | RTK ±1 cm, same base as UAV | 1 | 195 |
| 46 | IMU (UGV) | VectorNav VN-100 | 0.05° heading, IP67 | 1 | 640 |
| 47 | Wheel encoders | US Digital E8 1000 CPR | 1000 CPR, differential quadrature | 4 | 55 |
| 48 | Depth camera (obstacle) | Intel RealSense D455 | 86° FoV, 6 m range, IP52 | 2 | 285 |
| 49 | Mission computer (UGV) | NVIDIA Orin NX 16 GB | Same Orin NX as UAV for spares | 1 | 620 |

### Mobile Docking & Charging Subsystem

| # | Component | Manufacturer / Model | Spec | Qty | Unit Cost (€) |
|---|-----------|---------------------|------|-----|---------------|
| 50 | Landing pad structure | Custom 4mm CF plate 400×400mm | Laser-cut, anodised Al frame | 1 | 180 |
| 51 | AprilTag fiducial | 200×200mm printed, laminated | Tag36h11 family, UV-stable | 2 | 8 |
| 52 | Pogo-pin connector (charge) | Preci-dip 824 series 6-pin | 4×power + 2×data, 10 A/pin | 1 set | 95 |
| 53 | Inductive pad (backup) | Würth WE-WPCC 200W | 200 W, 87% eff, 15mm gap | 1 | 220 |
| 54 | Charging controller | Genasun GVB-8-Li 29.4V | 24V LiFePO4 MPPT, 15A | 1 | 165 |
| 55 | Mast (relay antenna) | Carbon 1m telescoping mast | Lightweight, 1 m deploy | 1 | 75 |
| 56 | Passive funnel guide | 3D-printed PETG cone | 200mm diameter → 50mm slot | 1 | 12 |

### 5-DoF Deployment Arm

| # | Component | Manufacturer / Model | Spec | Qty | Unit Cost (€) |
|---|-----------|---------------------|------|-----|---------------|
| 57 | Arm base + shoulder joint | Hebi Robotics X5-9 actuator | Integrated encoder + FOC, IP67 | 1 | 1,450 |
| 58 | Elbow + wrist joints | Hebi Robotics X5-4 (×3) | 12 Nm cont., IP67 | 3 | 980 |
| 59 | Wrist roll joint | Hebi Robotics X5-1 | 4 Nm, compact | 1 | 780 |
| 60 | Force-torque sensor (EE) | ATI Mini45 | 6-axis, ±145 N / ±10 Nm | 1 | 1,850 |
| 61 | Quick-change EE coupler | Schunk SWS 030 | Automatic locking, IP67 | 1 | 340 |

### NDE Crawler (Gc)

| # | Component | Manufacturer / Model | Spec | Qty | Unit Cost (€) |
|---|-----------|---------------------|------|-----|---------------|
| 62 | Crawler chassis (custom) | CNC Al 6061 + CF panels | 250×180×80 mm, 1.8 kg | 1 | 450 |
| 63 | Suction impeller | Sanyo Denki 9GA0812 | 12V DC, 1.2 Nm, 6500 RPM | 2 | 85 |
| 64 | Vacuum sealing skirt | Silicone shore A30 | Custom moulded, 4mm lip | 2 | 60 |
| 65 | Crawler drive modules | Maxon DCX 22 brushless | IP65, 25 W, encoder | 4 | 220 |
| 66 | UT phased array probe | Olympus 5L64-A2 | 64-element, 5 MHz, PEEK nose | 1 | 3,200 |
| 67 | UT pulser-receiver | Olympus OmniScan MX2 | Full matrix capture, 64:64 ch | 1 | 8,500 |
| 68 | Gel-fed roller coupling | Custom PTFE roller, gel pump | 100 mL tank, peristaltic pump | 1 | 280 |
| 69 | AE sensors | Physical Acoustics R15α | 150 kHz resonant, 22 mm, BNC | 2 | 310 |
| 70 | AE preamplifier | PAC 2/4/6-AST | 40 dB gain, 2-ch | 1 | 420 |
| 71 | Crawler compute | Raspberry Pi CM4 (8 GB) | eMMC 32 GB, no WiFi, isolated | 1 | 85 |
| 72 | Crawler comms (tether) | Ethernet over tether (10 m) | CAT6A, IP67 M12 connectors | 1 | 65 |

**UGV Subtotal (excl. spares): ~€29,800**

---

## CS3 — Shore / Edge Mission Server

| # | Component | Manufacturer / Model | Spec | Qty | Unit Cost (€) |
|---|-----------|---------------------|------|-----|---------------|
| 73 | Edge compute server | NVIDIA IGX Orin Dev Kit | 275 TOPS, 64 GB, PCIe 4.0 | 1 | 4,800 |
| 74 | NAS storage | Synology RS1221+ | 8-bay, 4×8TB IronWolf, RAID-6 | 1 | 2,200 |
| 75 | PoE managed switch | Cisco SG350-10P | 10-port, 62W PoE+, managed | 1 | 620 |
| 76 | 4G/5G router (site) | Robustel R2000-4L | Dual SIM, 5G NR, IP30, DIN rail | 1 | 780 |
| 77 | UPS | APC SMT1500RMI2U | 1500VA, 2U rack, Li-ion | 1 | 1,100 |
| 78 | MQTT broker appliance | HiveMQ Enterprise (software) | Clustered MQTT 5.0, TLS 1.3 | 1 lic | 1,200/yr |
| 79 | Satellite backup link | Starlink Maritime terminal | 100–300 Mbps, low latency | 1 | 3,500 |

**Server Subtotal: ~€14,200**

---

## Tools & Calibration Equipment

| # | Item | Spec | Cost (€) |
|---|------|------|----------|
| 80 | RTK base station | u-blox ANN-MB-00 + ZED-F9P | Fixed, sends NTRIP corrections | 650 |
| 81 | Calibration target board | 10×8 asymmetric circle grid, A2 | Extrinsic RGB/LWIR/LiDAR calib | 85 |
| 82 | Calibration phantom (UT) | Carbon/epoxy flat-bottom holes | ASTM reference block | 320 |
| 83 | Torque wrench set | Stahlwille 730N/10 | 2–10 Nm certified ±2% | 280 |
| 84 | Multimeter (insulation) | Fluke 1587 FC | 1 kV insulation resistance | 580 |

---

## Total System BOM Cost Summary

| Subsystem | Cost (€) |
|-----------|----------|
| UAV-A (×2 units) | 12,960 |
| UGV-G (×1 unit) | 29,800 |
| Shore/Edge Server | 14,200 |
| Tools & Calibration | 1,915 |
| Spares (15%) | 8,831 |
| **TOTAL** | **€67,706** |
