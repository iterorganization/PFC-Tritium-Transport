from iter_scenarios.benchmark import scenario as benchmark_scenario
from iter_scenarios.clean_every_2_days import scenario as clean_every_2_scenario
from iter_scenarios.clean_every_5_days import scenario as clean_every_5_scenario
from iter_scenarios.no_glow import scenario as no_glow_scenario
from iter_scenarios.do_nothing import scenario as do_nothing_scenario
from iter_scenarios.just_glow import scenario as just_glow_scenario

from hisp.scenario import Pulse

def test_scenario_times(scenario_list):
    """Tests that all scenarios are 21 days exactly.
    """
    expected_scenario_total_time = 21*24*3600 # 21 days in seconds

    for scenario in scenario_list: 
        total_time = 0.0
        for pulse in scenario.pulses: 
            total_time += pulse.total_duration * pulse.nb_pulses
    
        assert expected_scenario_total_time == total_time

    print("All tests have passed!")

if __name__=="__main__": 
    my_scenarios = [benchmark_scenario, clean_every_2_scenario, clean_every_5_scenario, no_glow_scenario, do_nothing_scenario, just_glow_scenario]
    test_scenario_times(my_scenarios)