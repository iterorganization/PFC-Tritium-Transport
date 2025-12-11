import os
import sys
import json
import pandas as pd
import numpy as np

from hisp.plamsa_data_handling import PlasmaDataHandling
from hisp.model import Model
from hisp.scenario import Scenario
from hisp.festim_models import make_temperature_function

# Get the parent directory of the current script
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Add the parent directory to sys.path
sys.path.insert(0, parent_dir)

from iter_bins.make_iter_bins import FW_bins, my_reactor
from run_bin_functions import load_scenario_variable

# Load command-line arguments
bin_index = int(sys.argv[1])
sub_bin_mode = sys.argv[2]
scenario_folder = sys.argv[3]
scenario_name = sys.argv[4]
# bin_index = 0 #int(sys.argv[1])
# sub_bin_mode = "shadowed" #sys.argv[2]
# scenario_folder = "iter_scenarios" # sys.argv[3]
# scenario_name = "testcase" #sys.argv[4]

scenario = load_scenario_variable(scenario_folder, scenario_name)

# Make a plasma data handling object
data_folder = "data"
plasma_data_handling = PlasmaDataHandling(
    pulse_type_to_data={
        "FP": pd.read_csv(data_folder + "/Binned_Flux_Data.dat", delimiter=","),
        "FP_D": pd.read_csv(data_folder + "/Binned_Flux_Data_just_D_pulse.dat", delimiter=","),
        "ICWC": pd.read_csv(data_folder + "/ICWC_data.dat", delimiter=","),
        "GDC": pd.read_csv(data_folder + "/GDC_data.dat", delimiter=","),
    },
    path_to_ROSP_data=data_folder + "/ROSP_data",
    path_to_RISP_data=data_folder + "/RISP_data",
    path_to_RISP_wall_data=data_folder + "/RISP_Wall_data.dat",
)

def run_scenario_wall(scenario: Scenario):

    # Make a HISP model object
    my_hisp_model = Model(
        reactor=my_reactor,
        scenario=scenario,
        plasma_data_handling=plasma_data_handling,
        coolant_temp=343.0,
        BC_type="Old",
    )

    # # Load the corresponding job data
    # job_file = f"job_data/wall_bin_{bin_index}_sub_bin_{sub_bin_mode}.json"
    # with open(job_file, "r") as f:
    #     job_data = json.load(f)

    # Run the wall bin process
    for fw_bin in FW_bins.bins:
        # print(f"Bin index {fw_bin.index}, looking for {bin_index}")
        if fw_bin.index == bin_index:
            # print("Bin found")
            for sub_bin in fw_bin.sub_bins:
                if sub_bin.material == "SS":
                    continue
                if sub_bin.mode == sub_bin_mode:
                # print("Sub bin found")
                    try:
                        print(f"Running wall bin {bin_index}, {sub_bin.mode}")
                        _, quantities = my_hisp_model.run_bin(sub_bin)

                        temperature_function = make_temperature_function(
                        scenario=scenario,
                        plasma_data_handling=plasma_data_handling,
                        bin=sub_bin,
                        coolant_temp=343.0,
                        )
                        # Format the data
                        t_sampled = next(iter(quantities.values())).t[::1]
                        wall_subbin_data = {
                            key: {"data": value.data[::1]}
                            for key, value in quantities.items()
                        }
                        wall_subbin_data["t"] = t_sampled
                        wall_subbin_data["mode"] = sub_bin.mode
                        wall_subbin_data["parent_bin_index"] = sub_bin.parent_bin_index

                        x_eval = np.array([[0.0]])  # x = 0
                        temperature_values = [float(temperature_function(x_eval, float(t))[0]) for t in t_sampled]
                        wall_subbin_data["temperature_at_x0"] = temperature_values


                        # Save results to JSON
                        # TODO make subdirectories for different scenarios
                        output_file = f"results_{scenario_name}/wall_bin_{bin_index}_sub_bin_{sub_bin.mode}.json"

                        os.makedirs("results_"+str(scenario_name), exist_ok=True)
                        with open(output_file, "w") as f:
                            json.dump(wall_subbin_data, f, indent=4)

                        print(f"Completed wall bin {bin_index}, {sub_bin.mode}")

                    except Exception as e:
                        print(f"Failed to process wall bin {bin_index}, {sub_bin.mode}: {e}")

run_scenario_wall(scenario)
