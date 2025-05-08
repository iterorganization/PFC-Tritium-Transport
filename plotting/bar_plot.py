import plotly.graph_objects as go
from make_iter_bins import Div_bins, total_fw_bins, FW_bins
from plotly.subplots import make_subplots
import json
import numpy as np

###### THIS FILE CREATES BAR GRAPHS AT SPECIFIED TIME POINTS FOR ALL BINS AND SUBBINS IN A SCENARIO ######
## There are a few things that need to be adjusted depending on what you want to plot:
# System path directory on line 17
# Scenario that you'd like to import and plot on line 18 
# D and T inventory file names created from post_process_data.py on lines 87 and 88
# Figure name on line 316
## Then you're good to go!

# import scenarios
import sys
sys.path.insert(0, '/home/ITER/dunnelk/PFC-tritium-transport/iter_scenarios')
from do_nothing import scenario as scenario

x_labels = [
    "FW P1",
    "FW P2",
    "FW P3",
    "FW P4",
    "FW P5",
    "FW P6",
    "FW P7",
    "FW P8",
    "FW P9",
    "FW P10",
    "FW P11",
    "FW P12",
    "FW P13",
    "FW P14",
    "FW P15",
    "FW P16",
    "FW P17",
    "FW P18",
    "OVT 19",
    "OVT 20",
    "OVT 21",
    "OVT 22",
    "OVT 23",
    "OVT 24",
    "OVT 25",
    "OVT 26",
    "OVT 27",
    "OVT 28",
    "OVT 29",
    "OVT 30",
    "OVT 31",
    "OVT 32",
    "OHP 33",
    "OHP 34",
    "DOM 35",
    "DOM 36",
    "DOM 37",
    "DOM 38",
    "DOM 39",
    "DOM 40",
    "DOM 41",
    "DOM 42",
    "IHP 43",
    "IHP 44",
    "IHP 45",
    "IHP 46",
    "IVT 47",
    "IVT 48",
    "IVT 49",
    "IVT 50",
    "IVT 51",
    "IVT 52",
    "IVT 53",
    "IVT 54",
    "IVT 55",
    "IVT 56",
    "IVT 57",
    "IVT 58",
    "IVT 59",
    "IVT 60",
    "IVT 61",
    "IVT 62",
    "IVT 63",
    "IVT 64",
]

file_path_d = "plotting/do_nothing_data_D.json"
file_path_t = "plotting/do_nothing_data_T.json"

with open(file_path_d, "r") as file:
    d_plot_data = json.load(file)

with open(file_path_t, "r") as file:
    t_plot_data = json.load(file)

# create figures based on the length of each list in values of dictionary
fig_pattern = "fig{}"
data_t = t_plot_data["0"]["high_wetted"]

print(f"{len(data_t)} figures will be made.")
for i, val in enumerate(data_t, start=1):
    globals()[fig_pattern.format(i)] = make_subplots(rows=2, cols=2, shared_xaxes=True)
    globals()[fig_pattern.format(i)].update_layout(
        title_text="Hydrogen Inventory (atm) after Pulse Type " + str(i),
        legend=dict(title=dict(text="Material and/or Mode")),
    )
    globals()[fig_pattern.format(i)].update_xaxes(title_text="Bin Index", row=2, col=2)
    globals()[fig_pattern.format(i)].update_xaxes(title_text="Bin Index", row=2, col=1)
    globals()[fig_pattern.format(i)].update_yaxes(
        title_text="D Quantity (atm)", row=1, col=1
    )
    globals()[fig_pattern.format(i)].update_yaxes(
        title_text="T Quantity (atm)", row=2, col=1
    )
    globals()[fig_pattern.format(i)].update_yaxes(
        title_text="D Quantity (atm/m)", row=1, col=2
    )
    globals()[fig_pattern.format(i)].update_yaxes(
        title_text="D Quantity (atm/m)", row=2, col=2
    )

# plotting tritium
for name, value in t_plot_data.items():
    for mode, data_lst in value.items():
        bin_idx = int(name)

        if bin_idx in range(18):
            if mode == "shadowed":
                material = FW_bins.get_bin(i).shadowed_subbin.material
            elif mode == "low_wetted":
                material = FW_bins.get_bin(i).low_wetted_subbin.material
            elif mode == "high_wetted":
                material = FW_bins.get_bin(i).high_wetted_subbin.material
            else:
                material = FW_bins.get_bin(i).wetted_subbin.material
        else:
            material = Div_bins.get_bin(bin_idx).material

        # color coding and fake legend traces
        if bin_idx in range(18):
            right_col = 1  # separating wall and divertor values
            if material == "W" and mode == "high_wetted":
                color = "purple"
            elif material == "W" and mode == "wetted":
                color = "purple"
            elif material == "W" and mode == "low_wetted":
                color = "blue"
            elif material == "W" and mode == "shadowed":
                color = "aqua"
            elif material == "B" and mode == "high_wetted":
                color = "green"
            elif material == "B" and mode == "wetted":
                color = "green"
            elif material == "B" and mode == "low_wetted":
                color = "lightgreen"
            elif material == "B" and mode == "shadowed":
                color = "orange"
            else:
                color = "pink"

        elif bin_idx in range(18, 62):
            right_col = 2  # separating wall and divertor values
            if material == "W":
                color = "darkblue"
            elif material == "B":
                color = "darkred"

        for numb in range(1, len(data_lst) + 1):
            globals()[fig_pattern.format(numb)].add_trace(  # just tritium plotting here
                go.Bar(
                    x=[x_labels[bin_idx]],
                    y=[data_lst[numb - 1]],
                    name=material + " " + mode,
                    marker_color=color,
                    showlegend=False,
                ),
                row=2,
                col=right_col,
            )

# plotting deuterium
for name, value in d_plot_data.items():
    for mode, data_lst in value.items():
        bin_idx = int(name)

        if bin_idx in range(18):
            if mode == "shadowed":
                material = FW_bins.get_bin(i).shadowed_subbin.material
            elif mode == "low_wetted":
                material = FW_bins.get_bin(i).low_wetted_subbin.material
            elif mode == "high_wetted":
                material = FW_bins.get_bin(i).high_wetted_subbin.material
            else:
                material = FW_bins.get_bin(i).wetted_subbin.material
        else:
            material = Div_bins.get_bin(bin_idx).material

        # color coding and fake legend traces
        if bin_idx in range(18):
            right_col = 1  # separating wall and divertor values
            if material == "W" and mode == "high_wetted":
                color = "purple"
            elif material == "W" and mode == "wetted":
                color = "purple"
            elif material == "W" and mode == "low_wetted":
                color = "blue"
            elif material == "W" and mode == "shadowed":
                color = "aqua"
            elif material == "B" and mode == "high_wetted":
                color = "green"
            elif material == "B" and mode == "wetted":
                color = "green"
            elif material == "B" and mode == "low_wetted":
                color = "lightgreen"
            elif material == "B" and mode == "shadowed":
                color = "orange"
            else:
                color = "pink"

        elif bin_idx in range(18, 62):
            right_col = 2  # separating wall and divertor values
            if material == "W":
                color = "darkblue"
            elif material == "B":
                color = "darkred"

        for numb in range(1, len(data_lst) + 1):
            globals()[
                fig_pattern.format(numb)
            ].add_trace(  # just deuterium plotting here
                go.Bar(
                    x=[x_labels[bin_idx]],
                    y=[data_lst[numb - 1]],
                    name=material + " " + mode,
                    marker_color=color,
                    showlegend=False,
                ),
                row=1,
                col=right_col,
            )

# fake legend traces and write figures
for i, val in enumerate(data_t, start=1):
    globals()[fig_pattern.format(i)].add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker=dict(color="purple", symbol="circle"),
            name="W High Wetted",
            showlegend=True,
        )
    )
    globals()[fig_pattern.format(i)].add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker=dict(color="blue", symbol="circle"),
            name="W Low Wetted",
            showlegend=True,
        )
    )
    globals()[fig_pattern.format(i)].add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker=dict(color="aqua", symbol="circle"),
            name="W Shadowed",
            showlegend=True,
        )
    )
    globals()[fig_pattern.format(i)].add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker=dict(color="yellow", symbol="circle"),
            name="SS (Shadowed)",
            showlegend=True,
        )
    )
    globals()[fig_pattern.format(i)].add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker=dict(color="green", symbol="circle"),
            name="B High Wetted",
            showlegend=True,
        )
    )
    globals()[fig_pattern.format(i)].add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker=dict(color="lightgreen", symbol="circle"),
            name="B Low Wetted",
            showlegend=True,
        )
    )
    globals()[fig_pattern.format(i)].add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker=dict(color="orange", symbol="circle"),
            name="B Shadowed",
            showlegend=True,
        )
    )

    globals()[fig_pattern.format(i)].write_html(
        "do_nothing_bar_" + str(i) + ".html", auto_open=True
    )
