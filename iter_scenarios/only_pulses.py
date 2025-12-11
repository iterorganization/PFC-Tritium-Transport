from hisp.scenario import Scenario, Pulse

from iter_scenarios.benchmark import gdc, bake, icwc
from iter_scenarios.do_nothing import fp
from iter_scenarios.clean_every_5_days import risp6, icwc_long

# fp = Pulse(
#     pulse_type="FP",
#     nb_pulses=2,
#     ramp_up=429,
#     steady_state=650,
#     ramp_down=455,
#     waiting=84866,
#     tritium_fraction=0.5,
# )
risp3 = Pulse(
    pulse_type="RISP",
    nb_pulses=3,
    ramp_up=10,
    steady_state=250,
    ramp_down=10,
    waiting=1530,
    tritium_fraction=0.0,
)
fp1_end_day = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=429,
    steady_state=650,
    ramp_down=455,
    waiting=77666,
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
icwc_end_day = Pulse(
    pulse_type="ICWC",
    nb_pulses=1,
    ramp_up=10,
    steady_state=280,  # half the time of regular icwc
    ramp_down=10,
    waiting=73500,  # icwc waiting takes us to next day
    tritium_fraction=0.0,
)

scenario = Scenario(
    pulses=[
        fp,
        #icwc,
        fp1_end_day,
        fp1_start_day,
        #icwc_end_day,
        fp,
        #icwc,
        fp1_end_day,
        fp1_start_day,
        #icwc_end_day,
        fp,
        #icwc_long,
        #icwc_long,
        #gdc,
        bake,
        fp,
        #icwc,
        fp1_end_day,
        fp1_start_day,
        #icwc_end_day,
        fp,
        #icwc,
        fp1_end_day,
        fp1_start_day,
        #icwc_end_day,
        fp,
        #icwc_long,
        #icwc_long,
        #gdc,
        bake,
        fp,
        #icwc,
        fp1_end_day,
        fp1_start_day,
        #icwc_end_day,
        fp,
        #icwc,
        fp1_end_day,
        fp1_start_day,
        #icwc_end_day,
        fp,
        #icwc_long,
        #icwc_long,
        #gdc,
        bake,
        fp,
        #icwc,
        fp1_end_day,
        fp1_start_day,
        #icwc_end_day,
        fp,
        fp1_end_day,
        fp1_start_day,
        fp,
        #gdc,
        bake,
    ]
)