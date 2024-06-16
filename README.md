# Library taken from https://github.com/QuirkyCort/IoTy/blob/main/public/extensions/ld2410.py

# Alternatively this french guy is using a similar or the same library:
# https://www.youtube.com/watch?v=QDC7T2RiKgo
# https://github.com/christianDUCROS/ld2410-human_sensor

# Arduino edition: https://github.com/0ingchun/arduino-lib_HLK-LD2450_Radar


MPY: soft reboot
enable config success
UART(1, baudrate=256000, bits=8, parity=None, stop=1, tx=12, rx=13, rts=-1, cts=-1, txbuf=256, rxbuf=256, timeout=1, timeout_char=1)
----------------------------------------
enable config success
probleme communication : reponse vide 
distance_gate_sensitivity_configuration failure
firmware :V 2 . 4 . 23 10 19 15
MAc Address f7 99 9b 63 f7 92
probleme communication : reponse vide 
Distance_resolution_setting failure 
end config success
-----------DECTECTION----------------
error, frame header is incorrect
pas de présence humaine
error, frame header is incorrect
pas de présence humaine


# Micropython
## Firmware - once per device
Get <https://github.com/espressif/esptool>
First, erase flash memory from dir `esptool-maser`

```
cd _archive/esptool
esptool.py --port /dev/cu.usbserial-0275EB94 erase_flash
```
if:
```
A fatal error occurred: Could not open /dev/cu.usbserial-0275EB94, the port is busy or doesn't exist.
([Errno 16] could not open port /dev/cu.usbserial-0275EB94: [Errno 16] Resource busy: '/dev/cu.usbserial-0275EB94')
```
Unconnect & reconnect, immedietly run the command above

Download generic firmware esp wroom:
<https://micropython.org/download/#esp32> / <https://micropython.org/download/ESP32_GENERIC/>
`v1.23.0 (2024-06-02) .bin`

Flash firmware:
```
esptool.py --chip esp32 --port /dev/cu.usbserial-0275EAB2 --baud 460800 write_flash -z 0x1000 ESP32_GENERIC-20240602-v1.23.0.bin 
```


## To upload code
in vscode
- pymakr extension install
- "new project" from sidebar
- `connect device` or three dots when hovering over project name `select devices`
- auf blitz klicken (if greyed out, right click three dots `stop script`)
- zum upload auf "upload wolke" klicken beim hovern over device name (nicht rechtsklick im filebrowser)
- After upload, three dots on device, `hard reset device`

> *Attention*: When changing the `pymakr.conf` file, its changes only take effect after its uploaded to the board. Right click on the `pymakr.conf` file > "pymakr" > "upload to device" before you upload the whole thing

### Death loop exit bzw direkt auf gerät sachen laden
- delete main file directly on the flash memory:
    - pip install oder so rshell & repl
    - `rshell --port /dev/cu.usbserial-0275EAB2`
    - `repl ~ /dev/cu.usbserial-0275EAB2`
    - `ctrl+x = exit`
    - `import os`
    - `os.remove("main.py")`

    0275EB94

# Pymakr.conf
Example:
```
{
    "address": "/dev/cu.usbserial-AB001234",
    "username": "micro",
    "password": "python",
    "sync_folder": "scripts"
}
```

in terminal
```
import os
os.listdir()
os.chdir("libraries")
```

rx_pin = Pin(13)
tx_pin = Pin(12)



Changes
-------
boardled = Pin(37, Pin.OUT)
boardled.off()

print('-----------CONFIGURATION----------------')
uart1 = UART(1, baudrate = 256000, tx=Pin(12), rx=Pin(13), timeout = 1)
# ------
# end changes