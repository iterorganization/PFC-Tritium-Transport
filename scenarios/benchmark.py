from scenario import Pulse

# Standard benchmark pulses used by multiple scenario scripts

gdc = Pulse(
    pulse_type="GDC",
    nb_pulses=1,
    ramp_up=1,
    steady_state=172798,  # 2 day glow
    ramp_down=1,
    waiting=172800,  # 2 days waiting
    tritium_fraction=0.0,
)

bake = Pulse(
    pulse_type="BAKE",
    nb_pulses=1,
    ramp_up=151200, # 5C degrees per hour; 42 hours total
    steady_state=345600,
    ramp_down=108000, # -7C per hour; 30 hours total
    waiting=10000,  # HISP expects at least 10 s of waiting...
    tritium_fraction=0.0,)
