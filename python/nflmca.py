import numpy as np
import matplotlib.pyplot as plt
import sys

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

def readpeakfromfile(filename, 
                     negative = False, 
                     tracelimit = 0, 
                     step = 5000, 
                     multipeakplot = False, 
                     multipeakdeletion = True):
    peaklength = 100
    multipeakcount = 0
    if(tracelimit == 0):
        filelength =  file_len(filename)
    else:
        if(tracelimit < file_len(filename)):
            filelength = tracelimit
        else:
            filelength = file_len(filename)
    print(filelength)
    maxno = filelength / step * step
    print(maxno)
    start = 0
    b = np.zeros(shape=(maxno/step,step), dtype='int')
    while((start+step) <= maxno):
        a = np.genfromtxt(filename, skip_header = start, dtype='int', max_rows=step)
        if(negative):
            b[start/step] = a.min(axis=1)
        else:
            firstmax = a[:,0:peaklength].max(axis=1)
            fullmax = a.max(axis=1)
            diff = firstmax - fullmax
            if(np.sum(diff) != 0):
                multipeakindexes = np.nonzero(diff)[0]
                multipeakcount += len(multipeakindexes);
                for index in multipeakindexes:
                    if(multipeakplot == True):
                        plt.plot(a[index])
                        plt.show()
                    if (multipeakdeletion == True):
                        fullmax[index] = 32000
            b[start/step] = fullmax
        start = start + step
        print "loaded {:f}%".format(100.0 * start / maxno)
    if(start < filelength):
        a = np.genfromtxt(filename, skip_header = start, dtype='int', max_rows=(filelength - start))
    print "Found {:d} multipeak traces, {:f}% of all traces".format(multipeakcount, 100.0*multipeakcount/filelength)
    return b.flatten()

def readcanberra(filename):
    a = np.genfromtxt(filename, skip_header = 7, delimiter=",")
    a = a[:,2]
    return a

def energyspectrum(channelcounts, m, b):
    dates = np.fromfunction(lambda i: i * m + b, (len(channelcounts),))
    return [dates, channelcounts]

def correctnegative(a):
    if(a >= 8192):
        return a - 16384;
    else:
        return a;
correctnegative = np.vectorize(correctnegative)

def readpitayafile(filename, negativepulse = False):
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

def integratetrace(trace, tracelength, pretriggerlength, risecounts = 5):
    base = np.average(trace[0:(pretriggerlength-risecounts)])
    integral = np.sum(np.subtract(trace, base))
    return integral
  
def integratetraces(traces, tracelength, pretriggerlength, risecounts = 5, plotnegative = False):
    negativecount = 0
    b = np.zeros(len(traces), dtype='int')
    for i in range(len(traces)):
        b[i] = integratetrace(traces[i], tracelength, pretriggerlength, risecounts)
        if(b[i] < 0):
            b[i] = 2 ** 25
            negativecount += 1
            if(plotnegative):
                print("Average baseline: {:f}".format(np.average(traces[i][0:(pretriggerlength-risecounts)])))
                plt.plot(traces[i])
                plt.show()
    print("Found {:d} traces with negative integrals ({:f} %)".format(negativecount, 100.0 * negativecount / len(traces)))
    return b

def peaksfromtraces(traces, tracelength, pretriggerlength, 
                    risecounts = 5, 
                    peaklength = 20,
                    multipeakplot = False,
                    multipeakdeletion = True):
    multipeakcount = 0 
    firstmax = traces[:,pretriggerlength-risecounts:pretriggerlength-risecounts+peaklength].max(axis=1)
    fullmax = traces.max(axis=1)
    diff = firstmax - fullmax
    if(np.sum(diff) != 0):
        multipeakindexes = np.nonzero(diff)[0]
        multipeakcount = len(multipeakindexes);
        for index in multipeakindexes:
            if(multipeakplot == True):
                plt.plot(traces[index])
                plt.show()
            if (multipeakdeletion == True):
                firstmax[index] = 32000
    print "Found {:d} multipeak traces, {:f}% of all traces".format(multipeakcount, 100.0*multipeakcount/len(traces))
    return firstmax[(firstmax != 32000)]
    
def channelhist(values, channelno = 2048, maxbin = -1):
    binmax = max(values)
    if(maxbin > 0 and maxbin < binmax):
        binmax = maxbin
    if(binmax < channelno):
        binstep = 1
        binmax = channelno
    else:
        binstep = int(1.0 * binmax / channelno)
    return np.histogram(values, bins=range(0,binmax,binstep))[0] 

def readacquistionfile(filename, negativepulse = False, binary = True, process = True):
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

def asciispectrum(totaldata, rows, columns, scaling = 1, binmax = 1000000):
    # make histogram
    spacer = 5
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
