from scenario import Scenario, Pulse
import pandas as pd
from plasma_data_handling import PlasmaDataHandling

data_folder = "data"
plasma_data_handling = PlasmaDataHandling(
    pulse_type_to_data={
        "FP": pd.read_csv(data_folder + "/Binned_Flux_Example.dat", delimiter=","),
        "FP_D": pd.read_csv(data_folder + "/Binned_Flux_Data_just_D_pulse.dat", delimiter=",", comment='#'),
        "ICWC": pd.read_csv(data_folder + "/ICWC_data.dat", delimiter=","),
        "GDC": pd.read_csv(data_folder + "/GDC_data.dat", delimiter=","),
    },
    path_to_RISP_data=data_folder + "/RISP_data",
    path_to_ROSP_data=data_folder + "/ROSP_data",
    path_to_RISP_wall_data=data_folder + "/RISP_Wall_data.dat",
)

# Reference baking pulse
bake = Pulse(
    pulse_type="BAKE",
    nb_pulses=1,
    ramp_up=151200,    # 5C degrees per hour; 42 hours total
    steady_state=345600,
    ramp_down=108000,   # -7C per hour; 30 hours total
    waiting=11,
    tritium_fraction=0.0,
)

# Example pulse 1
example1 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=1000,
    steady_state=2000,
    ramp_down=1000,
    waiting=2000,
    tritium_fraction=0.2,
    heat_scaling=0.33,
    flux_scaling=0.25,
)

# Example pulse 2
example2 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=1000,
    steady_state=2000,
    ramp_down=1000,
    waiting=2000,
    tritium_fraction=0.4,
    heat_scaling=0.5,
    flux_scaling=0.4,
)



# Build scenario with baking after each FPO phase
scenario = Scenario(pulses=[
    example1,
    example2,
    bake,
])

scenario.plasma_data_handling = plasma_data_handling