import nflmca
import os
import numpy as np
import sys
import matplotlib.pyplot as plt


if(len(sys.argv) != 2):
    print "Usage: plot.py <outputfilename>"
    print "Option can not be omitted!"
    exit(-1)

filename = sys.argv[1]

totaldata = np.genfromtxt(filename)

binmax = 1000000
binstep = binmax / 2048 # spacer to leave space for axis
histdata = np.histogram(totaldata, bins=range(0,binmax,binstep))[0]

plt.plot(histdata)
plt.show()
