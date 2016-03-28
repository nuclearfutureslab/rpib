from subprocess import call
from subprocess import check_output

HIGH = 1
LOW = 0

def initOutput(pn, pinno):
    if pinno < 0 or pinno > 7:
        print "Not a valid pin number"
        return 0
    if(pn == "p" or pn == "P"):
        address = "0x40000010"
    elif(pn == "n" or pn == "N"):
        address = "0x40000014"
    else:
        print "Unknown pn, can only be 'p' or 'n'"
        return 0
    # read current setting
    statusstring = check_output(["monitor", address])
    status = int(statusstring.rstrip(), 0)
    #convert pinno in bitmask
    bpin = 2 ** pinno
    #new status is oldstaus and bitwise or 
    newstatus = status | bpin
    #set new status
    call(["monitor", address, str(newstatus)])
            
def initInput(pn, pinno):
    if pinno < 0 or pinno > 7:
        print "Not a valid pin number"
        return 0
    if(pn == "p" or pn == "P"):
        address = "0x40000010"
    elif(pn == "n" or pn == "N"):
        address = "0x40000014"
    else:
        print "Unknown pn, can only be 'p' or 'n'"
        return 0
    # read current setting
    statusstring = check_output(["monitor", address])
    status = int(statusstring.rstrip(), 0)
    #convert pinno in negative bitmask (1 for all positions except pinno)
    bpin = 255 - 2 ** pinno
    #new status is oldstatus and bitwise and
    newstatus = status & bpin
    #set new status
    call(["monitor", address, str(newstatus)])

def output(pn, pinno, level):
    if pinno < 0 or pinno > 7:
        print "Not a valid pin number"
        return 0
    if(pn == "p" or pn == "P"):
        address = "0x40000018"
    elif(pn == "n" or pn == "N"):
        address = "0x4000001c"
    else:
        print "Unknown pn, can only be 'p' or 'n'"
        return 0
    statusstring = check_output(["monitor", address])
    status = int(statusstring.rstrip(), 0)
    if level == HIGH:
        #convert pinno in bitmask (1 at pin position)
        bpin = 2 ** pinno
        #new status is oldstaus and bitwise or 
        newstatus = status | bpin
    elif level == LOW:
        #convert pinno in bitmask (0 at pin position)
        bpin = 255 - 2 ** pinno
        #new status is olstatus and bitwise and
        newstatus = status & bpin
    else:
        print "Undefined level, should be 0 or 1"
        return 0
    #set new status
    call(["monitor", address, str(newstatus)])

def input(pn, pinno):
    if pinno < 0 or pinno > 7:
        print "Not a valid pin number"
        return 0
    if(pn == "p" or pn == "P"):
        address = "0x40000020"
    elif(pn == "n" or pn == "N"):
        address = "0x40000024"
    else:
        print "Unknown pn, can only be 'p' or 'n'"
        return 0
    # read from address
    statusstring = check_output(["monitor", address])
    status = int(statusstring.rstrip(), 0)
    # create bitmask for pin
    bpin = 2 ** pinno
    # return bitwise and between status and pin is pin status
    return status & bpin
