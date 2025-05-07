import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

#  Plotting with Plotly
from iter_scenarios.do_nothing import scenario as scenario
# from iter_scenarios.do_nothing import scenario as scenario

# pull milestones for plotting
time_points = [0]

for pulse in scenario.pulses:
    if pulse.pulse_type == "GDC" or pulse.pulse_type == "ICWC":
        for i in range(pulse.nb_pulses):
            time_points.append(time_points[-1] + pulse.duration_no_waiting)
            time_points.append(time_points[-1] + pulse.waiting)
    else:
        for i in range(pulse.nb_pulses):
            time_points.append(time_points[-1] + pulse.ramp_up) # end of ramp up
            time_points.append(time_points[-1] + pulse.steady_state) # start of ramp down 
            time_points.append(time_points[-1] + pulse.ramp_down) # end of ramp down 
            # time_points.append(time_points[-1] + pulse.duration_no_waiting)
            time_points.append(time_points[-1] + pulse.waiting)


plot_time = np.array(time_points) / 3600

D_inventory = np.loadtxt('cycle_data_d')
T_inventory = np.loadtxt('cycle_data_t')

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=plot_time,
        y=D_inventory,
        name="Total D",
        line=dict(color="firebrick", width=2),
        stackgroup="one",
    )
)

fig.add_trace(
    go.Scatter(
        x=plot_time,
        y=T_inventory,
        name="Total T",
        line=dict(color="royalblue", width=2),
        stackgroup="one",
    )
)

fig.update_xaxes(title_text="Time (hrs)")
fig.update_yaxes(title_text="Total Quantity (g)") #,type='log')

fig.update_layout(title_text="Total Inventory for 'Do Nothing'")

fig.write_html("do_nothing_inventory_plot.html", auto_open=True)

print('Finished.')
