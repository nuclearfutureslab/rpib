""" Measure continously, plot ascii spectrum in between """

import os
import shutil
import sys
from subprocess import call
from subprocess import Popen
import nflmca
import numpy as np
import hv

### Usage:
#   asciimeasure.py <totaltime> <splittime> <triggervalue> <outputfilename>
if(len(sys.argv) < 5 or len(sys.argv) > 6):
    print "Usage: measure-continous-new.py <totaltime> <splittime> <triggervalue> <outputfilename>"
    print "No option can be omitted!"
    print "Triggervalue should be between -8192 and 8192"
    exit(-1)
totaltime = int(sys.argv[1])
splittime = int(sys.argv[2])
triggervalue = float(sys.argv[3])
outputfilename = sys.argv[4]
noplot = False
if(len(sys.argv)== 6):
    if(sys.argv[5] == "noplot"):
        noplot = True

hvcontrol = hv.hv()
hvcontrol.enable()
hvcontrol.set_voltage(1000, ramp = True)

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

    if not noplot:
        # get current rows
        rows, columns = os.popen('stty size', 'r').read().split()
        rows = int(rows) - 4 # leave some space
        columns = int(columns)

        # plot
        scaling = nflmca.ascii_spectrum(totaldata, rows, columns, scaling)
                            
hvcontrol.set_voltage(0, ramp = True)
np.savetxt(outputfilename + ".txt", totaldata)
hvcontrol.disable()
