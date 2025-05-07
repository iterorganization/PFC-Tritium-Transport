# post-process inventory bar graphs
import json
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from make_iter_bins import Div_bins, total_fw_bins, FW_bins
import math

# import scenarios
from iter_scenarios.do_nothing import scenario as scenario

# from iter_scenarios.capability_test import scenario as scenario

# pull milestones at end of each pulse type for plotting
time_points = [0]

for pulse in scenario.pulses:
    time_points.append(
        time_points[-1] + pulse.total_duration * pulse.nb_pulses
    )  # end of each pulse type

time_points.remove(0)

print(time_points)

fig1 = make_subplots(rows=2, cols=1, shared_xaxes=True)
fig2 = make_subplots(rows=2, cols=2, shared_xaxes=True)
fig3 = make_subplots(rows=2, cols=2, shared_xaxes=True)

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


# func to calculate bin surface area
def calculate_bin_surface_area(bin_start_point, bin_end_point, bin_length):
    avg_r_coord = 0.5 * abs(bin_start_point[0] + bin_end_point[0])
    return 2 * math.pi * avg_r_coord * bin_length


# Function to load, process, and plot bin data for each bin
def load_and_process_bin_data(file_path, bin_surf_area, scenario_time, material):
    with open(file_path, "r") as file:
        bin_data = json.load(file)

    data_list_D = np.zeros(len(time_points))
    data_list_T = np.zeros(len(time_points))

    for name, value in bin_data.items():
        if name == "bin_index" or name == "parent_bin_index" or name == "mode":
            if name == "bin_index" or name == "parent_bin_index":
                bin_idx = value
            elif name == "mode":
                mode == value
            continue

        quantities_dict = value
        time = np.array(quantities_dict["t"])
        data = np.array(quantities_dict["data"])
        processed_times = []
        for idx, t in enumerate(time):
            if t in scenario_time:
                processed_times.append(t)
                time_idx = np.where(t == scenario_time)[0]
                if "D" in name:
                    data_list_D[time_idx] += data[idx] 
                elif "T" in name:
                    data_list_T[time_idx] += data[idx] 
            else:
                if material == "W" or material == "DFW":
                    if np.any(
                        np.isclose(t, np.array(processed_times), atol=0.01, rtol=0)
                    ):
                        continue
                    else:
                        if np.any(
                            np.isclose(t, np.array(scenario_time), atol=0.01, rtol=0)
                        ):
                            processed_times.append(t)
                            time_idx = np.where(
                                np.isclose(t, scenario_time, rtol=0, atol=1e-2)
                            )[0]
                            if "D" in name:
                                data_list_D[time_idx] += data[idx] * bin_surf_area
                            elif "T" in name:
                                data_list_T[time_idx] += data[idx] * bin_surf_area
                elif material == "B":
                    if np.any(
                        np.isclose(t, np.array(processed_times), atol=1e-5, rtol=0)
                    ):
                        continue
                    else:
                        if np.any(
                            np.isclose(t, np.array(scenario_time), rtol=0, atol=1e-4)
                        ):
                            processed_times.append(t)
                            time_idx = np.where(
                                np.isclose(t, scenario_time, rtol=0, atol=1e-5)
                            )[0]
                            if "D" in name:
                                data_list_D[time_idx] += data[idx] 
                            elif "T" in name:
                                data_list_T[time_idx] += data[idx] 
            if t == float(
                scenario.get_maximum_time() - 1
            ):  # write exception for the last point
                time_idx = -1
                if "D" in name:
                    data_list_D[time_idx] += data[idx] 
                elif "T" in name:
                    data_list_T[time_idx] += data[idx] 

    # return data_list_D, data_list_T
    # color coding and fake legend traces
    if bin_idx in range(18):
        print(bin_idx)
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

    elif bin_idx in range(18, 63):
        print(bin_idx)
        right_col = 2  # separating wall and divertor values
        if material == "W":
            color = "darkblue"
        elif material == "B":
            color = "darkred"

    fig1.add_trace(
        go.Bar(
            x=[x_labels[bin_idx]],
            y=[data_list_D[0]],
            name=material + " " + mode,
            marker_color=color,
        ),
        row=1,
        col=1,
    )
    fig1.add_trace(
        go.Bar(
            x=[x_labels[bin_idx]],
            y=[data_list_T[0]],
            name=material + " " + mode,
            marker_color=color,
        ),
        row=2,
        col=1,
    )

    fig2.add_trace(
        go.Bar(
            x=[x_labels[bin_idx]],
            y=[data_list_D[1]],
            name=material + " " + mode,
            marker_color=color,
            showlegend=False,
        ),
        row=1,
        col=right_col,
    )
    fig2.add_trace(
        go.Bar(
            x=[x_labels[bin_idx]],
            y=[data_list_T[1]],
            name=material + " " + mode,
            marker_color=color,
            showlegend=False,
        ),
        row=2,
        col=right_col,
    )

    fig3.add_trace(
        go.Bar(
            x=[x_labels[bin_idx]],
            y=[data_list_D[2]],
            name=material + " " + mode,
            marker_color=color,
            showlegend=False,
        ),
        row=1,
        col=right_col,
    )
    fig3.add_trace(
        go.Bar(
            x=[x_labels[bin_idx]],
            y=[data_list_T[2]],
            name=material + " " + mode,
            marker_color=color,
            showlegend=False,
        ),
        row=2,
        col=right_col,
    )


# Process wall bins (0 to 17)
for i in range(18):
    if i in [13, 14, 16, 17]:
        for mode in ["shadowed", "wetted"]:
            file_path = f"results_do_nothing/wall_bin_{i}_sub_bin_{mode}.json"
            if mode == "shadowed":
                bin_surf_area = FW_bins.get_bin(i).shadowed_subbin.surface_area
                material = FW_bins.get_bin(i).shadowed_subbin.material
            elif mode == "wetted":
                bin_surf_area = FW_bins.get_bin(i).wetted_subbin.surface_area
                material = FW_bins.get_bin(i).wetted_subbin.material
            data_list_D, data_list_T = load_and_process_bin_data(
                file_path,
                bin_surf_area,
                time_points,
                material,
            )
    else:
        for mode in ["shadowed", "low_wetted", "high_wetted"]:
            file_path = f"results_do_nothing/wall_bin_{i}_sub_bin_{mode}.json"
            if mode == "shadowed":
                bin_surf_area = FW_bins.get_bin(i).shadowed_subbin.surface_area
                material = FW_bins.get_bin(i).shadowed_subbin.material
            elif mode == "low_wetted":
                bin_surf_area = FW_bins.get_bin(i).low_wetted_subbin.surface_area
                material = FW_bins.get_bin(i).low_wetted_subbin.material
            else:
                bin_surf_area = FW_bins.get_bin(i).high_wetted_subbin.surface_area
                material = FW_bins.get_bin(i).high_wetted_subbin.material
            load_and_process_bin_data(
                file_path,
                bin_surf_area,
                time_points,
                material,
            )
    if i in [9, 13, 14]:
        file_path = f"results_do_nothing/wall_bin_{i}_sub_bin_dfw.json"
        if FW_bins.get_bin(i).shadowed_subbin.dfw:
            bin_surf_area = FW_bins.get_bin(i).shadowed_subbin.surface_area
        material = "DFW"
        load_and_process_bin_data(file_path, bin_surf_area, time_points, material)
    


# process div bins
for i in range(18, 62):
    file_path = f"results_do_nothing/div_bin_{i}.json"
    bin_surf_area = calculate_bin_surface_area(
        Div_bins.get_bin(i).start_point,
        Div_bins.get_bin(i).end_point,
        Div_bins.get_bin(i).length,
    )
    material = Div_bins.get_bin(i).material
    load_and_process_bin_data(file_path, bin_surf_area, time_points, material)

# updating figure parameters
fig2.update_layout(
    title_text="Hydrogen Inventory (atm) after FP10 Pulses",
    legend=dict(title=dict(text="Material and/or Mode")),
)
fig3.update_layout(
    title_text="Hydrogen Inventory (atm) after Bake",
    legend=dict(title=dict(text="Material and/or Mode")),
)

fig2.update_xaxes(title_text="Bin Index", row=2, col=1)
fig2.update_xaxes(title_text="Bin Index", row=2, col=2)
fig2.update_yaxes(title_text="D Quantity (atm)", row=1, col=1)
fig2.update_yaxes(title_text="T Quantity (atm)", row=2, col=1)
fig3.update_yaxes(title_text="D Quantity (atm)", row=1, col=2)
fig3.update_yaxes(title_text="T Quantity (atm)", row=2, col=2)

# fake legend traces
fig2.add_trace(
    go.Scatter(
        x=[None],
        y=[None],
        mode="markers",
        marker=dict(color="purple", symbol="circle"),
        name="W High Wetted",
        showlegend=True,
    )
)
fig2.add_trace(
    go.Scatter(
        x=[None],
        y=[None],
        mode="markers",
        marker=dict(color="blue", symbol="circle"),
        name="W Low Wetted",
        showlegend=True,
    )
)
fig2.add_trace(
    go.Scatter(
        x=[None],
        y=[None],
        mode="markers",
        marker=dict(color="aqua", symbol="circle"),
        name="W Shadowed",
        showlegend=True,
    )
)
fig2.add_trace(
    go.Scatter(
        x=[None],
        y=[None],
        mode="markers",
        marker=dict(color="yellow", symbol="circle"),
        name="SS (Shadowed)",
        showlegend=True,
    )
)
fig2.add_trace(
    go.Scatter(
        x=[None],
        y=[None],
        mode="markers",
        marker=dict(color="green", symbol="circle"),
        name="B High Wetted",
        showlegend=True,
    )
)
fig2.add_trace(
    go.Scatter(
        x=[None],
        y=[None],
        mode="markers",
        marker=dict(color="lightgreen", symbol="circle"),
        name="B Low Wetted",
        showlegend=True,
    )
)
fig2.add_trace(
    go.Scatter(
        x=[None],
        y=[None],
        mode="markers",
        marker=dict(color="orange", symbol="circle"),
        name="B Shadowed",
        showlegend=True,
    )
)
fig3.add_trace(
    go.Scatter(
        x=[None],
        y=[None],
        mode="markers",
        marker=dict(color="orange", symbol="circle"),
        name="B Shadowed",
        showlegend=True,
    )
)
fig3.add_trace(
    go.Scatter(
        x=[None],
        y=[None],
        mode="markers",
        marker=dict(color="lightgreen", symbol="circle"),
        name="B Low Wetted",
        showlegend=True,
    )
)
fig3.add_trace(
    go.Scatter(
        x=[None],
        y=[None],
        mode="markers",
        marker=dict(color="green", symbol="circle"),
        name="B High Wetted",
        showlegend=True,
    )
)
fig3.add_trace(
    go.Scatter(
        x=[None],
        y=[None],
        mode="markers",
        marker=dict(color="yellow", symbol="circle"),
        name="SS (Shadowed)",
        showlegend=True,
    )
)
fig3.add_trace(
    go.Scatter(
        x=[None],
        y=[None],
        mode="markers",
        marker=dict(color="aqua", symbol="circle"),
        name="W Shadowed",
        showlegend=True,
    )
)
fig3.add_trace(
    go.Scatter(
        x=[None],
        y=[None],
        mode="markers",
        marker=dict(color="purple", symbol="circle"),
        name="W High Wetted",
        showlegend=True,
    )
)
fig3.add_trace(
    go.Scatter(
        x=[None],
        y=[None],
        mode="markers",
        marker=dict(color="blue", symbol="circle"),
        name="W Low Wetted",
        showlegend=True,
    )
)


fig2.add_trace(
    go.Scatter(
        x=[None],
        y=[None],
        mode="markers",
        marker=dict(color="darkblue", symbol="circle"),
        name="W Div",
        showlegend=True,
    )
)
fig3.add_trace(
    go.Scatter(
        x=[None],
        y=[None],
        mode="markers",
        marker=dict(color="darkred", symbol="circle"),
        name="B Div",
        showlegend=True,
    )
)

fig2.write_html("bar-do-nothing-1.html", auto_open=True)
fig3.write_html("bar--do-nothing-2.html", auto_open=True)
