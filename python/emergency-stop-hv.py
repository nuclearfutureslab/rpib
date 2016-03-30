import hv

hvcontrol = hv.hv(init = False)
hvcontrol.setVoltage(0)
hvcontrol.disable()
