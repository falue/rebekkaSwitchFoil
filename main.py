# HLK-LD2410 B et C  (Microwave-based human/object presence sensor) 
#rev 1 DUCROS christian janvier 2024 à partir du fichier 
#rev 1 - shabaz - May 2023

#programme principal
from machine import Pin, UART
import utime

##
## https://github.com/csRon/HLK-LD2450
##
import serial_protocol
# import serial

print("started")

# Import additional local library
# Folder 'libraries/ld2450' is sent while offloading to device (?)
""" import sys
sys.path.append( './libraries')
from ld2450 import LD2450  # https://github.com/christianDUCROS/ld2410-human_sensor """


# led if human_detection
# board led on Sparkfun Thing Plus is 13
boardled = Pin(13, Pin.OUT)
boardled.on()

tx_pin = 27 # WORKS ON PIN 16 aswell
rx_pin = 12 # WORKS ON PIN 17 aswell
# probleme communication : reponse vide 

print('-----------CONFIGURATION----------------')
ser = UART(1, baudrate = 256000, tx=Pin(tx_pin), rx=Pin(rx_pin), timeout = 1, timeout_char = 0, invert = 0)
print(ser)

""" human_sensor = LD2450(uart1)
print('----------------------------------------')
human_sensor.enable_config()
human_sensor.read_firmware_version()
human_sensor.get_mac_address()
human_sensor.end_config() """

utime.sleep(1) #debug pour lire les rapports de configuration


print('-----------DECTECTION----------------')
while True:
    # Read a line from the serial port
    serial_port_line = ser.read_until(serial_protocol.REPORT_TAIL)

    all_target_values = serial_protocol.read_radar_data(serial_port_line)
    
    if all_target_values is None:
        continue

    target1_x, target1_y, target1_speed, target1_distance_res, \
    target2_x, target2_y, target2_speed, target2_distance_res, \
    target3_x, target3_y, target3_speed, target3_distance_res \
        = all_target_values

    # Print the interpreted information for all targets
    print(f'Target 1 x-coordinate: {target1_x} mm')
    print(f'Target 1 y-coordinate: {target1_y} mm')
    print(f'Target 1 speed: {target1_speed} cm/s')
    print(f'Target 1 distance res: {target1_distance_res} mm')

    print(f'Target 2 x-coordinate: {target2_x} mm')
    print(f'Target 2 y-coordinate: {target2_y} mm')
    print(f'Target 2 speed: {target2_speed} cm/s')
    print(f'Target 2 distance res: {target2_distance_res} mm')

    print(f'Target 3 x-coordinate: {target3_x} mm')
    print(f'Target 3 y-coordinate: {target3_y} mm')
    print(f'Target 3 speed: {target3_speed} cm/s')
    print(f'Target 3 distance res: {target3_distance_res} mm')

    print("--------------------------------------------------")
    utime.sleep(.05)