from hisp.scenario import Scenario, Pulse

fp = Pulse(
    pulse_type="FP",
    nb_pulses=9,
    ramp_up=429,
    steady_state=650,
    ramp_down=455,
    waiting=84866,
    tritium_fraction=0.5,
)

fp_do_nothing = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=429,
    steady_state=650,
    ramp_down=455,
    waiting=fp.waiting + 4 * 24 * 3600,
    tritium_fraction=0.5,
)
scenario = Scenario(pulses=[fp, fp_do_nothing])
