# Georegistered patch-level report published by UAV perception node
# Fields align with belief state b_t(p) = {c_hat, s_hat, Sigma, l_hat}

builtin_interfaces/Time stamp
string turbine_id          # e.g. "WTG-07"
uint8  blade_index         # 0=A, 1=B, 2=C
float32 chord_pos          # normalised chordwise position [0,1]
float32 span_pos           # normalised spanwise position [0,1]

# Georeference in blade frame (from eq. 18 in report)
geometry_msgs/Point position_blade_frame

# Perception outputs
uint8   defect_class       # 0=clean,1=LEerosion,2=crack,3=delamination,4=lightning
float32 severity           # s in [0,1]
float32 severity_aleatoric # sigma^2_aleatoric from deep ensemble
float32 severity_epistemic # sigma^2_epistemic from deep ensemble  <- u
float32 calibration_ece    # running ECE at time of report

# Modality flags
bool rgb_valid
bool lwir_valid
bool lidar_valid

# Image patches (compressed)
sensor_msgs/CompressedImage rgb_patch
sensor_msgs/CompressedImage lwir_patch
