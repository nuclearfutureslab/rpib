"""
Measures simple spectrum, reads it after that and builds integrated values.
At the end, plot an ASCII representation of the spectrum.
"""

import os
import shutil
from subprocess import call
from subprocess import Popen
import nflmca
import numpy as np
import hv

hvcontrol = hv.hv()
hvcontrol.enable()
hvcontrol.set_voltage(1000, ramp = True)

measurementtime = 300 # Time in seconds
outputfile = "out1"

# Measure spectrum

# Option -t: Trigger method (1-7); Method 1 forces immediate trigger
# Option -u: Trigger voltage must be calibrated/adjusted for current Red Pitaya

callstring ="./acquisition -t 3 -u -0.4 -p 32 -l 384 -f " + outputfile + " " + str(measurementtime)
calllist = callstring.split(" ")

call(calllist) # Execute command (C code); Python script will wait here

hvcontrol.set_voltage(0, ramp = True)
hvcontrol.disable()

# readout step file

a = nflmca.read_acquistion_file(outputfile + ".txt", negativepulse = True, binary = False)
a = a[1]
a = a[(a > 0)] # Drop negative integrals 

rows, columns = os.popen('stty size', 'r').read().split() # Get current rows
rows = int(rows) - 4 # Leave some space
columns = int(columns)

nflmca.ascii_spectrum(a, rows, columns, 1) # Plot                      
np.savetxt(outputfile + "-integrals.txt", a)
