import numpy as np
import matplotlib.pyplot as plt
import sys

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

def correctnegative(a):
    if(a >= 8192):
        return a - 16384;
    else:
        return a;
correctnegative = np.vectorize(correctnegative)

def read_acquistion_file(filename, negativepulse = False, binary = True, process = True):
    if binary:
        fh = open(filename, "rb")
        header_datatype = np.dtype([('decimation','int32'), 
                                    ('tracelength','int32'), 
                                    ('pretriggerlength', 'int32'),
                                    ('triggervoltage','float32'),
                                    ('trigger','int32')])
        header = np.fromfile(fh, 
                             dtype = header_datatype,
                             count = 1)
        #a = np.fromfile(filename,dtype='int32')
        a = np.fromfile(fh, dtype = 'int32')
        a = correctnegative(a)
        if(negativepulse):
            a = np.multiply(a, -1)
        a.shape = (len(a)/header['tracelength'][0], header['tracelength'][0])
        fh.close()
        return [header, a]
    else:
        pretriggerlength = 32
        risecounts = 5
        count = 0
        header = []
        filelength =  file_len(filename)
        filelength -= 5
        step = filelength / 20
        with open(filename) as f:
            sys.stdout.write("Reading Spectrum: ")
            # HEADER
            for line in f:
                count += 1
                #print(line)
                if(count == 5):
                    break
            # Content
            count = 0
            data = np.zeros(filelength, dtype = 'int')
            for line in f:
                a = np.fromstring(line, dtype = 'int', sep=' ')
                a = correctnegative(a)
                if(negativepulse):
                    a = np.multiply(a, -1)
                base = np.average(a[0:(pretriggerlength-risecounts)])
                integral = int(np.sum(np.subtract(a, base)))
                data[count] = integral
                count += 1
                if(count % step == 0):
                    sys.stdout.write(" {:d}%".format(int(100.0 * count / filelength)))
                    # print 1.0 * count / filelength
                    # if(1.0 * count /filelength > 0.2):
                    #     break
        print ""
        return [header, data]

def ascii_spectrum(totaldata, rows, columns, scaling = 1, binmax = 1000000):
    # make histogram
    spacer = 6
    binstep = binmax / (columns - spacer) # spacer to leave space for axis
    histdata = np.histogram(totaldata, bins=range(0,binmax,binstep))[0]

    while(max(histdata) * scaling > rows):
        scaling = scaling / 2.0
    histdata = np.multiply(histdata, scaling)
    maxdisplay = 1.0 * rows / scaling
    maxtick = int(np.around(maxdisplay, -int(np.log10(maxdisplay))))
    tick = 10 ** int(np.log10(maxdisplay))
    ticks = range(maxtick, tick, -tick) + [tick]
    rowticks = np.around(np.multiply(ticks, scaling))
    specstring = ""
    tickcount = 0
    for i in range(rows, 0, -1):
        if tickcount < len(ticks) and i <= rowticks[tickcount]:
            specstring += "{:.0e}+".format(ticks[tickcount])
            tickcount += 1
        else:
            specstring += "     |"
        for j in range(columns - spacer):
            if histdata[j] > i:
                specstring += "*"
            else:
                specstring += " "
        specstring += "\n"
    specstring = specstring.rstrip()

    print "Acquired Spectrum"
    print "  Counts (linear scale)"
    print specstring
    yaxis = "    0+"
    for i in range(1, columns - spacer):
        if i % 5 == 0:
            yaxis += "+"
        else:
            yaxis += "-"
    yaxis += "|"
    print yaxis
    return scaling


# -------------------
# CALIBRATE
# -------------------

#The expected energies of the calibration peaks in keV
#Peaks were chosen for prominence and separation from other peaks on the Thorium spectrum
EXPNRGS = [238.6, 583.2, 911.2, 2614.5]
#The smoothing windows for each peak, in channels in both directions
#Windows chosen are smaller for low-energy (high-resolution/narrow) peaks
SMOOTHS = [3, 5, 7, 10]
#The minimum expected channel number for each peak
MINCS = [100, 340, 500, 1500]
#The maximum expected channel number for each peak
MAXCS = [200, 400, 600, 1700]
#Channel numbers were tuned to capture the peaks on the current cable and HV source.
#Hardware changes will require manual re-tuning
#Pseudo-arbitrary scaling factor
SCALING = 0.00299667925129
#The number of bins - note this only matters for calibration and should not affect testing
BINS = 2000
PARAMS = np.array([3])

# ------------------------------------------------------------------
# Given a raw count list, returns quadratic parameters 
# The 3-value parameter vector goes from highest to lowest order
# so energies = params[0]*(charge**2) + params[1]*charge + params[2]
# (after scaling -- see getenergies function below)
# The suggested default fit,  'polyfit' will not constrain params[0] 
# to 0, any other setting on fit will. Leaving params[0] unconstrained
# is suggested, as it tends to lead to better calibration, except at 
# very low energies. 
#
# The testing parameter should only be turned on for testing (duh!): 
# it returns the peak channel numbers concatenated to the fit params
# 
# returns 0 if parameters are outside asserted values
# 
# -------------------------------------------------------------------
def calibrate(data, exp_e = EXPNRGS, chanmins = MINCS, chanmaxs = MAXCS, 
    smooths = SMOOTHS):
    
	# Ensure that input parameters are correct length
    pts = len(exp_e)
    if (len(chanmins) != pts): return 0
    if (len(chanmaxs) != pts): return 0
    if (pts < 3): return 0
    peakpos = np.zeros([pts])
    
    # Bin the charge input
    bincount = bindata(data)
        
    # And turn it into a spectrum
    spec = np.bincount(bincount, minlength=BINS)
    

    # polyfit peak positions to channel numbers

    for i in range(len(exp_e)):
        peakpos[i] = findmax(spec, chanmins[i], chanmaxs[i], exp_e[i], smooths[i])
        if (peakpos[i] == 0): return 0
        
    fitparams = np.polyfit(peakpos, exp_e, 2)
    
    # (quite forgiving) bounds for rejecting calibrations
    if ((fitparams[0] < -0.01) or (fitparams[0] > 0.01)): return 0
    if ((fitparams[1] < 1) or (fitparams[1] > 2)): return 0
    if ((fitparams[2] < -20) or (fitparams[2] > 20)): return 0

    # insert code to return 0 if fitparams are outside certain parameters
         
    return fitparams


# ---------------------------------------------------------------------------
# Define Region of Interest (minchan:maxchan) and find central channel of peak
# ---------------------------------------------------------------------------
	
def findmax(spec, minchan, maxchan, expnrg, smooth=10):

    if (minchan > maxchan):
    	temp = minchan
    	minchan = maxchan
    	maxchan = temp
    	
    if ((minchan + smooth*2) > maxchan): smooth = 1
    if (minchan == maxchan): return minchan
    

    roi =  spec[minchan:maxchan]
    	
	# ------------------------
	# Simple Moving Mean (SMM)
	# ------------------------

    smmroi = np.zeros(len(roi))

    for i in range(smooth, len(roi) - smooth):
        smmroi[i] = np.mean(roi[i - smooth : i + smooth])

	
	# Find maximum value of smooth peak and determine channel number

    peakpos = [i for i, j in enumerate(smmroi) if j == max(smmroi)][0] + minchan
    
    
    # Return 0 if peak is on edge (window too constrained)
    if ((peakpos == minchan + smooth) or (peakpos == maxchan - smooth)): return 0
    
    #print("For the peak at ", expnrg, " keV, the channel number is ", peakpos)
	
    #plt.plot(roi)
    #plt.plot(smmroi)
    #plt.show()
	
    return peakpos
    
# Bins charges
    
def bindata(data, scaling = SCALING, bins = BINS):
    
    binlist = np.linspace(1,bins,bins)
    bincount = np.digitize(scaling * data, binlist)
    return bincount
    
# Returns the energies given the charge input and the given (or saved) calibration
    
def getenergies(charges, params): 
    
    scaled = charges*SCALING
    energies = params[0]*(scaled**2) + params[1]*scaled + params[2]
    return energies
        

# -------------------
# Measure as Function
# -------------------

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
