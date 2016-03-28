"""Measures simple spectrum, reads it after that and builds integrated values. At the end, plot an ASCII representation of the spectrum."""

import os
import shutil
from subprocess import call
from subprocess import Popen
import nflmca
import numpy as np
import hv

hvcontrol = hv.hv()
hvcontrol.enable()
hvcontrol.setVoltage(1000, ramp = True)

measurementtime = 300
outputfile = "out1"

# measure
callstring ="./acquisition -t 3 -u -0.4 -p 32 -l 384 -f " + outputfile + " " + str(measurementtime)
calllist = callstring.split(" ")

call(calllist)

hvcontrol.setVoltage(0, ramp = True)
hvcontrol.disable()

# readout step file
a = nflmca.readacquistionfile(outputfile + ".txt", negativepulse = True, binary = False)
a = a[1]
a = a[(a > 0)]

# get current rows
rows, columns = os.popen('stty size', 'r').read().split()
rows = int(rows) - 4 # leave some space
columns = int(columns)

# plot
nflmca.asciispectrum(a, rows, columns, 1)
                            
np.savetxt(outputfile + "-integrals.txt", a)
