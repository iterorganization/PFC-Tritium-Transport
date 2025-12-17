import os
import importlib.util

# def find_sub_bin(bin_index, sub_bin_mode, FW_bins):
#     """Find the sub_bin based on bin_index and sub_bin_mode."""
#     for fw_bin in FW_bins.bins:
#         if fw_bin.index == bin_index:
#             for sub_bin in fw_bin.sub_bins:
#                 if sub_bin.mode == sub_bin_mode:
#                     return fw_bin, sub_bin
                
def load_scenario_variable(scenario_folder, scenario_name, variable_name="scenario"):
    """
    Dynamically loads a Python script and retrieves a variable from it.

    Parameters:
    - scenario_folder (str): The main folder (e.g., 'iter_scenarios')
    - scenario_name (str): The Python file (without .py extension) inside the folder
    - variable_name (str): The name of the variable to retrieve (default: 'scenario')

    Returns:
    - The value of the variable if found, else None
    """

    script_path = os.path.join(scenario_folder, f"{scenario_name}.py")

    if not os.path.exists(script_path):
        print(f"❌ Error: Script '{script_path}' not found.")
        return None

    try:
        # Load the module from the script file
        spec = importlib.util.spec_from_file_location(scenario_name, script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check if the variable exists in the module
        if hasattr(module, variable_name):
            scenario_variable = getattr(module, variable_name)
            print(f"✅ Successfully loaded '{variable_name}' from '{script_path}'.")
            return scenario_variable
        else:
            print(f"⚠️ Variable '{variable_name}' not found in '{script_path}'.")
            return None

    except Exception as e:
        print(f"❌ Error loading script '{script_path}': {e}")
        return None