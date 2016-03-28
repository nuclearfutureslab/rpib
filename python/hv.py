from subprocess import call
from subprocess import check_output
import time

import gpio


class hv:
    def __init__(self, enablepin = 1, adc = 0, init = True):
        """Initialization
        Sets specified Turns HV off, sets DAC to zero.

        adc = number of Red Pitaya slow ADC to be used (0 - 3)

        enablepin = Number of the P-pin of Red Pitaya GPIO to be used as enable signal (0-7). 
        """

        self.enablepin = enablepin
        self.adc = adc
        # set pin P<enablepin> as output
        gpio.initOutput("P", self.enablepin)

        if init:
            # turn pin P<enablepin> off (low)
            gpio.output("P", self.enablepin, gpio.LOW)

            # voltageGoal is variable to store user defined voltage
            self.voltageGoal = 0
            # set DAC to 0
            self._setDAClevel(0)
        # if init = false, leave dac at existing level
        
    def setVoltage(self, voltage, ramp = True):
        """Set specific voltage, either ramping or immediate. 
        Ramping using 100 steps is default.
        """
        rampsteps = 100
        if voltage > 1600:
            print "Maximal voltage is 1600"
            return 0
        currentvoltage = self.getVoltage()
        self.voltageGoal = voltage
        # convert to CAEN Vset voltage
        caenvoltage = self.voltageGoal / 1600.0 * 2.6
        currentcaenvoltage = currentvoltage / 1600.0 * 2.6
        # convert to MCP4725 level (3.3V == 4095)
        goallevel = int(4095 * caenvoltage / 3.3)
        currentlevel = int(4095 * currentcaenvoltage / 3.3)
        deltalevel = goallevel - currentlevel
        print (currentvoltage, self.voltageGoal, currentlevel, deltalevel, goallevel)
        if(ramp == True):
            for i in range(1, rampsteps):
                ramplevel = int(currentlevel + 1.0 * deltalevel / rampsteps * i)
                print "Ramping, DAC level {:d}, Vset={:f}, Vmon={:f}".format(ramplevel, ramplevel / 4095.0 * 3.3 / 2.6 * 1600, self.getVoltage())
                self._setDAClevel(ramplevel)
                time.sleep(0.03)
            print "Ramping, DAC level {:d}, Vset={:f}, Vmon={:f}".format(goallevel, goallevel / 4095.0 * 3.3 / 2.6 * 1600, self.getVoltage())
            self._setDAClevel(goallevel)
        else:
            self._setDAClevel(goallevel)
        print "Wait 3 more seconds..."
        # wait 3 second cooldown
        time.sleep(3)
                
    def getVoltage(self):
        """Returns current high voltage, using the voltage measured with 
        the RedPitaya slow ADC.
        """
        # address = 0x40400000 + self.adc * 4
        # print address
        # voltage = call(["monitor", str(address)])
        # print voltage
        vlevel = ""
        # filename from http://forum.redpitaya.com/viewtopic.php?f=14&t=1093&p=3893#p3893
        with open("/sys/devices/soc0/amba_pl/83c00000.xadc_wiz/iio:device1/in_voltage11_raw", 'r') as f:
            vlevel = f.read()
        vlevel = int(vlevel.rstrip())
        # it is unclear why we have to convert Pitaya Slow ADC with 2048, not 4096 channels...
        caenvoltage = vlevel * 1.0 / 2048 * 3.5
        voltage = caenvoltage / 2.6 * 1600
        return voltage

    def enable(self):
        """Turn on HV module (set enable pin to high)"""
        gpio.output("P", self.enablepin, gpio.HIGH)
        
    def disable(self):
        """Turn off HV module (set enable pin to low)"""
        gpio.output("P", self.enablepin, gpio.LOW)
    
    def _getDAClevel(self):
        """Get current level of MCP4725 DAC (0 - 4095)
        """
        return 0

    def _setDAClevel(self, level):
        """Set current level of MCP4725 DAC (0 - 4095)
        """
        if(level < 0 or level > 4095):
            print "Can not set to this level. Needs to be 0-4095"
            return 0
        bytes = [(level >> 4) & 0xFF, (level << 4) & 0xFF]
        iword = hex(bytes[1] * 256 + bytes[0])
        call(["i2cset", "-y", "0", "0x62", "0x40", str(iword), "w"])

        
