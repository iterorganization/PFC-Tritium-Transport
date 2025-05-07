from hisp.scenario import Scenario, Pulse

from iter_scenarios.benchmark import gdc, bake
from iter_scenarios.do_nothing import fp

# fp = Pulse(
#     pulse_type="FP",
#     nb_pulses=5,
#     ramp_up=429,
#     steady_state=650,
#     ramp_down=455,
#     waiting=84866,
#     tritium_fraction=0.5,
# )
risp6 = Pulse(
    pulse_type="RISP",
    nb_pulses=6,
    ramp_up=10,
    steady_state=250,
    ramp_down=10,
    waiting=1530,
    tritium_fraction=0.0,
)
icwc_long = Pulse(
    pulse_type="ICWC",
    nb_pulses=1,
    ramp_up=10,
    steady_state=280,
    ramp_down=10,
    waiting=75300,  # icwc waiting plus rest of day
    tritium_fraction=0.0,
)
scenario = Scenario(pulses=[fp, risp6, icwc_long, fp, risp6, icwc_long, gdc, bake])