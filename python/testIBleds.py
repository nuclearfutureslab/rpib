import numpy as np
import gpio
import time

# Ready LED - stays on the whole time, but turn off if a busy LED turns on
REA = ("A", 0)
gpio.init_output(*REA)
gpio.output(*REA, level = gpio.LOW)
# HV LED - turns on when HV is ramped on 
HVL = ("N", 0)
gpio.init_output(*HVL)
gpio.output(*HVL, level = gpio.LOW)
# Calibrate busy LED - on during the calibration process
BUC = ("A", 1)
gpio.init_output(*BUC)
gpio.output(*BUC, level = gpio.LOW)
# Calibration LED - turns on when calibration is complete
CAL = ("N", 1)
gpio.init_output(*CAL) 
gpio.output(*CAL, level = gpio.LOW)
# Acquire busy LED - on during data acquisition process
BUA = ("A", 2)
gpio.init_output(*BUA)
gpio.output(*BUA, level = gpio.LOW)
# Template 1 acquired LED - turns on once T1 is acquired
A1L = ("N", 2)
gpio.init_output(*A1L)
gpio.output(*A1L, level = gpio.LOW)
# Template 2 acquired LED - turns on once T2 is acquired
A2L = ("N", 4)
gpio.init_output(*A2L)
gpio.output(*A2L, level = gpio.LOW)
# Template 3 acquired LED - turns on once T3 is acquired
A3L = ("N", 3)
gpio.init_output(*A3L)
gpio.output(*A3L, level = gpio.LOW)
# Inspection Busy LED - turns on when inspection code is running
BUI = ("A", 3)
gpio.init_output(*BUI)
gpio.output(*BUI, level = gpio.LOW)
# Match Template 1 - turns on if match with T1
T1M = ("P", 5)
gpio.init_output(*T1M)
gpio.output(*T1M, level = gpio.LOW)
# Match Template 2 - turns on if match with T2
T2M = ("N", 5)
gpio.init_output(*T2M)
gpio.output(*T2M, level = gpio.LOW)
# Match Template 3 - turns on if match with T3
T3M = ("P", 6)
gpio.init_output(*T3M)
gpio.output(*T3M, level = gpio.LOW)
# Mismatch - turns on if no match with all three templates
MML = ("N", 6)
gpio.init_output(*MML)
gpio.output(*MML, level = gpio.LOW)

while True:
    print("Ready")
    gpio.output(*REA, level = gpio.HIGH)
    raw_input("Press Enter to continue...")
    gpio.output(*REA, level = gpio.LOW)

    print("HV")
    gpio.output(*HVL, level = gpio.HIGH)
    raw_input("Press Enter to continue...")
    gpio.output(*HVL, level = gpio.LOW)

    print("Calibration Busy")
    gpio.output(*BUC, level = gpio.HIGH)
    raw_input("Press Enter to continue...")
    gpio.output(*BUC, level = gpio.LOW)

    print("Calibration Done")
    gpio.output(*CAL, level = gpio.HIGH)
    raw_input("Press Enter to continue...")
    gpio.output(*CAL, level = gpio.LOW)

    print("Acquire Busy")
    gpio.output(*BUA, level = gpio.HIGH)
    raw_input("Press Enter to continue...")
    gpio.output(*BUA, level = gpio.LOW)
    
    print("Template 1 present")
    gpio.output(*A1L, level = gpio.HIGH)
    raw_input("Press Enter to continue...")
    gpio.output(*A1L, level = gpio.LOW)

    print("Template 2 present")
    gpio.output(*A2L, level = gpio.HIGH)
    raw_input("Press Enter to continue...")
    gpio.output(*A2L, level = gpio.LOW)

    print("Template 3 present")
    gpio.output(*A3L, level = gpio.HIGH)
    raw_input("Press Enter to continue...")
    gpio.output(*A3L, level = gpio.LOW)

    print("Inspect busy")
    gpio.output(*BUI, level = gpio.HIGH)
    raw_input("Press Enter to continue...")
    gpio.output(*BUI, level = gpio.LOW)

    print("Template 1 Match")
    gpio.output(*T1M, level = gpio.HIGH)
    raw_input("Press Enter to continue...")
    gpio.output(*T1M, level = gpio.LOW)

    print("Template 2 Match")
    gpio.output(*T2M, level = gpio.HIGH)
    raw_input("Press Enter to continue...")
    gpio.output(*T2M, level = gpio.LOW)

    print("Template 3 Match")
    gpio.output(*T3M, level = gpio.HIGH)
    raw_input("Press Enter to continue...")
    gpio.output(*T3M, level = gpio.LOW)

    print("Mismatch!")
    gpio.output(*MML, level = gpio.HIGH)
    raw_input("Press Enter to continue...")
    gpio.output(*MML, level = gpio.LOW)
