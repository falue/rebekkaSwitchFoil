from machine import Pin
import time

print("System started...")

# Define the pin connected to the LED
led_pin = Pin(13, Pin.OUT)  # D13 on SparkFun RedBoard

# Function to turn the LED on and off
def blink_led(num_iterations):
    for _ in range(num_iterations):
        led_pin.value(1)  # Turn the LED on
        print('LED ON')
        time.sleep(1)     # Wait for 1 second
        led_pin.value(0)  # Turn the LED off
        print('LED OFF')
        time.sleep(1)     # Wait for 1 second

# Call the function
blink_led(10)