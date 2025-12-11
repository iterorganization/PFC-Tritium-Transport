from hisp.scenario import Scenario, Pulse

fp = Pulse(
    pulse_type="FP",
    nb_pulses=9,
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
cold_waiting = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=0,
    steady_state=0,
    ramp_down=0,
    waiting=15,
    tritium_fraction=0.0,
)
#scenario = Scenario(pulses=[cold_waiting,fp, fp_do_nothing, bake])
scenario = Scenario(pulses=[cold_waiting,fp])