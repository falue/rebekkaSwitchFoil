# HLK-LD2450 B et C  (Microwave-based human/object presence sensor) 
#rev 1 DUCROS christian janvier 2024 à partir du fichier 
#rev 1 - shabaz - May 2023
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
# STATE_MOVING_TARGET = 1
# STATE_STATIONARY_TARGET = 2
# STATE_COMBINED_TARGET = 3
# TARGET_NAME = ["no_target", "moving_target", "stationary_target", "combined_target"]

THRESHOLD_CM = 70

class LD2450() :
    
    def __init__(self,bus_uart): 
        self.ser = bus_uart
        print(f"Threshold is {THRESHOLD_CM} cm")
        self.meas = [None, None, None]
        
        self.communication_error = 0 

    def parse_report(self, data):
        # sanity checks
        # self.print_frame_bytes(data)
        # if len(data) != 30:
            # print(f"error, frame length ,ist be 30 but is {len(data)}")
            # return 0
        if data[0:4] != REPORT_HEADER:
            # print(f"error, frame header is incorrect")
            return 0
        
        # Process each chunk of data
        for i in range(3):  # There are 3 chunks in total
            start_index = 4 + i * 8
            end_index = start_index + 8
            chunk = data[start_index:end_index]
            # print('start_index',start_index)
            # print('end_index',end_index)
            # print(f'chunk {i}:', chunk)
            
            if all(b == 0 for b in chunk):
                # Skip chunks that are all zeros and set to None
                self.meas[i] = None
                continue
            
            x = 0 - (chunk[0] + (chunk[1] << 8))  # mm
            y = (chunk[2] + (chunk[3] << 8)) - 2**15  # mm
            speed = 0 - (chunk[4] + (chunk[5] << 8))  # cm/s
            dist_res = chunk[6] + (chunk[7] << 8)  # mm

            meas_data = {
                "x": abs(x - -32768) / 10 if x < -32768 else x / 10,
                "y": y / 10,
                "speed": speed,
                "dist_res": dist_res / 10
            }
            
            self.meas[i] = meas_data
        return 1


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
        #Extraire les octets individuels de chaque valeur -->pour faire little endian 
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
            self.parse_report(report_data) #analyse mesure
            return report_data
        else :
            print("probleme communication : reponse vide ")
            report_data = NULLDATA
            # sanity checks passed. Store the sensor data in meas
            # self.meas["state"] = 0
            # self.meas["x"] = 0
            # self.meas["y"] = 0
            # self.meas["speed"] = 0
            # self.meas["dist_res"] = 0
            self.communication_error = 1
            return report_data
        

    # def print_meas(self):
        # print(f"X axis: {self.meas['x']}")
        # print(f"Y axis: {self.meas['y']}")
        # print(f"Speed axis: {self.meas['speed']}")
        # print(f"Distance resolution: {self.meas['speed']}")

    def get_sensor_measurements(self):
        return self.meas

    # def human_detection(self,led,seuil_stat,seuil_mov):
    #     if self.communication_error :
    #         for i in range (10):
    #             led.on()
    #             utime.sleep(0.1)
    #             led.off()
    #             utime.sleep(0.1)
    #     else: 
    #         print('presence humaine immobile  à ',self.meas['stationary_distance'],'cm')
    #         print('presence humaine en mouvement à ',self.meas['moving_distance'],'cm')
    #         led.on()
    #         return 1
        #else:     
        #    print('pas de présence humaine')
        #    led.off()
        #    return 0