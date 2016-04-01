import numpy as np
import matplotlib.pyplot as plt
import sys

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

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
