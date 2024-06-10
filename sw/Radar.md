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