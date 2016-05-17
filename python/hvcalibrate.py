# -------------------
# CALIBRATE
# -------------------

import numpy as np

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
        
