from hisp.scenario import Scenario, Pulse

from iter_scenarios.benchmark import icwc, risp5, risp1, bake

############## BENCHMARK NO GLOW SCENARIO ##############
fp = Pulse(
    pulse_type="FP",
    nb_pulses=10,
    ramp_up=429,
    steady_state=650,
    ramp_down=455,
    waiting=3600,
    tritium_fraction=0.5,
)

risp1_longer_wait = Pulse(
    pulse_type="RISP",
    nb_pulses=1,
    ramp_up=10,
    steady_state=250,
    ramp_down=10,
    waiting=risp1.waiting + 2 * 24 * 3600, # risp1 waiting plus two days nothing
    tritium_fraction=0.0,
)
scenario = Scenario(pulses=[fp, icwc, risp5, risp1, icwc, risp5, risp1_longer_wait, bake])