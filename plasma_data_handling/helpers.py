"""
Helper functions for plasma data handling and pulse processing.

These functions are used to create time-dependent boundary conditions
and process pulse profiles for FESTIM simulations.
"""

from scenario import Pulse

def periodic_pulse_function(current_time: float, pulse: Pulse, quant: str, value, value_off=343.0):
    """Creates bake function with ramp up rate and ramp down rate.

    Args:
        current_time (float): time within the pulse 
        pulse (Pulse): pulse of HISP Pulse class
        quant (str): 'heat' or 'flux' to determine which fraction to use
        value (float): steady-state value 
        value_off (float): value at t=0 and t=final time. 
    """

    if pulse.pulse_def == 'classic':
        if current_time == pulse.total_duration:
            return value_off
        elif current_time % pulse.total_duration < pulse.ramp_up:  # ramp up 
            return (value - value_off) / (pulse.ramp_up) * current_time + value_off  # y = mx + b, slope is temp/ramp up time
        elif current_time % pulse.total_duration < pulse.ramp_up + pulse.steady_state:  # steady state
            return value
        else:  # ramp down, waiting
            lower_value = value - (value - value_off)/pulse.ramp_down * (current_time - (pulse.ramp_up + pulse.steady_state))  # y = mx + b, slope is temp/ramp down time
            if lower_value >= value_off: 
                return lower_value
            else: 
                return value_off
    elif pulse.pulse_def == 'steps':
        time_prev = 0
        value_prev = value_off
        for r in range(len(pulse.steady_STATE)):
            if time_prev <= current_time < time_prev + pulse.transition[r]:
                return (value * pulse.fraction[r] - value_prev) / pulse.transition[r] * (current_time - time_prev) + value_prev
            elif time_prev + pulse.transition[r] <= current_time < time_prev + pulse.transition[r] + pulse.steady_STATE[r]:
                return value * pulse.fraction[r]
            value_prev = value * pulse.fraction[r]
            time_prev += pulse.transition[r] + pulse.steady_STATE[r]
        if time_prev <= current_time <= time_prev + pulse.transition[-1]:
            return (value_off - value_prev) / pulse.transition[-1] * (current_time - time_prev) + value_prev
        if current_time >= pulse.duration_no_waiting:
            return value_off
        if current_time == pulse.total_duration:
            return value_off
    elif pulse.pulse_def == 'timing':
        if quant == 'flux':
            if current_time == pulse.timing_flux[0]:
                return value * pulse.fraction_flux[0]
            for r in range(len(pulse.timing_flux)-1):
                if pulse.timing_flux[r] < current_time <= pulse.timing_flux[r+1]:
                    return value * (pulse.fraction_flux[r+1] - pulse.fraction_flux[r]) / (pulse.timing_flux[r+1] - pulse.timing_flux[r]) * (current_time - pulse.timing_flux[r]) + pulse.fraction_flux[r] * value
            if current_time > pulse.timing_flux[-1]: #waiting time
                return value_off
        elif quant == 'heat':
            if current_time == pulse.timing_heat[0]:
                return value * pulse.fraction_heat[0]
            for r in range(len(pulse.timing_heat)-1):
                if pulse.timing_heat[r] < current_time <= pulse.timing_heat[r+1]:
                    return value * (pulse.fraction_heat[r+1] - pulse.fraction_heat[r]) / (pulse.timing_heat[r+1] - pulse.timing_heat[r]) * (current_time - pulse.timing_heat[r]) + pulse.fraction_heat[r] * value
            if current_time > pulse.timing_heat[-1]: #waiting time
                return value_off

def periodic_step_function(x, period_on, period_total, value, value_off=0.0):
    """
    Creates a periodic step function with two periods.
    
    Args:
        x: time or position value
        period_on: duration when the function is "on"
        period_total: total period duration
        value: value when "on"
        value_off: value when "off"
    
    Returns:
        value or value_off depending on position in period
    """
    if x % period_total < period_on:
        return value
    else:
        return value_off
