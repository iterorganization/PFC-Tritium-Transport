import plotly.graph_objects as go
import plotly.express as px
from make_iter_bins import Div_bins, total_fw_bins, FW_bins
from plotly.subplots import make_subplots
import json
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# import scenarios
import sys
sys.path.insert(0, '/home/ITER/dunnelk/PFC-tritium-transport/iter_scenarios')
from do_nothing import scenario as scenario

file_path_d = "plotting/do_nothing_D_data.json"
file_path_t = "plotting/do_nothing_T_data.json"

with open(file_path_d, "r") as file:
    d_plot_data = json.load(file)

with open(file_path_t, "r") as file:
    t_plot_data = json.load(file)

# create material inv lists with number of points determined by length of data list 
data_t_len = len(t_plot_data["0"]["high_wetted"])
boron_inv_wall = np.zeros(data_t_len)
boron_inv_div = np.zeros(data_t_len)
tungsten_inv_wall = np.zeros(data_t_len)
tungsten_inv_div = np.zeros(data_t_len)
ss_inv_wall = np.zeros(data_t_len)
ss_inv_div = np.zeros(data_t_len)

# extract inv in materials 
for name, value in t_plot_data.items():
    for mode, data_lst in value.items():
        bin_idx = int(name)

        if bin_idx in range(18):
            if mode == "shadowed":
                material = FW_bins.get_bin(bin_idx).shadowed_subbin.material
            elif mode == "low_wetted":
                material = FW_bins.get_bin(bin_idx).low_wetted_subbin.material
            elif mode == "high_wetted":
                material = FW_bins.get_bin(bin_idx).high_wetted_subbin.material
            else:
                material = FW_bins.get_bin(bin_idx).wetted_subbin.material 

            if material == "B": 
                boron_inv_wall += data_lst
            elif material == "W":
                tungsten_inv_wall += data_lst
            else:
                ss_inv_wall += data_lst
            
        else:
            material = Div_bins.get_bin(bin_idx).material
        
            if material == "B": 
                boron_inv_div += data_lst
            elif material == "W":
                tungsten_inv_div += data_lst
            else:
                ss_inv_div += data_lst

# insert zeros for plotting purposes 
# boron_inv = np.insert(boron_inv, 0, 0)
# tungsten_inv = np.insert(tungsten_inv, 0, 0)
# ss_inv = np.insert(ss_inv, 0, 0)

# create scatter plot 
#create scatter plot in matplotlib
fig, (ax_left, ax_right) = plt.subplots(1, 2)


# pull milestones for plotting on time 
time_points = [0]

for pulse in scenario.pulses:
    time_points.append(
        time_points[-1] + pulse.total_duration * pulse.nb_pulses
    )  # end of each pulse type

time_points = time_points[2:]
plot_time = np.array(time_points) / 3600
# plot_time = np.insert(plot_time, 0, 0)

# add traces 
# fig.add_trace(
#     go.Bar(
#         x=['Boron'],
#         y=[boron_inv[0]],
#         name="Boron Inventory (atm)",
#         marker_color="firebrick",
#     )
# )

# fig.add_trace(
#     go.Bar(
#         x=['Tungsten'],
#         y=[tungsten_inv[0]],
#         name="Tungsten Inventory (atm)",
#         marker_color="royalblue",
#     )
# )

# fig.add_trace(
#     go.Bar(
#         x=['SS316'],
#         y=[ss_inv[0]],
#         name="SS316 Inventory (atm)",
#         marker_color="forestgreen",
#     )
# )

ax_left.plot([0, 1], boron_inv_wall, label="Boron Inventory", color="firebrick",linestyle="dashed", marker="o", linewidth=2)
ax_left.plot([0, 1], tungsten_inv_wall, label="Tungsten Inventory", color="royalblue",linestyle="dashed", marker="o", linewidth=2)
ax_left.annotate(text="B", xy=(1 + 0.1, boron_inv_wall[-1] + 0.1), color="firebrick")
ax_left.annotate(text="W", xy=(1 + 0.1, tungsten_inv_wall[-1] + 0.1), color="royalblue")
ax_left.annotate(f"-{float(np.diff(boron_inv_wall))/boron_inv_wall[0]:.2%}", xy=(0.5, np.mean(boron_inv_wall)*1.1) , color="firebrick")
ax_left.annotate(f"-{float(np.diff(tungsten_inv_wall))/tungsten_inv_wall[0]:.2%}", xy=(0.5, np.mean(tungsten_inv_wall)*1.01) , color="royalblue")
# fig.add_trace(
#     go.Scatter(
#         x=["After FP10", "Afer BAKE"],
#         y=boron_inv_wall,
#         # mode='markers',
#         name="Boron Inventory",
#         line=dict(color="firebrick", width=2, dash='dash'),
#     ),
#     row=1, col=1
# )

# fig.add_trace(
#     go.Scatter(
#         x=["After FP10", "Afer BAKE"],
#         y=tungsten_inv_wall,
#         # mode='markers',
#         name="Tungsten Inventory",
#         line=dict(color="royalblue", width=2, dash='dash'),
#     ),
#     row=1, col=1
# )

# fig.add_trace(
#     go.Scatter(
#         x=["After FP10", "Afer BAKE"],
#         y=ss_inv_wall,
#         name="SS316 Inventory",
#         # mode='markers',
#         line=dict(color="forestgreen", width=2, dash='dash'),
#     ),
#     row=1, col=1
# )

ax_right.plot([0, 1], boron_inv_div, marker="o",color="firebrick",linestyle="dashed", linewidth=2)
ax_right.plot([0, 1], tungsten_inv_div, marker="o",color="royalblue",linestyle="dashed", linewidth=2)

ax_right.annotate(text="B", xy=(1.1, boron_inv_div[-1] + 0.1), color="firebrick")
ax_right.annotate(text="W", xy=(1.1, tungsten_inv_div[-1] + 0.1), color="royalblue")

# ax_right.annotate(f"x{boron_inv_div[-1]/boron_inv_div[0]:.2f}", xy=(0.5, np.mean(boron_inv_div)*1.1) , color="firebrick")
# ax_right.annotate(f"x{tungsten_inv_div[-1]/tungsten_inv_div[0]:.2f}", xy=(0.5, np.mean(tungsten_inv_div)*1.1) , color="royalblue")

ax_right.annotate(f"-{float(np.diff(boron_inv_div))/boron_inv_div[0]:.2%}", xy=(0.5, np.mean(boron_inv_div)*1.1) , color="firebrick")
ax_right.annotate(f"-{float(np.diff(tungsten_inv_div))/tungsten_inv_div[0]:.2%}", xy=(0.5, np.mean(tungsten_inv_div)*1.05) , color="royalblue")
# fig.add_trace(
#     go.Scatter(
#         x=["After FP10", "Afer BAKE"],
#         y=boron_inv_div,
#         # mode='markers',
#         name="Boron Inventory",
#         line=dict(color="firebrick", width=2, dash='dash'),
#         showlegend=False
#     ),
#     row=1, col=2
# )

# fig.add_trace(
#     go.Scatter(
#         x=["After FP10", "Afer BAKE"],
#         y=tungsten_inv_div,
#         # mode='markers',
#         name="Tungsten Inventory",
#         line=dict(color="royalblue", width=2, dash='dash'),
#         showlegend=False
#     ),
#     row=1, col=2
# )

# fig.add_trace(
#     go.Scatter(
#         x=["After FP10", "Afer BAKE"],
#         y=ss_inv_div,
#         name="SS316 Inventory",
#         # mode='markers',
#         line=dict(color="forestgreen", width=2, dash='dash'),
#         showlegend=False
#     ),
#     row=1, col=2
# )

ax_left.set_yscale("log")
ax_right.set_yscale("log")
ax_left.set_ylabel("Inventory (T)")
ax_right.set_ylabel("Inventory (T/m)")
# ax_top.legend(loc='upper left')
ax_left.grid(which="both", alpha=0.3)
ax_right.grid(which="both", alpha=0.3)

ax_left.set_title('Wall')
ax_right.set_title('Divertor')

ax_left.set_xticks([0, 1], ["After FP10", "Afer BAKE"])
ax_right.set_xticks([0, 1], ["After FP10", "Afer BAKE"])
# --- Format bottom axis ---
# ax_bottom.set_ylabel("Surface Temp")
# ax_left.legend(loc='upper right')

#legend 
# tungsten=mpatches.Patch(color='royalblue',label="W")
# boron=mpatches.Patch(color='firebrick',label="B")

for ax in [ax_left, ax_right]:
    ax.spines[['top', 'right']].set_visible(False)
    ax.set_xlim(right=1.2)
    # ax.set_ylim(1e18, 1e20)

plt.tight_layout()
# plt.legend(handles=[tungsten,boron],loc='upper right')
plt.savefig("paper_plots/material-comp.pdf", bbox_inches="tight")
plt.savefig("paper_plots/material-comp.png", bbox_inches="tight")
print('done')