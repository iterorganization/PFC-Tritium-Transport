from scenario import Scenario, Pulse

fp = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=429,
    steady_state=650,
    ramp_down=455,
    waiting=3600,
    tritium_fraction=0.5,
)
fp_do_nothing = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=429,
    steady_state=650,
    ramp_down=455,
    waiting=3600, 
    tritium_fraction=0.5,
    heat_scaling=0.33,
    flux_scaling=0.25,
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
scenario = Scenario(pulses=[fp_do_nothing,fp,bake])