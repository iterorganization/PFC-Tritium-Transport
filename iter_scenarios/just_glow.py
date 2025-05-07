from iter_scenarios.benchmark import gdc, bake
from hisp.scenario import Scenario, Pulse

fp = Pulse(
    pulse_type="FP",
    nb_pulses=10,
    ramp_up=429,
    steady_state=650,
    ramp_down=455,
    waiting=3600,
    tritium_fraction=0.5,
)
# gdc = Pulse(
#     pulse_type="GDC",
#     nb_pulses=1,
#     ramp_up=1,
#     steady_state=172798, # 2 day glow
#     ramp_down=1,
#     waiting=172800, # 2 days waiting 
#     tritium_fraction=0.0,
# )
# bake = Pulse(
#     pulse_type="BAKE",
#     nb_pulses=1,
#     ramp_up=1,
#     steady_state=604797,
#     ramp_down=1,
#     waiting=1,
#     tritium_fraction=0.0,
# )


scenario = Scenario(
    pulses=[fp, gdc, bake]
)

