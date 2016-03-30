import gpio
import hv
import time

######################################
# TESTING OUTPUT (LED)
######################################

print "GPIO Test"
print "Initialize P0 as output"
gpio.initOutput("P", 0)
print "Initialize P2 as output"
gpio.initOutput("P", 2)
print "Initialize N7 as output"
gpio.initOutput("N", 7)
print "Set P0 to high"
gpio.output("P", 0, gpio.HIGH)
time.sleep(2)
print "Set P0 to low"
gpio.output("P", 0, gpio.LOW)
print "Set P2 to high"
gpio.output("P", 2, gpio.HIGH)
time.sleep(2)
print "Set P2 to low"
gpio.output("P", 2, gpio.LOW)
print "Set N7 to high"
gpio.output("N", 7, gpio.HIGH)
time.sleep(2)
print "Set N7 to low"
gpio.output("N", 7, gpio.LOW)

######################################
# TESTING INPUT (BUTTON)
######################################

print "Initialize P7 as input"
gpio.initInput("P", 7)

while gpio.input("P", 7) == 1:
	True
print("Button pressed")

# exit()

######################################
# TESTING HIGH VOLTAGE
######################################

print ""
print "HV Test"
print "Create instance"
hvcontrol = hv.hv()
print "Enable HV Module"
hvcontrol.enable()
print "Ramp up to 1000 V"
hvcontrol.setVoltage(1000, ramp = True)
print "Current Voltage (measured): {:f}".format(hvcontrol.getVoltage())
print "Wait 5 seconds"
time.sleep(5)
print "Current Voltage (measured): {:f}".format(hvcontrol.getVoltage())
print "Wait 5 seconds"
time.sleep(5)
print "Current Voltage (measured): {:f}".format(hvcontrol.getVoltage())
print "Ramp down to 0 V"
hvcontrol.setVoltage(0, ramp = True)
hvcontrol.disable()

######################################
