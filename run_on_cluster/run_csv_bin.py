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

# Import CSV bin system
from csv_bin_loader import CSVBinLoader
from csv_bin import CSVReactor
from run_bin_functions import load_scenario_variable

# Load command-line arguments
bin_id = int(sys.argv[1])  # CSV bin ID (row index in input table)
scenario_folder = sys.argv[2]
scenario_name = sys.argv[3]
csv_file_path = sys.argv[4] if len(sys.argv) > 4 else "input_table.csv"

# Uncomment for testing
# bin_id = 0  # First bin (row index 0)
# scenario_folder = "iter_scenarios"
# scenario_name = "testcase"
# csv_file_path = "input_table.csv"

print(f"Loading scenario: {scenario_name} from {scenario_folder}")
scenario = load_scenario_variable(scenario_folder, scenario_name)

print(f"Loading CSV bins from: {csv_file_path}")
# Load CSV reactor
csv_reactor = CSVReactor.from_csv(csv_file_path)

print(f"Loaded {len(csv_reactor)} bins from CSV")
print(csv_reactor.get_reactor_summary())

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

def run_csv_bin_scenario(scenario: Scenario, bin_id: int):
    """Run scenario for a specific CSV bin ID (row index in input table)."""
    
    # Make a HISP model object with CSV reactor
    my_hisp_model = Model(
        reactor=csv_reactor,
        scenario=scenario,
        plasma_data_handling=plasma_data_handling,
        coolant_temp=343.0,
    )

    # Find the specific bin by bin_id
    try:
        target_bin = csv_reactor.get_bin_by_id(bin_id)
        print(f"Found target bin: {target_bin}")
    except ValueError as e:
        print(f"Error: {e}")
        print(f"Available bin IDs: {[bin.bin_id for bin in csv_reactor.bins]}")
        return

    try:
        print(f"Running CSV bin ID {bin_id} (bin_number={target_bin.bin_number}, {target_bin.material}, {target_bin.mode}, {target_bin.location})")
        
        # Run the bin
        model, quantities = my_hisp_model.run_bin(target_bin)

        # Get temperature function
        temperature_function = make_temperature_function(
            scenario=scenario,
            plasma_data_handling=plasma_data_handling,
            bin=target_bin,
            coolant_temp=343.0,
        )
        
        # Format the data (same as original script)
        t_sampled = next(iter(quantities.values())).t[::1]
        csv_bin_data = {
            key: {"data": value.data[::1]}
            for key, value in quantities.items()
        }
        csv_bin_data["t"] = t_sampled
        
        # Add CSV bin specific information
        csv_bin_data["bin_id"] = target_bin.bin_id
        csv_bin_data["bin_number"] = target_bin.bin_number
        csv_bin_data["mode"] = target_bin.mode
        csv_bin_data["material"] = target_bin.material
        csv_bin_data["location"] = target_bin.location
        csv_bin_data["thickness"] = target_bin.thickness
        csv_bin_data["cu_thickness"] = target_bin.cu_thickness
        csv_bin_data["ion_scaling_factor"] = target_bin.ion_scaling_factor
        csv_bin_data["surface_area"] = target_bin.surface_area
        csv_bin_data["parent_bin_surf_area"] = target_bin.parent_bin_surf_area
        
        # Add bin configuration parameters
        bin_config = target_bin.bin_configuration
        csv_bin_data["bin_configuration"] = {
            "rtol": bin_config.rtol,
            "atol": bin_config.atol,
            "fp_max_stepsize": bin_config.fp_max_stepsize,
            "max_stepsize_no_fp": bin_config.max_stepsize_no_fp,
            "bc_plasma_facing_surface": bin_config.bc_plasma_facing_surface,
            "bc_rear_surface": bin_config.bc_rear_surface,
        }

        # Calculate temperature at x=0 (surface)
        x_eval = np.array([[0.0]])  # x = 0
        temperature_values = [float(temperature_function(x_eval, float(t))[0]) for t in t_sampled]
        csv_bin_data["temperature_at_x0"] = temperature_values

        # Save results to JSON
        output_file = f"results_{scenario_name}/csv_bin_id_{bin_id}_num_{target_bin.bin_number}_{target_bin.material}_{target_bin.mode}.json"
        
        os.makedirs("results_"+str(scenario_name), exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(csv_bin_data, f, indent=4)

        print(f"Completed CSV bin ID {bin_id} (bin_number={target_bin.bin_number}, {target_bin.material}, {target_bin.mode})")
        print(f"Results saved to: {output_file}")
        
        print(f"Bin Configuration:")
        print(f"  - Material: {target_bin.material}")
        print(f"  - Thickness: {target_bin.thickness*1000:.1f} mm")
        print(f"  - Cu thickness: {target_bin.cu_thickness*1000:.1f} mm")
        print(f"  - Mode: {target_bin.mode}")
        print(f"  - Location: {target_bin.location}")
        print(f"  - Ion scaling factor: {target_bin.ion_scaling_factor:.3f}")
        print(f"  - BC plasma facing: {bin_config.bc_plasma_facing_surface}")
        print(f"  - BC rear surface: {bin_config.bc_rear_surface}")
        print(f"  - Tolerances: rtol={bin_config.rtol:.0e}, atol={bin_config.atol:.0e}")
        print(f"  - Max stepsize FP: {bin_config.fp_max_stepsize:.1f} s")
        print(f"  - Max stepsize no FP: {bin_config.max_stepsize_no_fp:.1f} s")

    except Exception as e:
        print(f"Failed to process CSV bin ID {bin_id}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_csv_bin_scenario(scenario, bin_id)
