# Remaining Useful Life estimate per blade patch (Paris-Erdogan, Eq. 35-36)

builtin_interfaces/Time stamp
string turbine_id
uint8  blade_index
float32 chord_pos
float32 span_pos

float64 crack_length_m         # a_0 current estimate [m]
float64 crack_length_std_m     # uncertainty on a_0
float64 crack_critical_m       # a_c [m]
float64 rul_cycles             # N_RUL [load cycles]
float64 rul_days               # N_RUL converted to calendar days
float64 rul_confidence_lower   # 5th percentile
float64 rul_confidence_upper   # 95th percentile

string maintenance_recommendation  # "monitor" | "inspect" | "repair" | "urgent"
