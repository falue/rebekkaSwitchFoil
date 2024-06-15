# HLK-LD2410 B et C  (Microwave-based human/object presence sensor) 
#rev 1 DUCROS christian janvier 2024 à partir du fichier 
#rev 1 - shabaz - May 2023

#programme principal
from machine import Pin, UART
import utime

print("started")
""" print("..Wait 2s to not go into death loop")
utime.sleep(2)
print("go on") """

# Import additional local library
# Folder 'libraries/ld2450' is sent while offloading to device (?)
import sys
sys.path.append( './libraries')
from ld2450 import LD2450  # https://github.com/christianDUCROS/ld2410-human_sensor


# led if human_detection
# board led on Sparkfun Thing Plus is 13
boardled = Pin(13, Pin.OUT)
boardled.on()

tx_pin = 27 # WORKS ON PIN 16 aswell
rx_pin = 12 # WORKS ON PIN 17 aswell
# probleme communication : reponse vide 

print('-----------CONFIGURATION----------------')
uart1 = UART(1, baudrate = 256000, tx=Pin(tx_pin), rx=Pin(rx_pin), timeout = 1, timeout_char = 0, invert = 0)
print(uart1)

human_sensor = LD2450(uart1)
print('----------------------------------------')
human_sensor.enable_config()
human_sensor.read_firmware_version()
human_sensor.get_mac_address()
human_sensor.end_config()

utime.sleep(1) #debug pour lire les rapports de configuration

print('-----------DECTECTION----------------')
while True:
    human_sensor.send_command_report_data()  # returns bytes
    human_sensor.print_meas()
    measurements = human_sensor.get_meas()
    for keys,values in measurements.items():
        print("{0}: {1}".format(keys, values))

    detected = human_sensor.human_detection(boardled,0,0)
    if detected:
        print("  HUMAN DETECTED: ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||")
    else:
        print("  HUMAN DETECTED:")
    print("--------------------------------------------------")
    utime.sleep(.05)