# See https://forums.raspberrypi.com/viewtopic.php?p=2118520&hilit=dimmer#p2118520

from   machine import Pin, Timer
from   math    import acos, pi

ZERO_CROSSOVER_PIN = 33
TRIAC_FIRING_PIN   = 15

zeroCrossoverPin = Pin(ZERO_CROSSOVER_PIN, Pin.IN, Pin.PULL_DOWN)
triacFiringPin   = Pin(TRIAC_FIRING_PIN, Pin.OUT, value=0)

freq  = 200
timer = Timer(1)

def triacpulse(a):
    global dummy
    triacFiringPin.on()
    for x in range (50): pass
    triacFiringPin.off()
    
def ZeroCrossover(arg):
    triacFiringPin.off()
    timer.init(freq=freq,mode=Timer.ONE_SHOT,callback=triacpulse)
          
zeroCrossoverPin.irq(trigger=Pin.IRQ_RISING, handler=ZeroCrossover)

while True:
    p = int(input ( "enter number between 1 and 100: " ))
    p = p/100
    p = min(1, max(0, p))
    p = acos(1 - p * 2) / pi
    
    if p < 0.15 :
        freq = 100
    elif p > 0.99:
        freq = 2000
    else:
        freq = int(100 / (1 - p))
