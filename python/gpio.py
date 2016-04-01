
# ---------------------------------------------------------------------------
# GPIO PACKAGE FOR RED PITAYA (Revision 0, March 2016)
# ---------------------------------------------------------------------------

from subprocess import call
from subprocess import check_output

HIGH = 1
LOW = 0

# ---------------------------------------------------------------------------
# Initialize pin as output pin
# ---------------------------------------------------------------------------

def init_output(pn, pinno):
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
    
    # Read current setting
    
    statusstring = check_output(["monitor", address])
    status = int(statusstring.rstrip(), 0)
    
    # Convert pinno in bitmask
    
    bpin = 2 ** pinno

    # New status is old status and bitwise or 

    newstatus = status | bpin
    
    # Set new status
    
    call(["monitor", address, str(newstatus)])

# ---------------------------------------------------------------------------
# Initialize pin as input pin
# ---------------------------------------------------------------------------
            
def init_input(pn, pinno):
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

    # Read current setting

    statusstring = check_output(["monitor", address])
    status = int(statusstring.rstrip(), 0)

    # Convert pinno in negative bitmask (1 for all positions except pinno)

    bpin = 255 - 2 ** pinno

    # New status is old status and bitwise and

    newstatus = status & bpin

    # Set new status
    
    call(["monitor", address, str(newstatus)])

# ---------------------------------------------------------------------------
# Set output pin to LOW/HIGH
# ---------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------
# Read input pin status
# ---------------------------------------------------------------------------

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

    # Read from address

    statusstring = check_output(["monitor", address])
    status = int(statusstring.rstrip(), 0)

    # Create bitmask for pin

    bpin = 2 ** pinno

    # Return bitwise and between status and pin is pin status

    return status & bpin

# ---------------------------------------------------------------------------
