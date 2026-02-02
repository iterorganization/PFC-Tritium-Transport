from scenario import Scenario, Pulse

# Reference baking pulse
bake = Pulse(
    pulse_type="BAKE",
    nb_pulses=1,
    ramp_up=151200,    # 5C degrees per hour; 42 hours total
    steady_state=345600,
    ramp_down=108000,   # -7C per hour; 30 hours total
    waiting=11,
    tritium_fraction=0.0,
)

# FPO 1, Pulse 1
fpo1_p1 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=60060,
    steady_state=91000,
    ramp_down=63700,
    waiting=504000,
    tritium_fraction=0.00,
    heat_scaling=0.33,
    flux_scaling=0.25,
)

# FPO 1, Pulse 2
fpo1_p2 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=60060,
    steady_state=91000,
    ramp_down=63700,
    waiting=504000,
    tritium_fraction=0.00,
    heat_scaling=0.67,
    flux_scaling=0.50,
)

# FPO 1, Pulse 3
fpo1_p3 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=11583,
    steady_state=17550,
    ramp_down=12285,
    waiting=97200,
    tritium_fraction=0.50,
    heat_scaling=0.33,
    flux_scaling=0.50,
)

# FPO 1, Pulse 4
fpo1_p4 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=4719,
    steady_state=7150,
    ramp_down=5005,
    waiting=39600,
    tritium_fraction=0.01,
    heat_scaling=0.17,
    flux_scaling=0.25,
)

# FPO 1, Pulse 5
fpo1_p5 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=5148,
    steady_state=7800,
    ramp_down=5460,
    waiting=43200,
    tritium_fraction=0.01,
    heat_scaling=0.34,
    flux_scaling=0.50,
)

# FPO 1, Pulse 6
fpo1_p6 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=5148,
    steady_state=7800,
    ramp_down=5460,
    waiting=43200,
    tritium_fraction=0.01,
    heat_scaling=0.20,
    flux_scaling=0.25,
)

# FPO 1, Pulse 7
fpo1_p7 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=10296,
    steady_state=15600,
    ramp_down=10920,
    waiting=86400,
    tritium_fraction=0.01,
    heat_scaling=0.40,
    flux_scaling=0.33,
)

# FPO 1, Pulse 8
fpo1_p8 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=21021,
    steady_state=31850,
    ramp_down=22295,
    waiting=176400,
    tritium_fraction=0.01,
    heat_scaling=0.60,
    flux_scaling=0.50,
)

# FPO 2, Pulse 9
fpo2_p9 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=5148,
    steady_state=7800,
    ramp_down=5460,
    waiting=43200,
    tritium_fraction=0.00,
    heat_scaling=0.33,
    flux_scaling=0.25,
)

# FPO 2, Pulse 10
fpo2_p10 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=5148,
    steady_state=7800,
    ramp_down=5460,
    waiting=43200,
    tritium_fraction=0.00,
    heat_scaling=0.67,
    flux_scaling=0.50,
)

# FPO 2, Pulse 11
fpo2_p11 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=59716,
    steady_state=90480,
    ramp_down=63335,
    waiting=501119,
    tritium_fraction=0.00,
    heat_scaling=0.67,
    flux_scaling=0.50,
)

# FPO 2, Pulse 12
fpo2_p12 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=6435,
    steady_state=9750,
    ramp_down=6825,
    waiting=54000,
    tritium_fraction=0.01,
    heat_scaling=0.40,
    flux_scaling=0.33,
)

# FPO 2, Pulse 13
fpo2_p13 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=9438,
    steady_state=14300,
    ramp_down=10010,
    waiting=79200,
    tritium_fraction=0.01,
    heat_scaling=0.53,
    flux_scaling=0.50,
)

# FPO 2, Pulse 14
fpo2_p14 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=2831,
    steady_state=4290,
    ramp_down=3003,
    waiting=23760,
    tritium_fraction=0.30,
    heat_scaling=0.41,
    flux_scaling=0.25,
)

# FPO 2, Pulse 15
fpo2_p15 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=3088,
    steady_state=4680,
    ramp_down=3276,
    waiting=25920,
    tritium_fraction=0.30,
    heat_scaling=0.58,
    flux_scaling=0.50,
)

# FPO 2, Pulse 16
fpo2_p16 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=14586,
    steady_state=22100,
    ramp_down=15470,
    waiting=122400,
    tritium_fraction=0.50,
    heat_scaling=0.41,
    flux_scaling=0.25,
)

# FPO 2, Pulse 17
fpo2_p17 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=14586,
    steady_state=22100,
    ramp_down=15470,
    waiting=122400,
    tritium_fraction=0.50,
    heat_scaling=0.58,
    flux_scaling=0.50,
)

# FPO 2, Pulse 18
fpo2_p18 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=7722,
    steady_state=11700,
    ramp_down=8190,
    waiting=64800,
    tritium_fraction=0.50,
    heat_scaling=0.58,
    flux_scaling=0.50,
)

# FPO 2, Pulse 19
fpo2_p19 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=22308,
    steady_state=33800,
    ramp_down=23660,
    waiting=187200,
    tritium_fraction=0.01,
    heat_scaling=0.54,
    flux_scaling=0.67,
)

# FPO 2, Pulse 20
fpo2_p20 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=27456,
    steady_state=41600,
    ramp_down=29120,
    waiting=230400,
    tritium_fraction=0.50,
    heat_scaling=0.51,
    flux_scaling=0.33,
)

# FPO 2, Pulse 21
fpo2_p21 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=27885,
    steady_state=42250,
    ramp_down=29575,
    waiting=234000,
    tritium_fraction=0.50,
    heat_scaling=0.70,
    flux_scaling=0.67,
)

# FPO 2, Pulse 22
fpo2_p22 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=7722,
    steady_state=11700,
    ramp_down=8190,
    waiting=64800,
    tritium_fraction=0.50,
    heat_scaling=0.70,
    flux_scaling=0.67,
)

# FPO 3, Pulse 23
fpo3_p23 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=5148,
    steady_state=7800,
    ramp_down=5460,
    waiting=43200,
    tritium_fraction=0.00,
    heat_scaling=0.33,
    flux_scaling=0.25,
)

# FPO 3, Pulse 24
fpo3_p24 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=5148,
    steady_state=7800,
    ramp_down=5460,
    waiting=43200,
    tritium_fraction=0.00,
    heat_scaling=0.67,
    flux_scaling=0.50,
)

# FPO 3, Pulse 25
fpo3_p25 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=59716,
    steady_state=90480,
    ramp_down=63335,
    waiting=501119,
    tritium_fraction=0.00,
    heat_scaling=0.67,
    flux_scaling=0.50,
)

# FPO 3, Pulse 26
fpo3_p26 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=22308,
    steady_state=33800,
    ramp_down=23660,
    waiting=187200,
    tritium_fraction=0.01,
    heat_scaling=0.61,
    flux_scaling=0.83,
)

# FPO 3, Pulse 27
fpo3_p27 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=22308,
    steady_state=33800,
    ramp_down=23660,
    waiting=187200,
    tritium_fraction=0.01,
    heat_scaling=0.61,
    flux_scaling=1.00,
)

# FPO 3, Pulse 28
fpo3_p28 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=10725,
    steady_state=16250,
    ramp_down=11375,
    waiting=90000,
    tritium_fraction=0.50,
    heat_scaling=0.81,
    flux_scaling=0.50,
)

# FPO 3, Pulse 29
fpo3_p29 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=10725,
    steady_state=16250,
    ramp_down=11375,
    waiting=90000,
    tritium_fraction=0.50,
    heat_scaling=1.03,
    flux_scaling=0.50,
)

# FPO 3, Pulse 30
fpo3_p30 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=16731,
    steady_state=25350,
    ramp_down=17745,
    waiting=140400,
    tritium_fraction=0.50,
    heat_scaling=0.93,
    flux_scaling=1.00,
)

# FPO 3, Pulse 31
fpo3_p31 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=16945,
    steady_state=25675,
    ramp_down=17972,
    waiting=142200,
    tritium_fraction=0.50,
    heat_scaling=1.00,
    flux_scaling=1.00,
)

# FPO 3, Pulse 32
fpo3_p32 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=7722,
    steady_state=11700,
    ramp_down=8190,
    waiting=64800,
    tritium_fraction=0.50,
    heat_scaling=1.00,
    flux_scaling=1.00,
)

# FPO 4, Pulse 33
fpo4_p33 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=5148,
    steady_state=7800,
    ramp_down=5460,
    waiting=43200,
    tritium_fraction=0.00,
    heat_scaling=0.33,
    flux_scaling=0.25,
)

# FPO 4, Pulse 34
fpo4_p34 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=5148,
    steady_state=7800,
    ramp_down=5460,
    waiting=43200,
    tritium_fraction=0.00,
    heat_scaling=0.67,
    flux_scaling=0.50,
)

# FPO 4, Pulse 35
fpo4_p35 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=98841,
    steady_state=149760,
    ramp_down=104832,
    waiting=829440,
    tritium_fraction=0.00,
    heat_scaling=0.67,
    flux_scaling=0.50,
)

# FPO 4, Pulse 36
fpo4_p36 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=140197,
    steady_state=212420,
    ramp_down=148694,
    waiting=1176480,
    tritium_fraction=0.01,
    heat_scaling=0.61,
    flux_scaling=1.00,
)

# FPO 4, Pulse 37
fpo4_p37 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=29343,
    steady_state=44460,
    ramp_down=31122,
    waiting=246240,
    tritium_fraction=0.50,
    heat_scaling=0.70,
    flux_scaling=0.50,
)

# FPO 4, Pulse 38
fpo4_p38 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=29343,
    steady_state=44460,
    ramp_down=31122,
    waiting=246240,
    tritium_fraction=0.50,
    heat_scaling=0.80,
    flux_scaling=1.00,
)

# FPO 4, Pulse 39
fpo4_p39 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=140197,
    steady_state=212420,
    ramp_down=148694,
    waiting=1176480,
    tritium_fraction=0.01,
    heat_scaling=0.61,
    flux_scaling=1.00,
)

# FPO 4, Pulse 40
fpo4_p40 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=29343,
    steady_state=44460,
    ramp_down=31122,
    waiting=246240,
    tritium_fraction=0.50,
    heat_scaling=0.70,
    flux_scaling=0.50,
)

# FPO 4, Pulse 41
fpo4_p41 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=29343,
    steady_state=44460,
    ramp_down=31122,
    waiting=246240,
    tritium_fraction=0.50,
    heat_scaling=0.80,
    flux_scaling=1.00,
)

# FPO 4, Pulse 42
fpo4_p42 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=140197,
    steady_state=212420,
    ramp_down=148694,
    waiting=1176480,
    tritium_fraction=0.01,
    heat_scaling=0.61,
    flux_scaling=1.00,
)

# FPO 4, Pulse 43
fpo4_p43 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=29343,
    steady_state=44460,
    ramp_down=31122,
    waiting=246240,
    tritium_fraction=0.50,
    heat_scaling=0.70,
    flux_scaling=0.50,
)

# FPO 4, Pulse 44
fpo4_p44 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=30973,
    steady_state=46930,
    ramp_down=32851,
    waiting=259920,
    tritium_fraction=0.50,
    heat_scaling=0.80,
    flux_scaling=1.00,
)

# FPO 5, Pulse 45
fpo5_p45 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=5148,
    steady_state=7800,
    ramp_down=5460,
    waiting=43200,
    tritium_fraction=0.00,
    heat_scaling=0.33,
    flux_scaling=0.25,
)

# FPO 5, Pulse 46
fpo5_p46 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=5148,
    steady_state=7800,
    ramp_down=5460,
    waiting=43200,
    tritium_fraction=0.00,
    heat_scaling=0.67,
    flux_scaling=0.50,
)

# FPO 5, Pulse 47
fpo5_p47 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=152380,
    steady_state=230880,
    ramp_down=161616,
    waiting=1278720,
    tritium_fraction=0.00,
    heat_scaling=0.67,
    flux_scaling=0.50,
)

# FPO 5, Pulse 48
fpo5_p48 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=257571,
    steady_state=390260,
    ramp_down=273182,
    waiting=2161440,
    tritium_fraction=0.01,
    heat_scaling=0.61,
    flux_scaling=1.00,
)

# FPO 5, Pulse 49
fpo5_p49 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=92921,
    steady_state=140790,
    ramp_down=98553,
    waiting=779760,
    tritium_fraction=0.50,
    heat_scaling=0.70,
    flux_scaling=0.50,
)

# FPO 5, Pulse 50
fpo5_p50 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=26083,
    steady_state=39520,
    ramp_down=27664,
    waiting=218880,
    tritium_fraction=0.50,
    heat_scaling=0.80,
    flux_scaling=1.00,
)

# FPO 5, Pulse 51
fpo5_p51 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=26083,
    steady_state=39520,
    ramp_down=27664,
    waiting=218880,
    tritium_fraction=0.50,
    heat_scaling=1.00,
    flux_scaling=1.00,
)

# FPO 5, Pulse 52
fpo5_p52 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=19562,
    steady_state=29640,
    ramp_down=20748,
    waiting=164160,
    tritium_fraction=0.50,
    heat_scaling=1.27,
    flux_scaling=1.00,
)

# FPO 5, Pulse 53
fpo5_p53 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=6336,
    steady_state=9600,
    ramp_down=6720,
    waiting=53169,
    tritium_fraction=0.50,
    heat_scaling=1.00,
    flux_scaling=1.00,
)

# FPO 5, Pulse 54
fpo5_p54 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=84126,
    steady_state=127465,
    ramp_down=89225,
    waiting=705960,
    tritium_fraction=0.01,
    heat_scaling=0.61,
    flux_scaling=1.00,
)

# FPO 5, Pulse 55
fpo5_p55 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=19008,
    steady_state=28800,
    ramp_down=20160,
    waiting=159507,
    tritium_fraction=0.50,
    heat_scaling=0.93,
    flux_scaling=0.50,
)

# FPO 5, Pulse 56
fpo5_p56 = Pulse(
    pulse_type="FP",
    nb_pulses=1,
    ramp_up=11088,
    steady_state=16800,
    ramp_down=11760,
    waiting=93046,
    tritium_fraction=0.50,
    heat_scaling=1.00,
    flux_scaling=1.00,
)

# Build scenario with baking after each FPO phase
scenario = Scenario(pulses=[
    # FPO 1
    fpo1_p1,
    fpo1_p2,
    fpo1_p3,
    fpo1_p4,
    fpo1_p5,
    fpo1_p6,
    fpo1_p7,
    fpo1_p8,
    bake,  # Baking after FPO 1
    # FPO 2
    fpo2_p9,
    fpo2_p10,
    fpo2_p11,
    fpo2_p12,
    fpo2_p13,
    fpo2_p14,
    fpo2_p15,
    fpo2_p16,
    fpo2_p17,
    fpo2_p18,
    fpo2_p19,
    fpo2_p20,
    fpo2_p21,
    fpo2_p22,
    bake,  # Baking after FPO 2
    # FPO 3
    fpo3_p23,
    fpo3_p24,
    fpo3_p25,
    fpo3_p26,
    fpo3_p27,
    fpo3_p28,
    fpo3_p29,
    fpo3_p30,
    fpo3_p31,
    fpo3_p32,
    bake,  # Baking after FPO 3
    # FPO 4
    fpo4_p33,
    fpo4_p34,
    fpo4_p35,
    fpo4_p36,
    fpo4_p37,
    fpo4_p38,
    fpo4_p39,
    fpo4_p40,
    fpo4_p41,
    fpo4_p42,
    fpo4_p43,
    fpo4_p44,
    bake,  # Baking after FPO 4
    # FPO 5
    fpo5_p45,
    fpo5_p46,
    fpo5_p47,
    fpo5_p48,
    fpo5_p49,
    fpo5_p50,
    fpo5_p51,
    fpo5_p52,
    fpo5_p53,
    fpo5_p54,
    fpo5_p55,
    fpo5_p56,
    bake,  # Baking after FPO 5
])