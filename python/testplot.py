import nflmca
import os
import numpy as np

filename = "testplot.txt"

totaldata = np.genfromtxt(filename)

rows, columns = os.popen('stty size', 'r').read().split()

rows = int(rows) - 4 # leave some space
columns = int(columns)

scaling = 1.0
scaling = nflmca.asciispectrum(totaldata, rows, columns, scaling)

