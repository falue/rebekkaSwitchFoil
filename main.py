# HLK-LD2410 B et C  (Microwave-based human/object presence sensor) 
#rev 1 DUCROS christian janvier 2024 à partir du fichier 
#rev 1 - shabaz - May 2023
#rev 2 - dalius, fabian, besi - jun 2024
# 
# Based on
#   https://github.com/christianDUCROS/ld2410-human_sensor
# and
#   https://github.com/QuirkyCort/IoTy/blob/main/public/extensions/ld2410.py
# 
# Check out the PDF in docs/ page 12 for different communication protocol for sensor 2450 instead of 2410 (!)
# 
# Repo @ https://github.com/falue/rebekkaSwitchFoil


print("Program initiated")

from machine import Pin, UART
import utime
import sys

# Import additional local library
sys.path.append( './libraries')
from ld2450 import LD2450  # https://github.com/christianDUCROS/ld2410-human_sensor

# DEFINE PLAYGROUND
# If a person is in this area, the relay is switched on
# Polygon edge points, clockwise from top left, in cm
p1 = (-35, 1200)
p2 = (35, 1200)
p3 = (35, 0)
p4 = (-35, 0)
points = [p1, p2, p3, p4]

# PIN DEFINITIONS
# Sparkfun Thing Plus
led_pin = Pin(13, Pin.OUT)   # On board led
relay_pin = Pin(4, Pin.OUT)  # GPIO 4 is equiv. A5
tx_pin = 27
rx_pin = 12


def is_point_on_edge(x, y, l1, l2):
    """
    Check if a point (x, y) is on the edge defined by points l1 and l2.
    """
    if (min(l1[0], l2[0]) <= x <= max(l1[0], l2[0]) and
            min(l1[1], l2[1]) <= y <= max(l1[1], l2[1])):
        if l1[0] != l2[0]:  # Non-vertical line
            slope = (l2[1] - l1[1]) / (l2[0] - l1[0])
            intercept = l1[1] - slope * l1[0]
            return y == slope * x + intercept
        else:  # Vertical line
            return x == l1[0]
    return False

def is_point_in_polygon(posX, posY):
    """
    Check if the point (posX, posY) is inside the polygon defined by points p1, p2, p3, p4.
    Args:
    posX (float): X coordinate of the point to check.
    posY (float): Y coordinate of the point to check.
    Returns:
    bool: True if the point is inside the polygon, False otherwise.
    """

    # Check if the point is on any of the polygon's edges
    for i in range(4):
        if is_point_on_edge(posX, posY, points[i], points[(i + 1) % 4]):
            return True

    # Ray-casting algorithm
    def is_inside_polygon(x, y, points):
        n = len(points)
        inside = False
        px, py = points[0]
        for i in range(1, n + 1):
            qx, qy = points[i % n]
            if y > min(py, qy):
                if y <= max(py, qy):
                    if x <= max(px, qx):
                        if py != qy:
                            x_intersect = (y - py) * (qx - px) / (qy - py) + px
                        if px == qx or x <= x_intersect:
                            inside = not inside
            px, py = qx, qy
        return inside

    return is_inside_polygon(posX, posY, points)

# SETUP
print('-----------CONFIGURATION----------------')
uart1 = UART(1, baudrate = 256000, tx=Pin(tx_pin), rx=Pin(rx_pin), timeout = 1, timeout_char = 0, invert = 0)
print(uart1)
led_pin.on()
human_sensor = LD2450(uart1)
human_sensor.enable_config()
human_sensor.read_firmware_version()
human_sensor.get_mac_address()
human_sensor.end_config()
print('----------------------------------------')
# utime.sleep(1) # debug to read configuration reports
print('-----------DECTECTION-------------------')

# LOOP
while True:
    # Read line from the serial port as HEX
    human_sensor.send_command_report_data() # get sensor data

    # Translate data to object
    targets = human_sensor.get_sensor_measurements()
    print('DATA:',targets)

    # targetCoords = [(targets[0]["x"], targets[0]["y"]), (targets[1]["x"],targets[1]["y"]), (targets[2]["x"], targets[2]["y"])]
    targetCoords = [
        ((targets[0]["x"], targets[0]["y"]) if targets[0] is not None else (0, -100)),
        ((targets[1]["x"], targets[1]["y"]) if targets[1] is not None else (0, -100)),
        ((targets[2]["x"], targets[2]["y"]) if targets[2] is not None else (0, -100))
    ]
    # targets = [(246, 279), (-286, 285), (292, -140)]
    # TODO: if all points outside or noone around, how to detect?

    # detect persons
    results = [(x, y, is_point_in_polygon(x, y)) for x, y in targetCoords]
    any_human_in_area = any(result for _, _, result in results)

    # Is someone in area?
    if any_human_in_area:
        print("There you are! Human detected.")
        relay_pin.value(0)  # Turn the relay off (therefore, make smart foil white, therefore needs no power)
        led_pin.value(1)    # Turn the LED on
    else:
        print("Target lost!")
        relay_pin.value(1)  # Turn the relay on (therefore, make smart foil transparent, therefore needs power)
        led_pin.value(0)    # Turn the LED off

    utime.sleep(.03) #speed
