# 5FP DT
# 1FP DD, decrease fluxes and loads by 5
# 5FP DT
# 1FP DD, decrease fluxes and loads by 5
# GDC 1 day
# bake

from scenario import Scenario, Pulse

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

bake = Pulse(
    pulse_type="BAKE",
    nb_pulses=1,
    ramp_up=151200, # 5C degrees per hour; 42 hours total
    steady_state=345600,
    ramp_down=108000, # -7C per hour; 30 hours total
    waiting=11,  # HISP expects at least 10 s of waiting...
    tritium_fraction=0.0,
)

gdc = Pulse(
    pulse_type="GDC",
    nb_pulses=1,
    ramp_up=1,
    steady_state=172798,  # 2 day glow
    ramp_down=1,
    waiting=172800,  # 2 days waiting
    tritium_fraction=0.0,
)

scenario = Scenario(pulses=[fp, fp_d, fp, fp_d, gdc, bake])
