# Test dimmer library
import time
from dimmer import Dimmer
from machine  import Pin
import network

sta_if = network.WLAN(network.STA_IF)
sta_if.active(False)
ap_if = network.WLAN(network.AP_IF)
ap_if.active(False)


dim_pin = 18
zero_cross_pin = 5
dimmer = Dimmer(dim_pin, zero_cross_pin)
dimmer.value = 0

button_a = Pin(33, Pin.IN, Pin.PULL_UP)
button_b = Pin(19, Pin.IN, Pin.PULL_UP)
led = Pin(13, Pin.OUT)

def blink():
    led.on()
    time.sleep(0.05)
    led.off()
    time.sleep(0.05)
    

blink();blink();blink()
print(f"dimmer is at {dimmer.value}")


while True:

    if button_a() == 0:
        blink()
        v = dimmer.value
        dimmer.value = dimmer.value - 0.1
        if v <= 0.1:
            blink()
            dimmer.value = 1
        print(f"dimmer is at {dimmer.value}")
    
    time.sleep(0.2)
    
    
# this works to create a spooky light bulb effect

