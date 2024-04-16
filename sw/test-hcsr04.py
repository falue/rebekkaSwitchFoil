# https://randomnerdtutorials.com/micropython-hc-sr04-ultrasonic-esp32-esp8266/

echo_pin = 13
trig_pin = 12

# Complete project details at https://RandomNerdTutorials.com/micropython-hc-sr04-ultrasonic-esp32-esp8266/
from hcsr04 import HCSR04
from time import sleep

ultrasonic = HCSR04(trigger_pin=trig_pin, echo_pin=echo_pin, echo_timeout_us=100000)

while True:
    distance = ultrasonic.distance_cm()
    print('Distance:', distance, 'cm')
    sleep(.5)
    