# HLK-LD2450 B et C  (Microwave-based human/object presence sensor) 
#rev 1 DUCROS christian janvier 2024 à partir du fichier 
#rev 1 - shabaz - May 2023
#rev 3 - fabian - Jun 2024
import  utime

#------------ 2.1 Command protocol frame format---------------
HEADER = bytes([0xfd, 0xfc, 0xfb, 0xfa])
TERMINATOR = bytes([0x04, 0x03, 0x02, 0x01])
#----------- 2.3 Reported data frame format-------------------
# Example data report in Basic mode:
#  aa ff 03 00 35 01 e5 82 00 00 68 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 55 cc
REPORT_HEADER = bytes([0xaa, 0xff, 0x03, 0x00])
REPORT_TERMINATOR = bytes([0x55, 0xcc])

NULLDATA = bytes([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]) #no response --> ack = 0 donc failure

STATE_NO_TARGET = 0
STATE_MOVING_TARGET = 1
STATE_STATIONARY_TARGET = 2
STATE_COMBINED_TARGET = 3
TARGET_NAME = ["no_target", "moving_target", "stationary_target", "combined_target"]

THRESHOLD_CM = 7000

class LD2450() :
    
    def __init__(self,bus_uart): 
        self.ser = bus_uart
        print(f"Threshold is {THRESHOLD_CM} cm")
        self.meas = {
                "state": STATE_NO_TARGET,
                "moving_distance": 0,
                "moving_energy": 0,
                "stationary_distance": 0,
                "stationary_energy": 0,
                "detection_distance": 0 }
        
        self.communication_error = 0 

    def parse_report(self,data):
        # sanity checks
        #self.print_frame_bytes(data)  #####
        if len(data) != 30:
            # print(f"error, frame length ,ist be 30 but is {len(data)}")
            return 0
        if data[0:4] != REPORT_HEADER:
            # print(f"error, frame header is incorrect")
            return 0
        # sanity checks passed. Store the sensor data in meas
        x = 0 - data[4] + (data[5] << 8)
        d = (data[6] + (data[7] << 8)) -  2**15
        from machine import Pin
        boardled = Pin(13, Pin.OUT)
    
        if d/10 < 70:
            boardled.on()
        else:
            boardled.off()
        #print(f"X = {x/10} cm")
        #print(f"Distance = {d/10} cm")
        #print(f"Speed = {data[8] + (data[9] << 8)} cm/s")
        
        self.meas["moving_distance"] = data[8] + (data[9] << 8)
        self.meas["moving_energy"] = data[11]
        self.meas["stationary_distance"] = data[12] + (data[13] << 8)
        self.meas["stationary_energy"] = data[14]
        self.meas["detection_distance"] = data[15] + (data[16] << 8)
        return data
        return 1  ######
          

    #---------fonctions communes configuration ----------
    #affichage des frames - Utiliser pour debugger
    def print_frame_bytes(self,data):  
        try :                      
            text = f"hex: "
            for i in range(0, len(data)):
                text = text + f" {data[i]:02x}"
            print(text)
        except :
            pass
    #flush : vidange du buffer (lecture des datas)
    def serial_flush(self):
        dummy = self.ser.read()
        #return dummy

     #----------------Send command with ACK------------------------------------
    def send_command(self, cmd_values):
        cmd_data_len = bytes([len(cmd_values), 0x00]) #little endian
        frame = HEADER + cmd_data_len + cmd_values + TERMINATOR
        self.ser.write(frame)
        #print(frame)#debug
        #self.serial_flush() 
        utime.sleep_ms(20)
        #----------------reception  message----------------
        if self.ser.any() > 0: 
            #Lire le message reçu
            response = self.ser.read()
            #self.print_frame_bytes(response) # debug
            if len(response) <10 :
                response = NULLDATA
            return response
        else :
            print("probleme communication : reponse vide ")
            response = NULLDATA
            return response
 
    #2.2.1 
    def enable_config(self):
        cmd = 0x00FF
        value = 0x0001
        #Extraire les octets individuels de chaque valeur -->pour faire little endian 
        octet1_cmd = (cmd & 0xFF00) >> 8
        octet2_cmd = cmd & 0x00FF
        octet1_value = (value & 0xFF00) >> 8
        octet2_value = value & 0x00FF
        # Créer la séquence d'octets en ordre spécifié
        cmd_value = bytes([octet2_cmd, octet1_cmd, octet2_value, octet1_value])
        response = self.send_command(cmd_value)
        if response[7] :
            print('enable config success')
            return 1
        else :
            print('enable config failure')
            return 0
        
    #2.2.2
    def end_config(self):
        cmd = 0x00FE
        value = None
        #Extraire les octets individuels de chaque valeur -->pour faire little endian 
        octet1_cmd = (cmd & 0xFF00) >> 8
        octet2_cmd = cmd & 0x00FF
        cmd_value = bytes([octet2_cmd, octet1_cmd])
        response = self.send_command(cmd_value)
        if response[7] :
            print('end config success')
            return 1
        else :
            print('end config failure')
            return 0
        
     
        
    #2.2.4 # A finir parser
    def read_parameter(self):
        cmd = 0x0061
        value = None
        #Extraire les octets individuels de chaque valeur -->pour faire little endian 
        octet1_cmd = (cmd & 0xFF00) >> 8
        octet2_cmd = cmd & 0x00FF
        cmd_value = bytes([octet2_cmd, octet1_cmd])
        response = self.send_command(cmd_value)
        self.print_frame_bytes(response)
        if response[7] :
            print('read parameter success')
            return response
        else :
            print('read parameter failure')
            return 0   

          
    #2.2.8
    def read_firmware_version(self):
        cmd = 0x00A0
        value = None
        #Extraire les octets individuels de chaque valeur -->pour faire little endian 
        octet1_cmd = (cmd & 0xFF00) >> 8
        octet2_cmd = cmd & 0x00FF
        cmd_value = bytes([octet2_cmd, octet1_cmd])
        response = self.send_command(cmd_value)
        if response[7] :
            response_12 = hex(response[12])[2:]
            response_13 = hex(response[13])[2:]
            response_14 = hex(response[14])[2:]
            response_15 = hex(response[15])[2:]
            response_16 = hex(response[16])[2:]
            response_17 = hex(response[17])[2:]
            print('firmware :V',response_13,'.',response_12,'.',response_17,response_16,response_15,response_14)
        else :
            print('read firmware version failure')
            return 0
         
    #2.2.10
    def restore_factory_settings(self):
        cmd = 0x00A2
        value = None
        #Extraire les octets individuels de chaque valeur -->pour faire little endian 
        octet1_cmd = (cmd & 0xFF00) >> 8
        octet2_cmd = cmd & 0x00FF
        cmd_value = bytes([octet2_cmd, octet1_cmd])
        response = self.send_command(cmd_value)
        if response[7] :
            print('restore_factory_settings success')
            return 1
        else :
            print('restore_factory_settings failure')
            return 0
               
    #2.2.11
    def reboot_module(self): 
        cmd = 0x00A3
        value = None
        #Extraire les octets individuels de chaque valeur -->pour faire little endian 
        octet1_cmd = (cmd & 0xFF00) >> 8
        octet2_cmd = cmd & 0x00FF
        cmd_value = bytes([octet2_cmd, octet1_cmd])
        response = self.send_command(cmd_value)
        if response[7] :
            print('reboot module success')
            return 1
        else :
            print('reboot module failure')
            return 0
            
    #2.2.13
    def get_mac_address(self) : 
        cmd = 0x00A5
        value = 0x0001
        #Extraire les octets individuels de chaque valeur -->pour faire little endian 
        octet1_cmd = (cmd & 0xFF00) >> 8
        octet2_cmd = cmd & 0x00FF
        octet1_value = (value & 0xFF00) >> 8
        octet2_value= value & 0x00FF
        # Créer la séquence d'octets en ordre spécifié
        cmd_value = bytes([octet2_cmd, octet1_cmd, octet2_value, octet1_value])
        response = self.send_command(cmd_value)
        if response[7] :
            response_10 = hex(response[10])[2:]
            response_11 = hex(response[11])[2:]
            response_12 = hex(response[12])[2:]
            response_13 = hex(response[13])[2:]
            response_14 = hex(response[14])[2:]
            response_15 = hex(response[15])[2:]
            print('MAc Address',response_10,response_11,response_12,response_13,response_14,response_15)
            return response[10:16]
        else :
            print('get_mac_address failure')
            return 0

            
    #2.3 RADAR data output
    #2.3.1  envoi d'une commande pour recevoir un rapport             
    def send_command_report_data(self) :
        cmd = 0x0000
        value = None
        # Extract individual bytes from each value -->to do little endian
        octet1_cmd = (cmd & 0xFF00) >> 8
        octet2_cmd = cmd & 0x00FF
        cmd_value = bytes([octet2_cmd, octet1_cmd])
        cmd_data_len = bytes([len(cmd_value), 0x00]) #little endian
        frame = REPORT_HEADER + cmd_data_len + cmd_value + REPORT_TERMINATOR
        self.ser.write(frame)
        #print(frame)#debug
        self.serial_flush() 
        utime.sleep_ms(100)  #tempo assez longue pour récupérer les datas
        #----------------reception  message----------------
        if self.ser.any() > 0: 
            #Lire le message reçu
            report_data = self.ser.read()
            #self.print_frame_bytes(report_data) # debug
            return self.parse_report(report_data) #analyse mesure
            return report_data
        else :
            print("probleme communication : reponse vide ")
            report_data = NULLDATA
            # sanity checks passed. Store the sensor data in meas
            self.meas["state"] = 0
            self.meas["moving_distance"] = 0
            self.meas["moving_energy"] = 0
            self.meas["stationary_distance"] = 0
            self.meas["stationary_energy"] = 0
            self.meas["detection_distance"] = 0
            self.communication_error = 1 
            return report_data
        

    def print_measORIGINAL(self):
        print(f"moving distance: {self.meas['moving_distance']}")
        print(f"moving energy: {self.meas['moving_energy']}")
        print(f"stationary distance: {self.meas['stationary_distance']}")
        print(f"stationary energy: {self.meas['stationary_energy']}")
        print(f"detection distance: {self.meas['detection_distance']}")

    
    def print_meas(self):
        print(f"state: {TARGET_NAME[self.meas['state']]}")
        print(f"moving distance: {self.meas['moving_distance']}")
        print(f"moving energy: {self.meas['moving_energy']}")
        print(f"stationary distance: {self.meas['stationary_distance']}")
        print(f"stationary energy: {self.meas['stationary_energy']}")
        print(f"detection distance: {self.meas['detection_distance']}")
    
    def get_meas(self):
        return self.meas
        

    def human_detectionORIGINAL(self,led,seuil_stat,seuil_mov):
        if self.communication_error :
            for i in range (10):
                led.on()
                utime.sleep(0.1)
                led.off()
                utime.sleep(0.1)
        else: 
            print('motionless human presence at ',self.meas['stationary_distance'],'cm')
            print('human presence in movement at ',self.meas['moving_distance'],'cm')
            led.on()
            return 1
        #else:     
        #    print('pas de présence humaine')
        #    led.off()
        #    return 0

    def human_detection(self,led,seuil_stat,seuil_mov):  # threshold_static, threshold_movement
        if self.communication_error :
            for i in range (10) :
                led.on()
                utime.sleep(0.1)
                led.off()
                utime.sleep(0.1)
        elif self.meas['stationary_energy']>seuil_stat or self.meas['moving_energy']>seuil_mov :
            if self.meas['stationary_distance']<self.meas['moving_distance'] :
                print('  Motionless human presence at ',self.meas['stationary_distance'],'cm')
            else :
                print('  Human presence in movement at  ',self.meas['moving_distance'],'cm')
            led.on()
            return 1
        else :     
            print('  no human presence')
            led.off()
            return 0
        