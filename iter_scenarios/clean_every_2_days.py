from hisp.scenario import Scenario, Pulse

from iter_scenarios.clean_every_5_days import gdc, icwc_long, risp6

fp = Pulse(
    pulse_type="FP",
    nb_pulses=2,
    ramp_up=429,
    steady_state=650,
    ramp_down=455,
    waiting=84866,
    tritium_fraction=0.5,
)
risp3 = Pulse(
    pulse_type="RISP",
    nb_pulses=3,
    ramp_up=10,
    steady_state=250,
    ramp_down=10,
    waiting=1530,
    tritium_fraction=0.0,
)
icwc_short = Pulse(
    pulse_type="ICWC",
    nb_pulses=1,
    ramp_up=50,
    steady_state=500,  # half the time of regular icwc
    ramp_down=50,
    waiting=30000,  # icwc waiting takes us to 16h for FP pulse
    tritium_fraction=0.0,
)
fp1_end_day = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=429,
    steady_state=650,
    ramp_down=455,
    waiting=48866,
    tritium_fraction=0.5,
)
fp1_start_day = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=429,
    steady_state=650,
    ramp_down=455,
    waiting=5666,
    tritium_fraction=0.5,
)
icwc_short_end_day = Pulse(
    pulse_type="ICWC",
    nb_pulses=1,
    ramp_up=50,
    steady_state=500,  # half the time of regular icwc
    ramp_down=50,
    waiting=73200,  # icwc waiting takes us to next day
    tritium_fraction=0.0,
)

scenario = Scenario(
    pulses=[
        fp,
        risp3,
        icwc_short,
        fp1_end_day,
        fp1_start_day,
        risp3,
        icwc_short_end_day,
        fp,
        risp3,
        icwc_short,
        fp1_end_day,
        fp1_start_day,
        risp3,
        icwc_short_end_day,
        fp,
        risp6,
        icwc_long,
        risp6,
        icwc_long,
        gdc,
    ]
)