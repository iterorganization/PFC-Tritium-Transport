import json
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use("TkAgg")  # Forces external interactive plots

# Load the JSON file
# file_path = "results_do_nothing/div_bin_61.json"  # first pulse did not solve
# file_path = "results_do_nothing/div_bin_59.json"  # fully ok SHOW
# file_path = "results_do_nothing/div_bin_60.json"  # 
# file_path = "results_do_nothing/div_bin_47.json"  # fully ok SHOW
# file_path = "results_do_nothing/div_bin_37.json"  # baking did not solve
# file_path = "results_do_nothing/div_bin_53.json"  # fully ok SHOW

# file_path = "results_do_nothing/div_bin_18.json"  # Update the path if needed
# file_path = "results_do_nothing/div_bin_30.json"  # Update the path if needed
# file_path = "results_do_nothing/div_bin_40.json"  # Update the path if needed
# file_path = "results_do_nothing/wall_bin_8_sub_bin_high_wetted.json"  # Update the path if needed
# file_path = "results_do_nothing/wall_bin_8_sub_bin_low_wetted.json"  # same temperature as high wetted?
# # file_path = "results_do_nothing/wall_bin_8_sub_bin_shadowed.json"  # same temperature as high wetted?
# file_path = "results_do_nothing/wall_bin_4_sub_bin_high_wetted.json"  # Update the path if needed
# file_path = "results_do_nothing/wall_bin_4_sub_bin_low_wetted.json"  # same temperature as high wetted?
# file_path = "results_do_nothing/wall_bin_4_sub_bin_shadowed.json"  # same temperature as high wetted?
# file_path = "results_do_nothing/wall_bin_14_sub_bin_dfw.json"  # loading wrong
# file_path = "results_do_nothing/wall_bin_14_sub_bin_wetted.json"  # ok
# file_path = "results_do_nothing/wall_bin_14_sub_bin_shadowed.json"  # wrong?
# file_path = "results_do_nothing/wall_bin_10_sub_bin_shadowed.json"  # bake wrong?
# file_path = "results_do_nothing/wall_bin_4_sub_bin_high_wetted.json"  # ok
# file_path = "results_do_nothing/wall_bin_4_sub_bin_low_wetted.json"  # ok

# selected for PFMC
# file_path = "results_do_nothing/div_bin_59.json"  # fully ok SHOW
# file_path = "results_do_nothing/div_bin_47.json"  # fully ok SHOW
# file_path = "results_do_nothing/div_bin_53.json"  # fully ok SHOW
# file_path = "results_do_nothing/wall_bin_4_sub_bin_shadowed.json"  # ok SHOW

# file_path = "results_do_nothing/div_bin_61.json"  # OK

# file_path = "results_capability_test/div_bin_18.json"  # Update the path if needed
# file_path = "results_capability_test/div_bin_61.json"  # Update the path if needed
with open(file_path, "r") as file:
    data = json.load(file)

# Loop through all keys in the dictionary and plot them
# Create two subplots (vertically stacked), sharing x-axis
# fig, (ax_top, ax_middle, ax_bottom) = plt.subplots(3, 1, sharex=True, figsize=(5.5, 5.5), height_ratios=[3, 1, 1])
fig, (ax_top, ax_bottom) = plt.subplots(2, 1, sharex=True, figsize=(5.5, 4.5), height_ratios=[3, 1])

time_values = None
total_D = None
total_T = None

for key, values in data.items():
    if isinstance(values, dict) and "t" in values and "data" in values:
        time_values = [time / 3600 for time in values["t"]]  # Convert seconds to hours
        data_values = np.array(values["data"])

        if key == "surface_temperature":
            ax_bottom.plot(time_values, data_values, label="Surface temperature, K", color="tab:red")
        else:
            if total_T is None:
                total_D = np.zeros_like(data_values)
                total_T = np.zeros_like(data_values)

            if 'flux' not in key:
                if 'D' in key:
                    total_D += data_values
                if 'T' in key:
                    total_T += data_values
            # else:
            #     ax_middle.plot(time_values, data_values, label=f"{key}")

            if key != "T" and 'D' not in key and 'flux' not in key:
                ax_top.plot(time_values, data_values, label=f"{key}")

# Plot totals after loop
if total_T is not None:
    ax_top.plot(time_values, total_T, label="Total T", linestyle='-', linewidth=2, color='black')
# Optionally plot total_D too
# ax_top.plot(time_values, total_D, label="Total D", linestyle='--', linewidth=2, color='blue')

# --- Format top axis ---
ax_top.set_xscale("log")
# ax_top.set_yscale("log")  # Uncomment if needed
# ax_top.set_xlim(0.05, 15)
ax_top.set_xlim(0.05, 200)
# ax_top.set_ylim(1e16, 1e23)  # Uncomment if needed
# ax_top.set_ylabel("Data Value (log scale)")
ax_top.legend(loc='upper left')
ax_top.grid(which="both", linestyle="--", linewidth=0.5)

# ax_middle.legend()

# --- Format bottom axis ---
ax_bottom.set_xlabel("Time (hours)")
# ax_bottom.set_ylabel("Surface Temp")
ax_bottom.legend()
ax_bottom.grid(which="both", linestyle="--", linewidth=0.5)

plt.tight_layout()
plt.show()

