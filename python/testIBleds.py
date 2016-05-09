import numpy as np
import gpio
import time

gpio.init_output("A", 0) #ready LED - stay on the whole time, but turn off if a busy LED turns on
gpio.init_output("N", 0) #turns on when HV is ramped on 
gpio.init_output("A", 1) #Calibrate busy LED - on during the calibration process
gpio.init_output("N", 1) #turns on when calibration is complete
gpio.init_output("A", 2) #Acquire busy LED - on during data acquisition process
gpio.init_output("N", 2) #Template A acquired LED - turns on once TA is acquired
gpio.init_output("N", 3) #Template B acquired LED - turns on once TB is acquired
gpio.init_output("N", 4) #Template C acquired LED - turns on once TC is acquired
gpio.init_output("A", 3) #turns on when inspection code is running
gpio.init_output("P", 5) #turns on if match with TA
gpio.init_output("N", 5) #turns on if match with TB
gpio.init_output("P", 6) #turns on if match with TC
gpio.init_output("N", 6) #turns on if no match with all three templates

analogstrings = [ "Ready", "Calibrate Busy", "Acquire Busy", "Inspection Busy"]
while True:
    print("Ready")
    gpio.output("A", 0, gpio.HIGH)
    raw_input("Press Enter to continue...")
    #input("Press Enter to continue...")
    raw_input("Press Enter to continue...")
    
    gpio.output("A", 0, gpio.LOW)

    print("HV")
    gpio.output("N", 0, gpio.HIGH)
    raw_input("Press Enter to continue...")
    
    gpio.output("N", 0, gpio.LOW)

    print("Calibration Busy")
    gpio.output("A", 1, gpio.HIGH)
    raw_input("Press Enter to continue...")
    
    gpio.output("A", 1, gpio.LOW)

    print("Calibration Done")
    gpio.output("N", 1, gpio.HIGH)
    raw_input("Press Enter to continue...")
    
    gpio.output("N", 1, gpio.LOW)

    print("Acquire Busy")
    gpio.output("A", 2, gpio.HIGH)
    raw_input("Press Enter to continue...")
    
    gpio.output("A", 2, gpio.LOW)

    print("Template 1 present")
    gpio.output("N", 2, gpio.HIGH)
    raw_input("Press Enter to continue...")
    
    gpio.output("N", 2, gpio.LOW)

    print("Template 2 present")
    gpio.output("N", 3, gpio.HIGH)
    raw_input("Press Enter to continue...")
    
    gpio.output("N", 3, gpio.LOW)

    print("Template 3 present")
    gpio.output("N", 4, gpio.HIGH)
    raw_input("Press Enter to continue...")
    
    gpio.output("N", 4, gpio.LOW)

    print("Inspect busy")
    gpio.output("A", 3, gpio.HIGH)
    raw_input("Press Enter to continue...")
    
    gpio.output("A", 3, gpio.LOW)

    print("Template 1 Match")
    gpio.output("P", 5, gpio.HIGH)
    raw_input("Press Enter to continue...")
    
    gpio.output("P", 5, gpio.LOW)

    print("Template 2 Match")
    gpio.output("N", 5, gpio.HIGH)
    raw_input("Press Enter to continue...")
    
    gpio.output("N", 5, gpio.LOW)

    print("Template 3 Match")
    gpio.output("P", 6, gpio.HIGH)
    raw_input("Press Enter to continue...")
    
    gpio.output("P", 6, gpio.LOW)

    print("Mismatch!")
    gpio.output("N", 6, gpio.HIGH)
    raw_input("Press Enter to continue...")
    
    gpio.output("N", 6, gpio.LOW)
