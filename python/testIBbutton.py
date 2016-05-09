import numpy as np
import gpio
import hv

#________________________________________________________________________
#INITIALIZING OUR BUTTONS
#________________________________________________________________________
gpio.init_input("P", 0) #HV button, ramps up HV
gpio.init_input("P", 1) #calibrate button, runs calibration function
gpio.init_input("P", 2) #reads in template A
gpio.init_input("P", 3) #reads in template B
gpio.init_input("P", 4) #reads in template C
gpio.init_input("N", 7) #inspect button, runs inspection function


while True:
    if gpio.input("P", 2) == 0:
        print "acquire 1"
    if gpio.input("P", 3) == 0:
        print "acquire 2"
    # if gpio.input("P", 4) == 0:
    #     print "acquire 3"
    if gpio.input("P", 0) == 0:
        print "hv button"
    if gpio.input("P", 1) == 0:
        print "calibrate button"
    if gpio.input("N", 7) == 0:
        print "inspect button"
