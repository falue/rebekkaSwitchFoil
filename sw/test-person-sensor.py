
# https://github.com/Jacob-CE/micropython-person-sensor/blob/master/person_sensor.py
"""
MicroPython implementation for the Person Sensor by Useful Sensors (https://core-electronics.com.au/catalog/product/view/sku/SEN-21231)

Harware documentation: https://github.com/usefulsensors/person_sensor_docs/blob/main/README.md

Jacob Morris - 30/05/23
"""

from machine import I2C, Pin
import time
import struct

# The person sensor has the I2C ID of hex 62, or decimal 98.
PERSON_SENSOR_I2C_ADDRESS = 0x62
PERSON_SENSOR_REG_MODE = 0x01
PERSON_SENSOR_REG_ENABLE_ID = 0x02
PERSON_SENSOR_REG_SINGLE_SHOT = 0x03
PERSON_SENSOR_REG_CALIBRATE_ID = 0x04
PERSON_SENSOR_REG_PERSIST_IDS = 0x05
PERSON_SENSOR_REG_ERASE_IDS = 0x06
PERSON_SENSOR_REG_DEBUG_MODE = 0x07

# We will be reading raw bytes over I2C, and we'll need to decode them into
# data structures. These strings define the format used for the decoding, and
# are derived from the layouts defined in the developer guide.
PERSON_SENSOR_I2C_HEADER_FORMAT = "BBH"
PERSON_SENSOR_I2C_HEADER_BYTE_COUNT = struct.calcsize(
    PERSON_SENSOR_I2C_HEADER_FORMAT)

PERSON_SENSOR_FACE_FORMAT = "BBBBBBbB"
PERSON_SENSOR_FACE_BYTE_COUNT = struct.calcsize(PERSON_SENSOR_FACE_FORMAT)

PERSON_SENSOR_FACE_MAX = 4
PERSON_SENSOR_RESULT_FORMAT = PERSON_SENSOR_I2C_HEADER_FORMAT + \
    "B" + PERSON_SENSOR_FACE_FORMAT * PERSON_SENSOR_FACE_MAX + "H"
PERSON_SENSOR_RESULT_BYTE_COUNT = struct.calcsize(PERSON_SENSOR_RESULT_FORMAT)

class PersonSensor(object):
    
    def __init__(self, bus=0, sda=8, scl=9):
        self.i2c = I2C(bus, sda=Pin(sda), scl=Pin(scl), freq=400_000)
        time.sleep_ms(200)  # Small wait to ensure I2C sets up properly
        
        devices = self.i2c.scan()

        if int(PERSON_SENSOR_I2C_ADDRESS) not in devices:
            raise Exception(f"Could not find Person Sensor at address 0x{PERSON_SENSOR_I2C_ADDRESS:02x}!")
    
    
    """
    Set the mode of the sensor.
    mode=1 Continuous: Capture continuously, setting the GPIO trigger pin to high if a face is detected.
    mode=0 Standby: Lowest power mode, sensor is in standby and not capturing.
    """
    def set_mode(self, mode):
        data = b'\x01' if mode == 1 else b'\x00'
        self.i2c.writeto_mem(PERSON_SENSOR_I2C_ADDRESS, PERSON_SENSOR_REG_MODE, data)

    """
    Enable / Disable the ID model. With this flag set to False, only capture bounding boxes.
    """
    def enable_id_model(self, is_enabled):
        data = b'\x01' if is_enabled else b'\x00'
        self.i2c.writeto_mem(PERSON_SENSOR_I2C_ADDRESS, PERSON_SENSOR_REG_ENABLE_ID, data)
         
    """
    Trigger a single-shot inference. Only works if the sensor is in standby mode.
    read_faces() will return the data from last single shot until single shot is called again.
    """
    def single_shot(self):
        self.i2c.writeto_mem(PERSON_SENSOR_I2C_ADDRESS, PERSON_SENSOR_REG_SINGLE_SHOT, b'\x00')
        
    """
    Calibrate the next identified frame as person N, from 0 to 7. If two frames pass with no person, this label is discarded.
    """
    def label_next_id(self):
        self.i2c.writeto_mem(PERSON_SENSOR_I2C_ADDRESS, PERSON_SENSOR_REG_CALIBRATE_ID, b'\x00')
    
    """
    Store any recognized IDs even when unpowered.
    """
    def persist_ids(self, is_enabled):
        data = b'\x01' if is_enabled else b'\x00'
        self.i2c.writeto_mem(PERSON_SENSOR_I2C_ADDRESS, PERSON_SENSOR_REG_PERSIST_IDS, data)
    
    """
    Wipe any recognized IDs from storage.
    """
    def erase_ids(self):
        self.i2c.writeto_mem(PERSON_SENSOR_I2C_ADDRESS, PERSON_SENSOR_REG_ERASE_IDS, b'\x00')
    
    """
    Enable the LED indicator of the sensor
    """
    def enable_debug(self, is_enabled):
        data = b'\x01' if is_enabled else b'\x00'
        self.i2c.writeto_mem(PERSON_SENSOR_I2C_ADDRESS, PERSON_SENSOR_REG_DEBUG_MODE, data)
    
    
    """
    Run inference and return a list of faces and associated data found
    """
    def read_faces(self):
        read_data = bytearray(PERSON_SENSOR_RESULT_BYTE_COUNT)
        self.i2c.readfrom_into(PERSON_SENSOR_I2C_ADDRESS, read_data)

        offset = 0
        (pad1, pad2, payload_bytes) = struct.unpack_from(
            PERSON_SENSOR_I2C_HEADER_FORMAT, read_data, offset)
        offset = offset + PERSON_SENSOR_I2C_HEADER_BYTE_COUNT

        (num_faces) = struct.unpack_from("B", read_data, offset)
        num_faces = int(num_faces[0])
        offset = offset + 1

        faces = []
        for i in range(num_faces):
            (box_confidence, box_left, box_top, box_right, box_bottom, id_confidence, id,
             is_facing) = struct.unpack_from(PERSON_SENSOR_FACE_FORMAT, read_data, offset)
            offset = offset + PERSON_SENSOR_FACE_BYTE_COUNT
            face = {
                "box_confidence": box_confidence,
                "box_left": box_left,
                "box_top": box_top,
                "box_right": box_right,
                "box_bottom": box_bottom,
                "id_confidence": id_confidence,
                "id": id,
                "is_facing": is_facing,
            }
            faces.append(face)
        
        #checksum = struct.unpack_from("H", read_data, offset)
        
        return faces
    
from machine import SoftI2C    


# Exception: Could not find Person Sensor at address 0x62!
import time
#from person_sensor import PersonSensor
sda = Pin(23, Pin.IN, Pin.PULL_UP)
scl = Pin(22, Pin.IN, Pin.PULL_UP)
device = SoftI2C(sda=sda, scl = scl)
device.scan()


sensor = PersonSensor(bus=0, sda=sda, scl=scl)
print("Starting loop...")
while True:
    faces = sensor.read_faces()
    print(faces)    
    time.sleep(0.2)