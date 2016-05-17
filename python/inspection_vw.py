#INFORMATION BARRIER CODE

import numpy as np
import hvcalibrate as hvc
import gpio
import hv
import time
import os
import shutil
import sys
import os.path
import measure_continuous_inspection as meas
hvcontrol = hv.hv()

#_______________________________________________________________________
#SETTING INITIAL PARAMETERS
#_______________________________________________________________________
# MEASUREMENT ROUTINE
# total time for one measurement, currently both for calibration, template acqusition and sample
meastime = 600
# to optimize resources, the data acquisition is split into several steps of length splittime
splittime = 30
# the value at which the Red Pitaya triggers and records a pulse
triggervalue = 1

# TEMPLATE ACQUISITION
# the minimum number of counts that acquired templates must have after the measurement to accept them
min_counts = 50000

# INSPECTION
# the difference between a sample's and a template's total counts must be less than
# tot_counts_threshold * template's total counts to proceed with the KS-test.
tot_counts_threshold = 0.1
# samples are accepted as a match if their maximum KS-distance to a template 
# is smaller than this value and if  they have passed the total gamma counts test.
cdf_threshold = .015

#_______________________________________________________________________
#DEFINE A FUNCTION TO CONVERT OUR DATA (LIST OF CHARGES) TO
#A LIST OF ENERGIES, AND BINS THEM - CONSIDERING ENERGIES UP TO
#2500 KEV
#_______________________________________________________________________
def data_set_prep(curve_fit_parameters, comparison_data):

    #convert the comparison data (templates and sample) to energies
    energies = hvc.getenergies(comparison_data, curve_fit_parameters)
    #bin our energies
    energy_list = np.linspace(1, 2500, 2500) #considering up to 2500 keV
    spectrum_count = np.digitize(energies, energy_list)
    spectrum = np.bincount(spectrum_count, minlength = 2500)
    #"dump" out the last bin, because it will hold the excess energies > 2500keV
    spectrum = spectrum[:(len(spectrum)-1)]
    #convert all values to floats for later analysis
    spectrum = np.array(spectrum).astype('float')
    return spectrum

#_______________________________________________________________________
#DEFINE A FUNCTION THAT RETURNS THE CUMULATIVE DISTRIBUTION FUNCTION
#FOR A 1D ARRAY OF BINNED ENERGIES (note: the CDF is a 1D array, where
#the index indicates the energy, and each array element is the
#cumulative probability at the respective energy)
#_______________________________________________________________________
def make_cdf(dataset):
    
    return [ sum(dataset[0:idx+1]) / sum(dataset) for idx in range(len(dataset)) ]

#_______________________________________________________________________
#DEFINE A FUNCTION TO RUN THE CDF DISTANCE TEST
#TAKES IN ARRAY OF BINNED ENERGIES, GENERATES CDF, AND COMPARES THE TWO,
#RETURNING THE MAXIMUM DIFFERENCE
#_______________________________________________________________________
def cdf_test(dataset1, dataset2):
    
    cdf1 = make_cdf(dataset1)
    cdf2 = make_cdf(dataset2)

    maximum_distance = 0.0
    for i in range(0, len(dataset1)):
        distance = abs(cdf1[i] - cdf2[i])
        if distance > maximum_distance:
            maximum_distance = distance

    return maximum_distance

#_______________________________________________________________________
#DEFINE A FUNCTION THAT WILL RETURN WHETHER OR NOT WE HAVE A MATCH
#WITH AN INDIVIDUAL TEMPLATE - READS IN ARRAYS OF BINNED ENERGIES
#_______________________________________________________________________
def match(template_A, template_B, template_C, sample):   
    
    #assesses total count differences. Factor can be changed of course.
    if abs(sum(template_A)-sum(sample)) < tot_counts_threshold*sum(template_A):
        diff_A_test = True
        print "The sample passed the template_A total count test."
    else:
        diff_A_test = False
        print "The sample failed the template_A total count test."
        
    if abs(sum(template_B)-sum(sample)) < tot_counts_threshold*sum(template_B):
        diff_B_test = True
        print "The sample passed the template_B total count test."
    else:
        diff_B_test = False
        print "The sample failed the template_B total count test."
        
    if abs(sum(template_C)-sum(sample)) < tot_counts_threshold*sum(template_C):
        diff_C_test = True
        print "The sample passed the template_C total count test."
    else:
        diff_C_test = False
        print "The sample failed the template_C total count test."
    
    # und dass die total counts passen
    # falls kein template vorliegt oder total counts nicht passen,
    # ist KS-Abstand 1, und damit maximal. No match, da > 0.15
    if np.any(template_A) == True and diff_A_test == True:
        cdf_test_result_A = cdf_test(template_A, sample)
        print "The KS distance to template A is " + str(cdf_test_result_A)
    else:
        cdf_test_result_A = 1
    if np.any(template_B) == True and diff_B_test == True:
        cdf_test_result_B = cdf_test(template_B, sample)
        print "The KS distance to template B is " + str(cdf_test_result_B)
    else: 
        cdf_test_result_B = 1
    if np.any(template_C) == True and diff_C_test == True:
        cdf_test_result_C = cdf_test(template_C, sample)
        print "The KS distance to template C is " + str(cdf_test_result_C)
    else: 
        cdf_test_result_C = 1

    #find the minimum deviation between the sample and the three templates
    #index 0 = template_A, index 1 = template_B, index 2 = template_C
    distances = np.array([cdf_test_result_A,cdf_test_result_B,cdf_test_result_C])
    minimum = min(distances)
    minimum_index = distances.argmin()
    return (minimum_index,minimum)

#_______________________________________________________________________
#INITIALIZING OUR LEDs
#_______________________________________________________________________

gpio.init_output("A", 0) #ready LED - stayS on the whole time, but turn off if a busy LED turns on
gpio.init_output("N", 0) #turns on when HV is ramped up
gpio.init_output("A", 1) #Calibrate busy LED - on while the calibration process is running
gpio.init_output("N", 1) #turns on if there is a successful calibration (note: unsuccessful calibration = no LED)
gpio.init_output("A", 2) #Acquire busy LED - on during data acquisition process
gpio.init_output("N", 2) #Template A acquired LED - turns on once TA is present
gpio.init_output("N", 3) #Template B acquired LED - turns on once TB is present
gpio.init_output("N", 4) #Template C acquired LED - turns on once TC is present
gpio.init_output("A", 3) #turns on while inspection code is running (inspection busy LED)
gpio.init_output("P", 5) #turns on if match with TA
gpio.init_output("N", 5) #turns on if match with TB
gpio.init_output("P", 6) #turns on if match with TC
gpio.init_output("N", 6) #turns on if no match with all three templates

#Turn all of the LEDs off to begin with, except for the general ready LED 
gpio.output("A", 0, gpio.HIGH) #ready LED - stay on the whole time, but turn off if a busy LED turns on
gpio.output("N", 0, gpio.LOW) #turns on when HV is ramped on 
gpio.output("A", 1, gpio.LOW) #Calibrate busy LED - on during the calibration process
gpio.output("N", 1, gpio.LOW) #turns on when calibration is complete
gpio.output("A", 2, gpio.LOW) #Acquire busy LED - on during data acquisition process
gpio.output("N", 2, gpio.LOW) #Template A acquired LED - turns on once TA is acquired
gpio.output("N", 3, gpio.LOW) #Template B acquired LED - turns on once TB is acquired
gpio.output("N", 4, gpio.LOW) #Template C acquired LED - turns on once TC is acquired
gpio.output("A", 3, gpio.LOW) #turns on when inspection code is running
gpio.output("P", 5, gpio.LOW) #turns on if match with TA
gpio.output("N", 5, gpio.LOW) #turns on if match with TB
gpio.output("P", 6, gpio.LOW) #turns on if match with TC
gpio.output("N", 6, gpio.LOW) #turns on if no match with all three templates

# This initialization is required to successfully perform the inspection function
# match(template_A, template_B, template_C, sample), when not all templates
# are recorded.

#________________________________________________________________________
#INITIALIZING OUR BUTTONS
#________________________________________________________________________
gpio.init_input("P", 0) #HV button, ramps up HV if down, ramps HV down if up
gpio.init_input("P", 1) #calibrate button, runs calibration function
gpio.init_input("P", 2) #acquires template A
gpio.init_input("P", 3) #acquires template B
gpio.init_input("P", 4) #acquires template C
gpio.init_input("N", 7) #inspect button, runs inspection function
#_________________________________________________________________________
#THE GRAND LOOP BEGINS

hv_status = 0
calibrated = 0
templatepresent = 0

#turn the ready LED on
gpio.output("A", 0, gpio.HIGH)
# turn other analog LEDs off
gpio.output("A", 1, gpio.LOW)
gpio.output("A", 2, gpio.LOW)
gpio.output("A", 3, gpio.LOW)

while 1:

#_______________________________________________________________________
#TURN THE MACHINE ON - press the high voltage button
#_______________________________________________________________________

    if  gpio.input("P", 0) == gpio.LOW and hv_status == 0:
        
        #turn the ready LED off
        gpio.output("A", 0, gpio.LOW)
        a = 0
        led = 1
        gpio.output("N", 0, gpio.HIGH) #high voltage LED button on 
        while(a < 30):
            a += 1
            time.sleep(0.1)
            if led == 1:
                led = 0
                gpio.output("N", 0, gpio.LOW) #high voltage LED button ff
            else:
                led = 1
                gpio.output("N", 0, gpio.HIGH) #high voltage LED button ff
        hv_status = 1
        gpio.output("N", 0, gpio.HIGH) #high voltage LED button on 
        gpio.output("A", 0, gpio.HIGH)
#_______________________________________________________________________
#TURN THE MACHINE OFF - press the high voltage button before powering down
#to turn off the high voltage 
#_______________________________________________________________________
    if  gpio.input("P", 0) == gpio.LOW and hv_status == 1:
        
        # #turn the ready LED off
        #gpio.output("A", 0, gpio.LOW)
        gpio.output("N", 1, gpio.LOW) #Calibrated LED
        #turn off any potential match LEDs that may be on 
        gpio.output("P", 5, gpio.LOW)
        gpio.output("N", 5, gpio.LOW)
        gpio.output("P", 6, gpio.LOW)
        gpio.output("N", 6, gpio.LOW)
        
        # hvcontrol.set_voltage(0, ramp = True)
        # hvcontrol.disable()
        hv_status = 0

        #turn appropriate LEDs off
        gpio.output("N", 0, gpio.LOW) #HV LED
        #gpio.output("A", 0, gpio.HIGH) #general ready LED on
        
#__________________________________________________________________________
#CALIBRATION PORTION OF THE RUN
#__________________________________________________________________________
    #if the calibration button is pressed and HV is on
        
    if  gpio.input("P", 1) == gpio.LOW and hv_status == 1: 
        
        #turn the ready LED off
        gpio.output("A", 0, gpio.LOW)
        #turn the calibration LED off and busy with calibration LED on
        gpio.output("N", 1, gpio.LOW)
        gpio.output("A", 1, gpio.HIGH)
        #turn all Match LEDs off
        gpio.output("P", 5, gpio.LOW)
        gpio.output("N", 5, gpio.LOW)
        gpio.output("Pp", 6, gpio.LOW)
        gpio.output("N", 6, gpio.LOW)
        
        time.sleep(3)
        gpio.output("N", 1, gpio.HIGH)
        calibrated = 1
        
        #turn the busy with calibration LED off
        gpio.output("A", 1, gpio.LOW)
        #turn the general ready LED back on
        gpio.output("A", 0, gpio.HIGH)

#_________________________________________________________________________
#ACQUISITION OF TEMPLATES
#_________________________________________________________________________
#Template A
    #if the acquire TA button is on, and HV is on and the calibrated LED button is on
    if  gpio.input("P", 2) == gpio.LOW and hv_status == 1 and calibrated == 1:
        
        #turn the general ready LED off
        gpio.output("A", 0, gpio.LOW)
        #turn the busy with acquisition LED on
        gpio.output("A", 2, gpio.HIGH)
        #turn all 4 match LEDs off
        gpio.output("P", 5, gpio.LOW)
        gpio.output("N", 5, gpio.LOW)
        gpio.output("P", 6, gpio.LOW)
        gpio.output("N", 6, gpio.LOW)
        # turn template A present LED off
        gpio.output("N", 2, gpio.LOW)
        
        time.sleep(5)
        gpio.output("N", 2, gpio.HIGH) #Template A acquired LED - turns on once TA is acquired
        templatepresent = 1
        
        #turn the busy with acquisition LED off
        gpio.output("A", 2, gpio.LOW)
        #turn the general ready LED back on
        gpio.output("A", 0, gpio.HIGH)

#Template B
    #if the acquire TB button is on, HV is on and the calibrated LED button is on
    if  gpio.input("P", 3) == gpio.LOW and hv_status == 1 and calibrated == 1:
        
        #turn the general ready LED off
        gpio.output("A", 0, gpio.LOW)
        #turn the busy with acquisition LED on
        gpio.output("A", 2, gpio.HIGH)
        #turn all 4 match LEDs off
        gpio.output("P", 5, gpio.LOW)
        gpio.output("N", 5, gpio.LOW)
        gpio.output("P", 6, gpio.LOW)
        gpio.output("N", 6, gpio.LOW)
        # turn template B present LED off
        
        time.sleep(5)
        gpio.output("N", 4, gpio.HIGH) #Template C acquired LED - turns on once TC is acq       gpio.output("N", )
        templatepresent = 1
        #turn the busy with acquisition LED off
        gpio.output("A", 2, gpio.LOW)
        #turn the general ready LED back on
        gpio.output("A", 0, gpio.HIGH)

#Template C
    #if the acquire TC button is on, HV is on and the calibrated LED button is on
    if  gpio.input("P", 4) == gpio.LOW and hv_status == 1 and calibrated == 1:

        gpio.output("A", 2, gpio.HIGH)
        time.sleep(5)
        templatepresent = 1
        gpio.output("N", 3, gpio.HIGH)
        #turn the busy with acquisition LED off
        gpio.output("A", 2, gpio.LOW)
        #turn the general ready LED back on
        gpio.output("A", 0, gpio.HIGH)
        
#________________________________________________________________________
#INSPECTION PORTION
#________________________________________________________________________
    # we want the inspect button to be pressed
    # HV and the successful calibration LED to be on as well
    # and at least one of the templates present
    if  gpio.input("N",7)==gpio.LOW and hv_status == 1 and templatepresent == 1:
        
        #turn the general ready LED off
        gpio.output("A", 0, gpio.LOW)
        #turn the busy with inspection LED on
        gpio.output("A", 3, gpio.HIGH)
        #turn all 4 match LEDs off
        gpio.output("P", 5, gpio.LOW)
        gpio.output("N", 5, gpio.LOW)
        gpio.output("P", 6, gpio.LOW)
        gpio.output("N", 6, gpio.LOW)

        time.sleep(5)
        
        gpio.output("P", 5, gpio.HIGH)
        gpio.output("N", 5, gpio.HIGH)
        gpio.output("P", 6, gpio.HIGH)
        gpio.output("N", 6, gpio.HIGH)
        
        #turn the busy with inspection LED off
        gpio.output("A", 3, gpio.LOW)
        #turn the general ready LED on
        gpio.output("A", 0, gpio.HIGH)
