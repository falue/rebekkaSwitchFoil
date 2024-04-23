from machine     import Timer, Pin
from micropython import alloc_emergency_exception_buf
from math        import acos, pi


class Dimmer:
    def __init__(self, pwm_pin, zc_pin, fpulse = 4000):
        alloc_emergency_exception_buf(100)
        self._cnt    = 0
        self._freq   = 0
        self._timer  = Timer(2)
        self._mode   = Timer.ONE_SHOT
        self._pwm    = Pin(pwm_pin, Pin.OUT)
        self._fpulse = fpulse
        self._ppulse = 100.0 / fpulse + 0.11
        self._zc     = Pin(zc_pin,  Pin.IN)
        self._val    = 1
        self._zc.irq(trigger = Pin.IRQ_RISING , handler = self._zeroDetectIsr)

    
    def _zeroDetectIsr(self, pin):
        if 0 == self._freq:
            self._pwm.on()
            return
        if 0 > self._freq:
            self._pwm.off()
            return
        
        self._cnt += 1
        
        if 1 == self._cnt:
            self._timer.init(freq = self._freq, mode = self._mode, callback = self._dimmDelayIsr)
    
    
    def _dimmDelayIsr(self, _timer):
        if 1 == self._cnt:
            self._pwm.on()
            self._timer.init(freq = self._fpulse, mode = self._mode, callback = self._dimmDelayIsr)
        else:
            self._pwm.off()
        
        self._cnt = 0
    
    
    @property
    def value(self):
        return self._val
    
    
    @value.setter
    def value(self, p):
        p = min(1, max(0, p))
        
        if not self._val == p:
            self._val = p
            p         = acos(1 - p * 2) / pi
            
            if p < self._ppulse:
                f = -1
            elif p > 0.99:
                f = 0
            else:
                f = 100 / (1 - p)
            
            self._freq = int(f)
        
        return self._val