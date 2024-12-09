import json
import pandas as pd

from hisp.plamsa_data_handling import PlasmaDataHandling

from make_iter_bins import FW_bins, Div_bins, my_reactor

from hisp.model import Model
from hisp.scenario import Scenario

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


def run_scenario(scenario: Scenario, results_file: str):

    # Make a HISP model object
    my_hisp_model = Model(
        reactor=my_reactor,
        scenario=scenario,
        plasma_data_handling=plasma_data_handling,
        coolant_temp=343.0,
    )

    global_data = {}
    processed_data = []

    # first wall bins
    for fw_bin in FW_bins.bins:
        global_data[fw_bin] = {}
        fw_bin_data = {"bin_index": fw_bin.index, "sub_bins": []}

        for sub_bin in fw_bin.sub_bins:
            _, quantities = my_hisp_model.run_bin(sub_bin)

            global_data[fw_bin][sub_bin] = quantities

            subbin_data = {
                key: {"t": value.t, "data": value.data}
                for key, value in quantities.items()
            }
            subbin_data["mode"] = sub_bin.mode
            subbin_data["parent_bin_index"] = sub_bin.parent_bin_index

            fw_bin_data["sub_bins"].append(subbin_data)

        processed_data.append(fw_bin_data)

        # write the processed data to JSON
        with open(results_file, "w+") as f:
            json.dump(processed_data, f, indent=4)

    # divertor bins
    for div_bin in Div_bins.bins:
        _, quantities = my_hisp_model.run_bin(div_bin)

        global_data[div_bin] = quantities

        bin_data = {
            key: {"t": value.t, "data": value.data} for key, value in quantities.items()
        }
        bin_data["bin_index"] = div_bin.index

        processed_data.append(bin_data)
        # write the processed data to JSON
        with open(results_file, "w+") as f:
            json.dump(processed_data, f, indent=4)


if __name__ == "__main__":

    from iter_scenarios.benchmark import scenario as scenario_benchmark
    from iter_scenarios.clean_every_2_days import (
        scenario as scenario_clean_every_2_days,
    )
    from iter_scenarios.clean_every_5_days import (
        scenario as scenario_clean_every_5_days,
    )
    from iter_scenarios.do_nothing import scenario as scenario_do_nothing
    from iter_scenarios.no_glow import scenario as scenario_no_glow

    for scenario, name in [
        (scenario_benchmark, "benchmark"),
        (scenario_clean_every_2_days, "clean_every_2_days"),
        (scenario_clean_every_5_days, "clean_every_5_days"),
        (scenario_do_nothing, "do_nothing"),
        (scenario_no_glow, "no_glow"),
    ]:
        print(f"Running scenario: {name}")
        run_scenario(scenario, f"results_{name}.json")
