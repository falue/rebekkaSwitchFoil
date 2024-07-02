from machine import Pin
import time

print("System started... B")

# Define the pin connected to the relay
led_pin = Pin(13, Pin.OUT)    # D13 on SparkFun RedBoard
relay_pin = Pin(4, Pin.OUT)  # D19 on SparkFun RedBoard 4=A5   MANUAL WIRING !!!!
relay_pin = Pin(18, Pin.OUT)  # D19 on SparkFun RedBoard 4=A5  PCB !!!!

# Function to turn the relay on and off
def switch_relay(num_iterations):
    if(num_iterations > 0):
        for _ in range(num_iterations):
            blink()
    else:
        while True:
            blink()

def blink():
    relay_pin.value(1)  # Turn the relay on
    led_pin.value(1)    # Turn the LED on
    print('relay ON')
    time.sleep(2)       # Wait for 1 second

    relay_pin.value(0)  # Turn the relay off
    led_pin.value(0)    # Turn the LED off
    print('relay OFF')
    time.sleep(2)       # Wait for 1 second


# Call the function
switch_relay(0)
