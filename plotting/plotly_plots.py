import plotly.graph_objects as go
from plotly.subplots import make_subplots

import json
from make_iter_bins import Div_bins, total_fw_bins, FW_bins
import math
import numpy as np

TRITIUM_AMU = 3.016049  # g/mol
D_AMU = 2.014102  # g/mol
T_AMU = 3.016049  # g/mol
AVOGADROS_CONST = 6.0221408e23  # atms/mol

BIN_INDEX = 21


def get_bin_data(data: list, bin_index: int) -> dict:
    """Returns the right dictionary for a given bin index

    Args:
        data (list): the list of dictionaries
        bin_index (int): the bin index
    """

    for i in data:
        if i["bin_index"] == bin_index:
            return i


if BIN_INDEX in range(total_fw_bins):
    my_bin = FW_bins.get_bin(BIN_INDEX)
else:
    my_bin = Div_bins.get_bin(BIN_INDEX)

avg_r_coord = 0.5 * abs(my_bin.start_point[0] + my_bin.end_point[0])
bin_surf_area = 2 * math.pi * avg_r_coord * my_bin.length

# open results file
with open("processed_data.json", "r") as file:
    dict_data = json.load(file)

bin_data = get_bin_data(dict_data, BIN_INDEX)

if BIN_INDEX in list(range(18, 62)):
    fig = make_subplots(
        rows=4,
        cols=1,
        subplot_titles=(
            "Dissected Inventory",
            "Total Inventory",
            "Surface Fluxes",
            "Surface Temperature",
        ),
        shared_xaxes=True,
        vertical_spacing=0.05,
    )

    Time_Full = False
    for name, value in bin_data.items():
        # skip the bin_index
        if name == "bin_index":
            continue
        quantities_dict = value
        if not Time_Full:
            time = quantities_dict["t"]
            Time_Full = True
        D_inventory = np.zeros(len(time))
        T_inventory = np.zeros(len(time))
        D_surface_flux = np.zeros(len(time))
        T_surface_flux = np.zeros(len(time))
    for name, value in bin_data.items():
        # skip the bin_index
        if name == "bin_index":
            continue
        print(name)
        quantities_dict = value
        data = np.array(quantities_dict["data"])
        if "temperature" in name:
            surface_time = np.array(quantities_dict["t"])
            surface_temp = data
        if "D" in name:
            if "flux" in name:
                D_surface_flux = data
            else:
                D_inventory += data
                if name == "D":
                    fig.add_trace(
                        go.Scatter(
                            x=time,
                            y=data * bin_surf_area / AVOGADROS_CONST * D_AMU,
                            name="mobile_D",
                            line=dict(width=2),
                        ),
                        row=1,
                        col=1,
                    )
                else:
                    fig.add_trace(
                        go.Scatter(
                            x=time,
                            y=data * bin_surf_area / AVOGADROS_CONST * D_AMU,
                            name=name,
                            line=dict(width=2),
                        ),
                        row=1,
                        col=1,
                    )
        elif "T" in name:
            if "flux" in name:
                T_surface_flux = data
            else:
                T_inventory += data
                if name == "T":
                    fig.add_trace(
                        go.Scatter(
                            x=time,
                            y=data * bin_surf_area / AVOGADROS_CONST * T_AMU,
                            name="mobile_T",
                            line=dict(width=2),
                        ),
                        row=1,
                        col=1,
                    )
                else:
                    fig.add_trace(
                        go.Scatter(
                            x=time,
                            y=data * bin_surf_area / AVOGADROS_CONST * T_AMU,
                            name=name,
                            line=dict(width=2),
                        ),
                        row=1,
                        col=1,
                    )
    D_grams = D_inventory * bin_surf_area / AVOGADROS_CONST * D_AMU
    T_grams = T_inventory * bin_surf_area / AVOGADROS_CONST * T_AMU

    # plotting with plotly

    fig.add_trace(
        go.Scatter(
            x=time, y=D_grams, name="total_D", line=dict(color="firebrick", width=2)
        ),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=time, y=T_grams, name="total_T", line=dict(color="royalblue", width=2)
        ),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=time,
            y=D_surface_flux,
            line=dict(color="firebrick", width=2),
            showlegend=False,
        ),
        row=3,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=time,
            y=T_surface_flux,
            line=dict(color="royalblue", width=2),
            showlegend=False,
        ),
        row=3,
        col=1,
    )
    fig.add_trace(
        go.Scatter(x=surface_time, y=surface_temp, showlegend=False), row=4, col=1
    )

    # for point in [429,1079,1534,86400,86829,87479,87934,172800,173229,173879,174334]:
    #     fig.add_vline(x=point, line_width=0.5, line_color="green")

    fig.update_xaxes(title_text="Time (s)", row=4, col=1)
    fig.update_yaxes(title_text="Total Quantity (g)", row=1, col=1, type="log")
    fig.update_yaxes(title_text="Total Quantity (g)", row=2, col=1)  # type="log")
    fig.update_yaxes(title_text="Flux (part/m2 s)", row=3, col=1, type="log")
    fig.update_yaxes(title_text="Temperature (K)", row=4, col=1)

    fig.update_layout(title_text="Bin " + str(BIN_INDEX) + " Results Test Scenario")

    fig.write_html("test3_BB.html", auto_open=True)

else:
    sub_bin_data = bin_data["sub_bins"]
    Time_Full = False
    D_Full = False
    fig = make_subplots(
        rows=4,
        cols=1,
        subplot_titles=(
            "Dissected Inventory",
            "Inventory",
            "Surface Fluxes",
            "Surface Temperature",
        ),
        shared_xaxes=True,
        vertical_spacing=0.05,
    )

    for sub_bin in sub_bin_data:
        mode = sub_bin["mode"]
        for name, quantities_dict in sub_bin.items():
            # skip the parent bin_index
            if name == "parent_bin_index":
                continue
            if name == "mode":
                continue
            if not Time_Full:
                time = quantities_dict["t"]
                Time_Full = True
        D_sub = np.zeros(len(time))
        T_sub = np.zeros(len(time))
        D_mobile_sub = np.zeros(len(time))
        T_mobile_sub = np.zeros(len(time))
        D_trapped_sub = np.zeros(len(time))
        T_trapped_sub = np.zeros(len(time))
        D_surface_flux = np.zeros(len(time))
        T_surface_flux = np.zeros(len(time))

        for name, quantities_dict in sub_bin.items():
            # skip the parent bin_index
            if name == "parent_bin_index":
                continue
            if name == "mode":
                continue
            print(name)
            data = np.array(quantities_dict["data"])
            if "temperature" in name:
                data = np.array(quantities_dict["data"])
                surface_temp = data
            if "D" in name:
                if "flux" in name and D_surface_flux is not None:
                    D_surface_flux = data
                else:
                    D_sub += data
                    if "trap" in name:
                        D_trapped_sub += data
                    else:
                        D_mobile_sub += data
            elif "T" in name:
                if "flux" in name and T_surface_flux is not None:
                    T_surface_flux = data
                else:
                    T_sub += data
                    if "trap" in name:
                        T_trapped_sub += data
                        T_mobile_sub += data

        if not D_Full:
            D_inventory = D_sub
            T_inventory = T_sub
            D_trapped = D_trapped_sub
            T_trapped = T_trapped_sub
            D_mobile = D_mobile_sub
            T_mobile = T_mobile_sub
            D_Full = True
        else:
            D_inventory += D_sub
            T_inventory += T_sub
            D_trapped += D_trapped_sub
            T_trapped += T_trapped_sub
            D_mobile += D_mobile_sub
            T_mobile += T_mobile_sub
    D_grams = D_inventory * bin_surf_area / AVOGADROS_CONST * D_AMU
    T_grams = T_inventory * bin_surf_area / AVOGADROS_CONST * D_AMU

    # plotting with plotly
    fig.add_trace(
        go.Scatter(
            x=time,
            y=D_mobile * bin_surf_area / AVOGADROS_CONST * D_AMU,
            name="mobile_D",
            line=dict(width=2),
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=time,
            y=T_mobile * bin_surf_area / AVOGADROS_CONST * D_AMU,
            name="mobile_T",
            line=dict(width=2),
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=time,
            y=D_trapped * bin_surf_area / AVOGADROS_CONST * D_AMU,
            name="trapped_D",
            line=dict(width=2),
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=time,
            y=T_trapped * bin_surf_area / AVOGADROS_CONST * D_AMU,
            name="trapped_T",
            line=dict(width=2),
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=time, y=D_grams, name="total_D", line=dict(color="firebrick", width=2)
        ),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=time, y=T_grams, name="total_T", line=dict(color="royalblue", width=2)
        ),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=time,
            y=D_surface_flux,
            name="D",
            line=dict(color="firebrick", width=2),
            showlegend=False,
        ),
        row=3,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=time,
            y=T_surface_flux,
            name="T",
            line=dict(color="royalblue", width=2),
            showlegend=False,
        ),
        row=3,
        col=1,
    )
    fig.add_trace(go.Scatter(x=time, y=surface_temp), row=4, col=1)

    # for point in [429,1079,1534,86400,86829,87479,87934,172800,173229,173879,174334]:
    #     fig.add_vline(x=point, line_width=0.5, line_color="green")

    fig.update_xaxes(title_text="Time (s)", row=4, col=1)
    fig.update_yaxes(title_text="Total Quantity (g)", row=1, col=1, type="log")
    fig.update_yaxes(title_text="Total Quantity (g)", row=2, col=1)
    fig.update_yaxes(title_text="Flux (part/m2 s)", row=3, col=1)
    fig.update_yaxes(title_text="Temperature (K)", row=4, col=1)

    fig.update_layout(
        title_text="Bin " + str(BIN_INDEX) + " " + mode + " Results Test Scenario"
    )

    fig.write_html("test2_SS.html", auto_open=True)
