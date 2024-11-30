from hisp.scenario import Scenario, Pulse

# benchmark scenario
fp = Pulse(
        pulse_type="FP",
        nb_pulses=10,
        ramp_up=429,
        steady_state=650,
        ramp_down=455,
        waiting=84866,
        tritium_fraction=0.5,
)
icwc = Pulse(
    pulse_type="ICWC",
    nb_pulses=1,
    ramp_up=50,
    steady_state=1200,
    ramp_down=50,
    waiting=6000,
    tritium_fraction=0.0,
)
risp5 = Pulse(
    pulse_type="RISP",
    nb_pulses=5,
    ramp_up=10,
    steady_state=250,
    ramp_down=10,
    waiting=1530,
    tritium_fraction=0.0,
)
risp1 = Pulse(
    pulse_type="RISP",
    nb_pulses=1,
    ramp_up=10,
    steady_state=250,
    ramp_down=10,
    waiting=69930,
    tritium_fraction=0.0,
)
gdc = Pulse(
    pulse_type="GDC",
    nb_pulses=1,
    ramp_up=1,
    steady_state=86398,
    ramp_down=1,
    waiting=64800,
    tritium_fraction=0.0,
)

my_scenario = Scenario(pulses=[fp, icwc, risp5, risp1, icwc, risp5, risp1, gdc])