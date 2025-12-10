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

from iter_bins.make_iter_bins import Div_bins, my_reactor
from run_bin_functions import load_scenario_variable

# Load command-line arguments
# bin_index = int(sys.argv[1])
# scenario_folder = sys.argv[2]
# scenario_name = sys.argv[3]
bin_index = int(sys.argv[1])
scenario_folder = sys.argv[2]
scenario_name = sys.argv[3]

scenario = load_scenario_variable(scenario_folder, scenario_name)

# Make a plasma data handling object
data_folder = "data"
plasma_data_handling = PlasmaDataHandling(
    pulse_type_to_data={
        "FP_D": pd.read_csv(data_folder + "/Binned_Flux_Data_just_D_pulse.dat", delimiter=","),
        "FP": pd.read_csv(data_folder + "/Binned_Flux_Data.dat", delimiter=","),
        "ICWC": pd.read_csv(data_folder + "/ICWC_data.dat", delimiter=","),
        "GDC": pd.read_csv(data_folder + "/GDC_data.dat", delimiter=","),
    },
    path_to_ROSP_data=data_folder + "/ROSP_data",
    path_to_RISP_data=data_folder + "/RISP_data",
    path_to_RISP_wall_data=data_folder + "/RISP_Wall_data.dat",
)

def run_scenario_div(scenario: Scenario):

    # Make a HISP model object
    my_hisp_model = Model(
        reactor=my_reactor,
        scenario=scenario,
        plasma_data_handling=plasma_data_handling,
        coolant_temp=343.0,
        BC_type="Old",
    )

    # # Save job data to a JSON file
    # job_json_file = f"job_data/div_bin_{div_bin.index}.json"
    # job_data = {"bin_index": div_bin.index}

    # with open(job_json_file, "w") as f:
    #     json.dump(job_data, f)

    for div_bin in Div_bins.bins:
        # print(f"Bin index {div_bin.index}, looking for {bin_index}")
        if div_bin.index == bin_index:
        # print("Bin found")
            # if div_bin.material == "B":
            try:
                print(f"Running divertor bin {div_bin.index}")
                _, quantities = my_hisp_model.run_bin(div_bin)

                temperature_function = make_temperature_function(
                        scenario=scenario,
                        plasma_data_handling=plasma_data_handling,
                        bin=div_bin,
                        coolant_temp=343.0,
                        )

                # Format the data
                t_sampled = next(iter(quantities.values())).t[::1]
                div_bin_data = {
                    key: {"data": value.data[::1]}
                    for key, value in quantities.items()
                }
                div_bin_data["t"] = t_sampled
                div_bin_data["bin_index"] = div_bin.index

                x_eval = np.array([[0.0]])  # x = 0
                temperature_values = [float(temperature_function(x_eval, float(t))[0]) for t in t_sampled]
                div_bin_data["temperature_at_x0"] = temperature_values

                # Save results to JSON
                output_file = f"results_{scenario_name}/div_bin_{div_bin.index}.json"
                os.makedirs("results_"+str(scenario_name), exist_ok=True)
                with open(output_file, "w") as f:
                    json.dump(div_bin_data, f, indent=4)

                print(f"Completed divertor bin {div_bin.index}")

            except Exception as e:
                print(f"Failed to process divertor bin {div_bin.index}: {e}")


run_scenario_div(scenario)
