# 5FP DT
# 1FP DD, decrease fluxes and loads by 5
# 5FP DT
# 1FP DD, decrease fluxes and loads by 5
# GDC 1 day
# bake

from hisp.scenario import Scenario, Pulse
from iter_scenarios.benchmark import bake, gdc

# assumes first pulse begins at 6am on day one
# scenarios thus stretch from 6am day one to 6:00am day 15 (for the start of the next scenario)
fp = Pulse(
    pulse_type="FP",
    nb_pulses=5,
    ramp_up=429,
    steady_state=650,
    ramp_down=455,
    waiting=3600,
    tritium_fraction=0.5,
)

fp_d = Pulse(
    pulse_type="FP_D",
    nb_pulses=1,
    ramp_up=429,
    steady_state=650,
    ramp_down=455,
    waiting=3600,
    tritium_fraction=0.0,
)

scenario = Scenario(pulses=[fp, fp_d, fp, fp_d, gdc, bake])
