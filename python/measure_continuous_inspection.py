""" Measure continously, plot ascii spectrum in between
    Input: (total_measurement_time,splittime,triggervalue)
    Output: list of charges """

import os
import shutil
import sys
from subprocess import call
from subprocess import Popen
import nflmca
import numpy as np


def take_measurement(totaltime,splittime,triggervalue):

    # measure command -- CHANGE
    callstring ="./acquisition -t 3 -v " + str(triggervalue) + " -p 32 -l 384 -f temp " + str(splittime)
    calllist = callstring.split(" ")

    # start first acquisition process
    devnull = open(os.devnull, 'wb') # use this in python < 3.3
    # python >= 3.3 has subprocess.DEVNULL
    print "Start Measurement process"
    process = Popen(calllist, stdout=devnull, stderr=devnull)

    # loop through left steps
    steps = totaltime / splittime
    totaldata = np.array([])
    scaling = 1.0
    for i in range(steps - 1):
        # wait for process to be finished
        count = 0
        while (process.poll() != 0):
            count += 1
        print "Measurement process done"
        # copy file
        shutil.copy("temp.txt", "read.txt")

        # start new process
        print "Start new measurement process"
        process = Popen(calllist, stdout=devnull, stderr=devnull)
    
        # readout step file
        a = nflmca.read_acquistion_file("read.txt", negativepulse = True, binary = False)
        a = a[1]
        a = a[(a > 0)]
        totaldata = np.concatenate((totaldata, a))
        # add file to long list
                            
    return totaldata
