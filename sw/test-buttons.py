from machine import Pin
import time

button_a = Pin(33, Pin.IN, Pin.PULL_UP)
button_b = Pin(19, Pin.IN, Pin.PULL_UP)

processing = False

def buttonPressed(button):
    global processing

    if not processing:        
        processing = True
        if button == button_a:
            print("down")
        else:
            print("up")
        time.sleep(.2)
        processing = False
    
button_a.irq(buttonPressed, Pin.IRQ_FALLING)
button_b.irq(buttonPressed, Pin.IRQ_FALLING)
