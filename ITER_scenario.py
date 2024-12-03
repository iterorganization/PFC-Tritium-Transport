from hisp.scenario import Scenario, Pulse

############## BENCHMARK SCENARIO ##############
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
benchmark_scenario = Scenario(pulses=[fp, icwc, risp5, risp1, icwc, risp5, risp1, gdc])

############## BENCHMARK NO GLOW SCENARIO ##############
risp1_longer_wait = Pulse(
    pulse_type="RISP",
    nb_pulses=1,
    ramp_up=10,
    steady_state=250,
    ramp_down=10,
    waiting=242730,  # risp1 waiting plus two days nothing
    tritium_fraction=0.0,
)
benchmark_no_glow_scenario = Scenario(
    pulses=[fp, icwc, risp5, risp1, icwc, risp5, risp1_longer_wait]
)

############## DO NOTHING SCENARIO ##############
fp_do_nothing = Pulse(
    pulse_type="FP",
    nb_pulses=10,
    ramp_up=429,
    steady_state=650,
    ramp_down=455,
    waiting=430466,  # fp waiting time plus 4 days of nothing
    tritium_fraction=0.5,
)
do_nothing_scenario = Scenario(pulses=[fp_do_nothing])

############## CLEAN EVERY 5 DAYS SCENARIO ##############
fp = Pulse(
    pulse_type="FP",
    nb_pulses=5,
    ramp_up=429,
    steady_state=650,
    ramp_down=455,
    waiting=84866,
    tritium_fraction=0.5,
)
risp6 = Pulse(
    pulse_type="RISP",
    nb_pulses=6,
    ramp_up=10,
    steady_state=250,
    ramp_down=10,
    waiting=1530,
    tritium_fraction=0.0,
)
icwc_long = Pulse(
    pulse_type="ICWC",
    nb_pulses=1,
    ramp_up=50,
    steady_state=1200,
    ramp_down=50,
    waiting=74300,  # icwc waiting plus rest of day
    tritium_fraction=0.0,
)
clean_every_5_scenario = Scenario(
    pulses=[fp, risp6, icwc_long, fp, risp6, icwc_long, gdc]
)

############## CLEAN EVERY 2 DAYS SCENARIO ##############
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
fp1_start_day = Pulse(
    pulse_type="FP",
    nb_pulses=2,
    ramp_up=429,
    steady_state=650,
    ramp_down=455,
    waiting=5666,
    tritium_fraction=0.5,
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
icwc_short_end_day = Pulse(
    pulse_type="ICWC",
    nb_pulses=1,
    ramp_up=50,
    steady_state=500,  # half the time of regular icwc
    ramp_down=50,
    waiting=73200,  # icwc waiting takes us to next day
    tritium_fraction=0.0,
)
clean_every_2_scenario = Scenario(
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
        gdc,
    ]
)
