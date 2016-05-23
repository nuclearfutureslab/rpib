import hv

hvcontrol = hv.hv(init = False)
hvcontrol.set_voltage(0)
hvcontrol.disable()
