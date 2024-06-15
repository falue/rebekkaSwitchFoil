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

def parse_hlk_ld2450_data(data):
    """
    Parses raw data from HLK-LD2450 sensor and returns a list of tuples with target coordinates.
    Args:
    data (bytes): Raw data from the HLK-LD2450 sensor.
    
    Returns:
    List[Tuple[int, int]]: List of tuples with x and y coordinates of targets.
    """
    if len(data) < 32:
        return []

    def bytes_to_int(bytes_seq):
        result = 0
        for b in bytes_seq:
            result = result * 256 + int(b)
        return result

    targets = []
    for i in range(3):  # Assuming up to 3 targets
        x_bytes = data[4 + i * 8:6 + i * 8]
        y_bytes = data[6 + i * 8:8 + i * 8]
        
        # Convert to signed integers manually
        x = bytes_to_int(x_bytes)
        if x >= 2**15:
            x -= 2**16
        y = bytes_to_int(y_bytes)
        if y >= 2**15:
            y -= 2**16
        
        if x == 0 and y == 0:
            continue
        targets.append((x, y))
    
    return targets


def print_targets(targets):
    """
    Prints the list of target coordinates in a readable format.
    Args:
    targets (List[Tuple[int, int]]): List of tuples with x and y coordinates of targets.
    """
    if not targets:
        print("No targets detected.")
    else:
        #print("Detected Targets:")
        for idx, (x, y) in enumerate(targets, start=1):
            print(f"Target {idx}: x={x}, y={y}")

print('-----------DECTECTION----------------')
while True:
    raw_data = human_sensor.send_command_report_data()  # returns bytes
    # print(type(raw_data))
    parsed_data = parse_hlk_ld2450_data(raw_data)  # returns list
    # print(type(parsed_data))
    #print(*parsed_data, sep = ", ")  # prints a comma sep. list
    print_targets(parsed_data)

    """ human_sensor.print_meas()
    measurements = human_sensor.get_meas()
    for keys,values in measurements.items():
        print("{0}: {1}".format(keys, values))

    detected = human_sensor.human_detection(boardled,0,0)
    if detected:
        print("  HUMAN DETECTED: ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||")
    else:
        print("  HUMAN DETECTED:") """
    print("--------------------------------------------------")
    utime.sleep(.05)