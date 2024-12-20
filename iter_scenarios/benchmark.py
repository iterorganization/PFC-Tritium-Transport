from hisp.scenario import Scenario, Pulse

# assumes first pulse begins at 6am on day one
# scenarios thus stretch from 6am day one to 6:00am day 15 (for the start of the next scenario)

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
    waiting=69830,
    tritium_fraction=0.0,
)
gdc = Pulse(
    pulse_type="GDC",
    nb_pulses=1,
    ramp_up=1,
    steady_state=86398,
    ramp_down=1,
    waiting=86400,
    tritium_fraction=0.0,
)


scenario = Scenario(
    pulses=[fp, icwc, risp5, risp1, icwc, risp5, risp1, gdc]
)

