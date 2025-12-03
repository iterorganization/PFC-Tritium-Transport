import json
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
# matplotlib.use("TkAgg")  # Forces external interactive plots
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Load the JSON file
# file_path = "results_just_glow/wall_bin_5_sub_bin_high_wetted.json"  # Update the path if needed
# 
file_path = "../results_capability_test/div_bin_44.json"  # Update the path if needed
# file_path = "results_benchmark/div_bin_46.json"  # Update the path if needed
with open(file_path, "r") as file:
    data = json.load(file)

# Create two subplots (vertically stacked), sharing x-axis
fig, (ax_top, ax_bottom) = plt.subplots(2, 1, sharex=True, figsize=(5.5, 4.5), height_ratios=[3, 1])
plotly_fig = make_subplots(rows=2, cols=1, subplot_titles=("Hydrogen Inventory", "Surface Temperature"))

total_D = None
total_T = None

# Convert top-level time values from seconds to hours
shared_time_values = [time / 3600 for time in data["t"]]

# Loop through all keys except "t"
for key, values in data.items():
    if key == "t":
        continue

    if isinstance(values, dict) and "data" in values:
        data_values = np.array(values["data"])

        if key == "surface_temperature":
            ax_bottom.plot(shared_time_values, data_values, label="Surface temperature, K", color="tab:red")
            plotly_fig.add_trace(
                go.Scatter(x=shared_time_values, y=data_values, line=dict(width=2)),
                row=2, col=1
            )
        else:
            if total_T is None:
                total_D = np.zeros_like(data_values)
                total_T = np.zeros_like(data_values)

            if 'flux' not in key:
                if 'D' in key:
                    total_D += data_values
                if 'T' in key:
                    total_T += data_values
            else:
                # You don't have ax_middle anymore, so skip this or redirect it
                pass

            if key != "T" and 'D' not in key and 'flux' not in key:
                ax_top.plot(shared_time_values, data_values, label=f"{key}")
                plotly_fig.add_trace(
                    go.Scatter(x=shared_time_values, y=data_values, name=key, line=dict(width=2)),
                    row=1, col=1
                )

# Plot total_T if it was computed
if total_T is not None:
    ax_top.plot(shared_time_values, total_T, label="Total T", linestyle='-', linewidth=2, color='black')
    plotly_fig.add_trace(
        go.Scatter(x=shared_time_values, y=total_T, name="Total T", line=dict(width=2, color='black')),
        row=1, col=1
    )


# Optionally plot total_D too
# ax_top.plot(time_values, total_D, label="Total D", linestyle='--', linewidth=2, color='blue')

# --- Format top axis ---
ax_top.set_xscale("log")
# ax_top.set_yscale("log")  # Uncomment if needed
#ax_top.set_xlim(200, 400)
#ax_top.set_xlim(0.05, 200)
ax_top.set_xlim(left=0.05)
# ax_top.set_ylim(1e16, 1e23)  # Uncomment if needed
ax_top.set_ylabel("Tritium Value (atms/m^2)")
ax_top.legend(loc='upper left')
ax_top.grid(which="both", linestyle="--", linewidth=0.5)
ax_top.set_title("Tungsten high-wetted Wall bin 11")

# ax_middle.legend()

# --- Format bottom axis ---
ax_bottom.set_xlabel("Time (hours)")
# ax_bottom.set_ylabel("Surface Temp")
ax_bottom.legend()
ax_bottom.grid(which="both", linestyle="--", linewidth=0.5)

# plotly_fig.write_html("1_bin.html", auto_open=True)

plt.tight_layout()
plt.savefig("1_bin_2")
print('done')
# plt.show()

