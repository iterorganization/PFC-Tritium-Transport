from scenario import Scenario, Pulse
import pandas as pd

# Reference FP pulse from capability_test.py
# ramp_up: 429s, steady_state: 650s, ramp_down: 455s, waiting: 3600s
REF_STEADY_STATE = 650
REF_RAMP_UP = 429
REF_RAMP_DOWN = 455
REF_WAITING = 3600

# Reference baking pulse
bake = Pulse(
    pulse_type="BAKE",
    nb_pulses=1,
    ramp_up=151200,    # 5C degrees per hour; 42 hours total
    steady_state=345600,
    ramp_down=108000,   # -7C per hour; 30 hours total
    waiting=11,         # HISP expects at least 10 s of waiting...
    tritium_fraction=0.0,
)

# Read the CSV file
csv_path = "/home/ITER/llealsa/Desktop/PFC-TT-INPUT Evaluations_for_guidelines_for_neutron_p_CV36ST_v1_2.csv"
df = pd.read_csv(csv_path)

# Clean and prepare data
df.columns = df.columns.str.strip()
df = df.dropna(subset=['FPO'])  # Remove empty rows

# Create pulses grouped by FPO
pulses = []
current_fpo = None

for idx, row in df.iterrows():
    fpo = int(row['FPO'])
    steady_state = int(row['Total duration'])
    
    # Scale the timing proportionally based on steady_state
    scale_factor = steady_state / REF_STEADY_STATE
    ramp_up = int(REF_RAMP_UP * scale_factor)
    ramp_down = int(REF_RAMP_DOWN * scale_factor)
    waiting = int(REF_WAITING * scale_factor)
    
    # Add baking after each FPO phase (before starting the next FPO)
    if current_fpo is not None and fpo != current_fpo:
        pulses.append(bake)
    
    # Create the pulse
    pulse = Pulse(
        pulse_type="FP",
        nb_pulses=1,
        ramp_up=ramp_up,
        steady_state=steady_state,
        ramp_down=ramp_down,
        waiting=waiting,
        tritium_fraction=float(row['Tritium content']),
        heat_scaling=float(row['Power scaling factor']),
        flux_scaling=float(row['Flux scaling factor']),
    )
    
    pulses.append(pulse)
    current_fpo = fpo

# Add final baking after FPO 5
pulses.append(bake)

# Create the scenario
scenario = Scenario(pulses=pulses)
