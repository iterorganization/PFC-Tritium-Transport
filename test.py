import json
import pandas as pd
from make_iter_bins import FW_bins, Div_bins, my_reactor

from hisp.plamsa_data_handling import PlasmaDataHandling
from hisp.scenario import Scenario, Pulse
from hisp.model import Model

import dolfinx
# dolfinx.log.set_log_level(dolfinx.log.LogLevel.INFO)


# Make a scenario
fp = Pulse(
    pulse_type="FP",
    nb_pulses=3,
    ramp_up=429,
    steady_state=650,
    ramp_down=455,
    waiting=84866,
    tritium_fraction=0.5,
)
fp_d = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=429,
    steady_state=650,
    ramp_down=455,
    waiting=84866,
    tritium_fraction=0.0,
)
icwc = Pulse(
    pulse_type="ICWC",
    nb_pulses=1,
    ramp_up=10,
    steady_state=280,
    ramp_down=10,
    waiting=1500,
    tritium_fraction=0.0,
)
gdc = Pulse(
    pulse_type="GDC",
    nb_pulses=1,
    ramp_up=1,
    steady_state=86398,
    ramp_down=1,
    waiting=86400,
    tritium_fraction=0.0,
)
risp5 = Pulse(
    pulse_type="RISP",
    nb_pulses=5,
    ramp_up=10,
    steady_state=250,
    ramp_down=10,
    waiting=1530,
    tritium_fraction=0.0,
)
risp1 = Pulse(
    pulse_type="RISP",
    nb_pulses=1,
    ramp_up=10,
    steady_state=250,
    ramp_down=10,
    waiting=75330,
    tritium_fraction=0.0,
)
bake = Pulse(
    pulse_type="BAKE",
    nb_pulses=1,
    ramp_up=151200, # 5C degrees per hour; 42 hours total
    steady_state=345600,
    ramp_down=108000, # -7C per hour; 30 hours total
    waiting=11,  # HISP expects at least 10 s of waiting...
    tritium_fraction=0.0,
)

my_scenario = Scenario(pulses=[fp, fp_d, bake])

# Make a plasma data handling object
data_folder = "data"
plasma_data_handling = PlasmaDataHandling(
    pulse_type_to_data={
        "FP": pd.read_csv(data_folder + "/Binned_Flux_Data.dat", delimiter=","),
        "ICWC": pd.read_csv(data_folder + "/ICWC_data.dat", delimiter=","),
        "GDC": pd.read_csv(data_folder + "/GDC_data.dat", delimiter=","),
    },
    path_to_ROSP_data=data_folder + "/ROSP_data",
    path_to_RISP_data=data_folder + "/RISP_data",
    path_to_RISP_wall_data=data_folder + "/RISP_Wall_data.dat",
)

# Make a HISP model object
my_hisp_model = Model(
    reactor=my_reactor,
    scenario=my_scenario,
    plasma_data_handling=plasma_data_handling,
    coolant_temp=343.0,
)

if __name__ == "__main__":
    global_data = {}
    processed_data = []

    # first wall bins
    # for fw_bin in FW_bins.bins:
    #     global_data[fw_bin] = {}
    #     fw_bin_data = {"bin_index": fw_bin.index, "sub_bins": []}

    #     for sub_bin in fw_bin.sub_bins:
    #         my_model, quantities = my_hisp_model.run_bin(sub_bin)

    #         global_data[fw_bin][sub_bin] = quantities

    #         subbin_data = {
    #             key: {"t": value.t, "data": value.data}
    #             for key, value in quantities.items()
    #         }
    #         subbin_data["mode"] = sub_bin.mode
    #         subbin_data["parent_bin_index"] = sub_bin.parent_bin_index

    #         fw_bin_data["sub_bins"].append(subbin_data)

    #     processed_data.append(fw_bin_data)

    # divertor bins
    for div_bin in Div_bins.bins [4:5]: #[21:22]:
        print(f"Running bin div {div_bin.index+1}")
        my_model, quantities = my_hisp_model.run_bin(div_bin)

        bin_data = {
            key: {"t": value.t, "data": value.data} for key, value in quantities.items()
        }
        bin_data["bin_index"] = div_bin.index

        processed_data.append(bin_data)

    # write the processed data to JSON
    with open("processed_data.json", "w+") as f:
        json.dump(processed_data, f, indent=4)
