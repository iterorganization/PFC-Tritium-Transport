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

# FPO 1, Pulse 1
fpo1_p1 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=60060,
    steady_state=91000,
    ramp_down=63700,
    waiting=504000,
    tritium_fraction=0.00,
    heat_scaling=0.33,
    flux_scaling=0.25,
)

# FPO 1, Pulse 2
fpo1_p2 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=60060,
    steady_state=91000,
    ramp_down=63700,
    waiting=504000,
    tritium_fraction=0.00,
    heat_scaling=0.67,
    flux_scaling=0.50,
)

# FPO 1, Pulse 3
fpo1_p3 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=11583,
    steady_state=17550,
    ramp_down=12285,
    waiting=97200,
    tritium_fraction=0.50,
    heat_scaling=0.33,
    flux_scaling=0.50,
)

# FPO 1, Pulse 4
fpo1_p4 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=4719,
    steady_state=7150,
    ramp_down=5005,
    waiting=39600,
    tritium_fraction=0.01,
    heat_scaling=0.17,
    flux_scaling=0.25,
)

# FPO 1, Pulse 5
fpo1_p5 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=5148,
    steady_state=7800,
    ramp_down=5460,
    waiting=43200,
    tritium_fraction=0.01,
    heat_scaling=0.34,
    flux_scaling=0.50,
)

# FPO 1, Pulse 6
fpo1_p6 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=5148,
    steady_state=7800,
    ramp_down=5460,
    waiting=43200,
    tritium_fraction=0.01,
    heat_scaling=0.20,
    flux_scaling=0.25,
)

# FPO 1, Pulse 7
fpo1_p7 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=10296,
    steady_state=15600,
    ramp_down=10920,
    waiting=86400,
    tritium_fraction=0.01,
    heat_scaling=0.40,
    flux_scaling=0.33,
)

# FPO 1, Pulse 8
fpo1_p8 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=21021,
    steady_state=31850,
    ramp_down=22295,
    waiting=176400,
    tritium_fraction=0.01,
    heat_scaling=0.60,
    flux_scaling=0.50,
)

# Build scenario with baking after each FPO phase
scenario = Scenario(pulses=[
    # FPO 1
    fpo1_p1,
    fpo1_p2,
    fpo1_p3,
    fpo1_p4,
    fpo1_p5,
    fpo1_p6,
    fpo1_p7,
    fpo1_p8,
    bake, # Baking after FPO 1
])

scenario.plasma_data_handling = plasma_data_handling