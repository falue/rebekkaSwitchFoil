# Test dimmer library

import network
sta_if = network.WLAN(network.STA_IF)
sta_if.active(False)
ap_if = network.WLAN(network.AP_IF)
ap_if.active(False)


dim_pin = 15
zero_cross_pin = 33
from dimmer import Dimmer
dimmer = Dimmer(dim_pin, zero_cross_pin)
dimmer.value = .25
import time

print("dimmer started")
while True:
    time.sleep(0.1)
    
    
# this works to create a spooky light bulb effect