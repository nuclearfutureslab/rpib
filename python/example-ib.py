import gpio
import hv
import time

# Initialize HV controller, enablepin is P1

hvctrl = hv.hv(enablepin = 1)

gpio.init_output("N", 0)      # Set N0 as output (LED: HV status, on/off)
gpio.output("N", 0, gpio.LOW) # Turn LED off

gpio.init_output("N", 2)      # Set N2 as output (LED: IB status, busy/ready)
gpio.output("N", 2, gpio.LOW) # Turn LED off

gpio.init_input("N", 1)       # Set N1 as input
gpio.init_input("N", 3)       # Set N3 as input

hvstatus = 0

while 1:

    if(gpio.input("N", 1) == gpio.LOW and hvstatus == 0):
        print "Pressed 1, Ramp HV up"
        hvstatus = 1
        hvctrl.enable()
        hvctrl.set_voltage(1000)
        
        gpio.output("N", 0, gpio.HIGH) # LED: HV on

    if(gpio.input("N", 1) == gpio.LOW and hvstatus == 1):
        print "Pressed 1, Ramp HV down"
        hvstatus = 0
        hvctrl.set_voltage(0)
        hvctrl.disable()
        
        gpio.output("N", 0, gpio.LOW) # LED: HV off

    if(gpio.input("N", 3) == gpio.LOW):
        print "Start Measurement"

        gpio.output("N", 2, gpio.HIGH) # LED: IB busy
        time.sleep(5)                  # Initiate measurement here

        gpio.output("N", 2, gpio.LOW)  # LED: IB ready

