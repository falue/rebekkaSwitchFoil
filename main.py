# HLK-LD2410 B et C  (Microwave-based human/object presence sensor) 
#rev 1 DUCROS christian janvier 2024 à partir du fichier 
#rev 1 - shabaz - May 2023

#programme principal
from machine import Pin, UART
import utime

##
## https://github.com/csRon/HLK-LD2450
##
# import serial_protocol
# import serial

print("started")

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


REPORT_HEADER = bytes.fromhex('AA FF 03 00')  # was AA FF 03 00
REPORT_TAIL = bytes.fromhex('55 CC')  # was 55 CC
def read_radar_data(serial_port_line:bytes)->tuple[12]:
    '''
    Read the basic mode data from the serial port line (see docs 2.3)
    Parameters:
    - serial_port_line (bytes): the serial port line
    Returns:
    - radar_data (tuple[12]): the radar data
        - [0-3] x, y, speed, distance_resolution of target 1
        - [4-7] x, y, speed, distance_resolution of target 2
        - [8-11] x, y, speed, distance_resolution of target 3
    '''

    # Check if the frame header and tail are present
    if REPORT_HEADER in serial_port_line and REPORT_TAIL in serial_port_line:
        # Interpret the target data
        if len(serial_port_line) == 30:
            target1_bytes = serial_port_line[4:12]
            target2_bytes = serial_port_line[12:20]
            target3_bytes = serial_port_line[20:28]

            all_targets_bytes = [target1_bytes, target2_bytes, target3_bytes]

            all_targets_data = []

            for target_bytes in all_targets_bytes:
                x = int.from_bytes(target_bytes[0:2], byteorder='little', signed=True)
                y = int.from_bytes(target_bytes[2:4], byteorder='little', signed=True)     
                speed = int.from_bytes(target_bytes[4:6], byteorder='little', signed=True)
                distance_resolution = int.from_bytes(target_bytes[6:8], byteorder='little', signed=False)
    
                # substract 2^15 depending if negative or positive
                x = x if x >= 0 else -2**15 - x
                y = y if y >= 0 else -2**15 - y
                speed = speed if speed >= 0 else -2**15 - speed

                # append ftarget data to the list and flatten
                all_targets_data.extend([x, y, speed, distance_resolution])
            
            return tuple(all_targets_data)
        
        # if the target data is not 17 bytes long the line is corrupted
        else:
            print("Serial port line corrupted - not 30 bytes long")
            return None
    # if the header and tail are not present the line is corrupted
    else: 
        print("Serial port line corrupted - header or tail not present")
        return None

print('-----------DECTECTION----------------')
while True:
    # Read a line from the serial port
    #serial_port_line = ser.read_until(serial_protocol.REPORT_TAIL)
    serial_port_line = human_sensor.send_command_report_data()  # returns bytes
    print(type(serial_port_line))
    serial_port_line = ' '.join(f'{byte:02x}' for byte in serial_port_line)
    print(serial_port_line)
    print(type(serial_port_line))
    print(type(serial_port_line.encode('utf-8')))

    all_target_values = read_radar_data(serial_port_line.encode('utf-8'))
    
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