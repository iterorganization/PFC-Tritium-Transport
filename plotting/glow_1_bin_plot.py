import json
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from make_iter_bins import Div_bins, total_fw_bins, FW_bins
import matplotlib.patches as patches
# matplotlib.use("TkAgg")  # Forces external interactive plots
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from matplotlib.ticker import ScalarFormatter

# Load the JSON file
# file_path = "results_just_glow/wall_bin_5_sub_bin_high_wetted.json"  # Update the path if needed
# 
# file_path = "div_bin_50.json"  # Update the path if needed
file_path = "results_do_nothing/div_bin_50.json"  # Update the path if needed
bin_idx = 50
with open(file_path, "r") as file:
    data = json.load(file)

# Loop through all keys in the dictionary and plot them
# Create two subplots (vertically stacked), sharing x-axis
# fig, (ax_top, ax_middle, ax_bottom) = plt.subplots(3, 1, sharex=True, figsize=(5.5, 5.5), height_ratios=[3, 1, 1])
fig, (ax_top, ax_bottom) = plt.subplots(2, 1, sharex=True, figsize=(5.5, 4.5), height_ratios=[3, 1])
# plotly_fig = make_subplots(rows=2,cols=1,subplot_titles=("Hydrogen Inventory","Surface Temperature"))

time_values = None
total_D = None
total_T = None

bin_length = Div_bins.get_bin(bin_idx).length

for key, values in data.items():
    if isinstance(values, dict) and "t" in values and "data" in values:
        time_values = [time / 3600 for time in values["t"]]  # Convert seconds to hours
        data_values = np.array(values["data"])

        if key == "surface_temperature":
            ax_bottom.plot(time_values, data_values, label="Surface temperature, K", color="tab:red")
            # plotly_fig.add_trace(go.Scatter(x=time_values,y=data_values,line=dict(width=2)),row=2,col=1)
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
                # ax_middle.plot(time_values, data_values, label=f"{key}")

            if key != "T" and 'D' not in key and 'flux' not in key:
                ax_top.plot(time_values, data_values, label=f"{key}")
                # plotly_fig.add_trace(go.Scatter(x=time_values,y=data_values,name=key,line=dict(width=2)),row=1,col=1)

# Plot totals after loop
if total_T is not None:
    ax_top.plot(time_values, total_T, label="Total T", linewidth=2, color='black')
    # plotly_fig.add_trace(go.Scatter(x=time_values,y=total_T,name="Total T",line=dict(width=2)),row=1,col=1)

# Optionally plot total_D too
# ax_top.plot(time_values, total_D, label="Total D", linewidth=2, color='green')

# --- Format top axis ---
ax_top.set_xscale("log")
# ax_top.set_yscale("log")  # Uncomment if needed
# ax_top.set_xlim(0.05, 15)
ax_top.set_xlim(0.05, 200)
# ax_top.set_ylim(1e16, 1e23)  # Uncomment if needed
ax_top.set_ylabel("Inventory (T/m^2)", fontsize=12)
# ax_top.legend(loc='upper left')
ax_top.grid(which="both", linestyle="--", linewidth=0.5)
# ax_top.set_title("Boron Divertor Bin 20")

# ax_middle.legend()

# --- Format bottom axis ---
ax_bottom.set_xlabel("Time (hours)", fontsize=12)
ax_bottom.set_ylabel("Surface Temp (K)", fontsize=12)
# ax_bottom.set_ylabel("Surface Temp")
# ax_bottom.legend()
ax_bottom.grid(which="both", linestyle="--", linewidth=0.5)

# for cleaning pulse delination 
# pulse_start = 5134*2/3600
# ramp_up_rect = plt.Rectangle(
#     (pulse_start, -1e20),
#     429/3600,
#     8e22,
#     facecolor='indigo',
#     alpha=0.5
# )
# ramp_up_rect_b = plt.Rectangle(
#     (pulse_start, 0),
#     429/3600,
#     800,
#     facecolor='indigo',
#     alpha=0.5
# )
bake_start = 51340/60/60
bake_rect = plt.Rectangle(
    (bake_start,-1e20),
    656151/3600,
    8e22,
    facecolor="grey",
    alpha=0.5,
)
ax_top.add_patch(bake_rect)
bake_rect_b = plt.Rectangle(
    (bake_start,0),
    656151/3600,
    800,
    facecolor="grey",
    alpha=0.5,
)
# glow_rect = plt.Rectangle(
#     (51340/3600,-1e22),
#     86400*2/3600,
#     8e22,
#     facecolor="cadetblue",
#     alpha=0.5,
# )
# glow_rect_b = plt.Rectangle(
#     (51340/3600,0),
#     86400*2/3600,
#     800,
#     facecolor="cadetblue",
#     alpha=0.5,
# )
# wait_rect = plt.Rectangle(
#     ((51340+86400)/3600,-1e22),
#     86400/3600,
#     7.5e22,
#     facecolor="olive",
#     alpha=0.5,
# )
# wait_rect_b = plt.Rectangle(
#     ((51340+86400)/3600,0),
#     86400/3600,
#     800,
#     facecolor="olive",
#     alpha=0.5,
# )
# ax_top.add_patch(glow_rect)
# ax_top.add_patch(ramp_up_rect)
# ax_bottom.add_patch(ramp_up_rect_b)
ax_bottom.add_patch(bake_rect_b)
# ax_bottom.add_patch(glow_rect_b)
# ax_top.add_patch(wait_rect)
# ax_bottom.add_patch(wait_rect_b)
# ax_top.annotate("Steady state", xy=(51340/3600+1,4.5e22), xytext=(20,6e22),fontsize=15,color='cadetblue')
# ax_top.annotate("Waiting", xy=(51340/3600+1,4.5e22), xytext=(45,6e22),fontsize=15,color='olive')
# ax_top.annotate("GDC", xy=(224140/3600,0), xytext=(20,2.5e22),fontsize=15,color='cadetblue')
ax_top.annotate("Bake", xy=(224140/3600,0), xytext=(70,2e20),fontsize=15,color='black')
# ax_top.annotate("Ramp up", xy=(2.8,0), xytext=(2.9,1.5e20),fontsize=15,color='indigo')
ax_top.annotate("10 FP Pulses", xy=(1,0), xytext=(0.15,2e20),fontsize=15,color='black')

# annotating traps instead of having a legend 
ax_top.annotate("Trap 1", xy=(1,0), xytext=(0.5,0.2e20),fontsize=10,color='C0')
ax_top.annotate("Trap 2", xy=(1,0), xytext=(0.5,0.6e20),fontsize=10,color='C1')
# ax_top.annotate("Trap 3", xy=(1,0), xytext=(20,2.2e22),fontsize=10,color='C2')
# ax_top.annotate("Trap 4", xy=(1,0), xytext=(20,1.5e22),fontsize=10,color='C3')
ax_top.annotate("Total T", xy=(51340/3600+1,4.5e19), xytext=(0.5,1e20),fontsize=10,color='black')
# ax_top.annotate("Total D", xy=(51340/3600+1,4.5e22), xytext=(5,5.5e22),fontsize=10,color='green')

for ax in [ax_top, ax_bottom]:
    ax.spines[['top', 'right']].set_visible(False)


# for zoom 
# ax_top.set_xlim(51340/3600-1,224140/3600) # glow zoom
# ax_top.set_xlim(2.8,3.4) # FP zoom
# ax_top.set_ylim(1e20,1.6e20)

# plotly_fig.write_html("1_bin.html", auto_open=True)
# formatter = ScalarFormatter(useOffset=False, useMathText=False)
# formatter.set_scientific(False) 
# ax_bottom.xaxis.set_major_formatter(formatter)

plt.tight_layout()
plt.savefig("paper_plots/W_scenA.pdf", format="pdf", bbox_inches="tight")
plt.savefig("paper_plots/W_scenA")
print('done')
# plt.show()