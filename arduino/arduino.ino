// USED THING !!!

#include <Arduino.h>
// #include <avr/wdt.h>  // FOR ARDUINO
#include "esp_system.h"  // FOR ESP32 / THING PLUS
#include <EEPROM.h>

#define ledPin 13
#define relayPin 19  // "IO19/MISO pin nr 17 bzw 19???"

typedef struct RadarTarget
{
    uint16_t id;         // Target ID
    int16_t x;           // X coordinate, unit: mm
    int16_t y;           // Y coordinate, unit: mm
    int16_t speed;       // Speed, in cm/s
    uint16_t resolution; // Distance resolution, unit: mm
} RadarTarget_t;

RadarTarget_t nowTargets[3]; // Stores the target of the current frame
RadarTarget_t lastTargets[3]; // Store the target of the previous frame

int countLeftToRight = 0; // Number of people from left to right
int countRightToLeft = 0; // Number of people from right to left

int countTime = 0; // Statistical time, sec

int16_t v_th = 17;  // 17; // Pedestrian speed threshold, in cm/s

// Define a global variable to track the last update time
unsigned long lastUpdateTime = 0;
const unsigned long updateIntervalEeprom = 0.5 * 60 * 1000; // 3 minutes = 180000 milliseconds
// const unsigned long updateIntervalEeprom = 1; // 3 minutes = 180000 milliseconds

int leftToRightAddress = 0; // Select an eeprom address for left-to-right traffic count
int rightToLeftAddress = 2; // Select an eeprom address for right-to-left traffic count
int countTimeAddress = 4; // Select an eeprom address for the last update time

void saveCountToEEPROM(int address, int count) {  // Save people flow count to EEPROM
    int storedCount = EEPROM.read(address) | (EEPROM.read(address + 1) << 8);
    if (storedCount != count) {
        EEPROM.write(address, count & 0xFF);
        EEPROM.write(address + 1, (count >> 8) & 0xFF);
    }
}


int readCountFromEEPROM(int address) {  // Read people count from EEPROM
    int storedCount = EEPROM.read(address) | (EEPROM.read(address + 1) << 8);
    return storedCount;
}


void clearEEPROM() {  // Clear EEPROM
    // for (int i = 0; i < EEPROM.length(); i++) {
    //     EEPROM.write(i, 0); // 将每个地址的EEPROM数据清除（设置为0）
    // }
    for (int i = 0; i < 7; i++) {
        EEPROM.write(i, 0); // Only delete the 0123456 address to extend the life, clear the EEPROM data of each address (set to 0)
    }
}


void softwareReset() {
    // ESP32 function to restart the microcontroller
    esp_restart();
    // ARDUINO
    /*wdt_enable(WDTO_15MS); // 开启看门狗定时器，设置超时为15毫秒
    while (1) {
      // 无限循环，等待看门狗重置微控制器
    }*/
}


/**
* Reads radar data and populates an array of RadarTarget objects.
*
* @param rec_buf The buffer that contains the radar data.
* @param len The length of the radar data buffer.
* @param targets An array of RadarTarget objects to store the radar targets.
* @param numTargets The number of radar targets to read.
*
* @return Returns 1 on successful reading of radar data, or 0 if the data is incomplete.
*
* @throws None
**/
int readRadarData(byte rec_buf[], int len, RadarTarget targets[], uint16_t numTargets) {
  // if (radar_serial.available() > 0) {
  //     byte rec_buf[256] = "";
  //     int len = radar_serial.readBytes(rec_buf, sizeof(rec_buf));

      for (int i = 0; i < len; i++) {
          // Check frame header and frame trailer
          if (rec_buf[i] == 0xAA && rec_buf[i + 1] == 0xFF && rec_buf[i + 2] == 0x03 && rec_buf[i + 3] == 0x00 && rec_buf[i + 28] == 0x55 && rec_buf[i + 29] == 0xCC) {
              String targetInfo = ""; // A string that stores target information
              int index = i + 4; // Skip the frame header and the data length field within the frame

              for (int targetCounter = 0; targetCounter < numTargets; targetCounter++) {
                  if (index + 7 < len) {
                      RadarTarget target;
                      target.x = (int16_t)(rec_buf[index] | (rec_buf[index + 1] << 8));
                      target.y = (int16_t)(rec_buf[index + 2] | (rec_buf[index + 3] << 8));
                      target.speed = (int16_t)(rec_buf[index + 4] | (rec_buf[index + 5] << 8));
                      target.resolution = (uint16_t)(rec_buf[index + 6] | (rec_buf[index + 7] << 8));

                      // debug_serial.println(target.x);
                      // debug_serial.println(target.y);
                      // debug_serial.println(target.speed);

                      // Check the highest bit of x and y and adjust the sign
                      if (rec_buf[index + 1] & 0x80) target.x -= 0x8000;
                      else target.x = -target.x;
                      if (rec_buf[index + 3] & 0x80) target.y -= 0x8000;
                      else target.y = -target.y;
                      if (rec_buf[index + 5] & 0x80) target.speed -= 0x8000;
                      else target.speed = -target.speed;

                      // Assign target information
                      // debug_serial.println(targetCounter + 1);
                      targets[targetCounter].id = targetCounter + 1;
                      targets[targetCounter].x = target.x;
                      targets[targetCounter].y = target.y;
                      targets[targetCounter].speed = target.speed;
                      targets[targetCounter].resolution = target.resolution;

                      // // Output target information
                      // debug_serial.print("Target ");
                      // debug_serial.print(++targetCounter); // Increase the target counter and output
                      // debug_serial.print(": X: ");
                      // debug_serial.print(target.x);
                      // debug_serial.print("mm, Y: ");
                      // debug_serial.print(target.y);
                      // debug_serial.print("mm, speed: ");
                      // debug_serial.print(target.speed);
                      // debug_serial.print("cm/s, Distance resolution: ");
                      // debug_serial.print(target.resolution);
                      // debug_serial.print("mm; ");

                      // Add target information to string
                      // targetInfo += "目标 " + String(targetCounter + 1) + ": X: " + target.x + "mm, Y: " + target.y + "mm, 速度: " + target.speed + "cm/s, 距离分辨率: " + target.resolution + "mm; ";
                      targetInfo += "target " + String(targetCounter + 1) + ": X: " + target.x + "mm, Y: " + target.y + "mm, speed: " + target.speed + "cm/s, distance resolution: " + target.resolution + "mm; ";

                      index += 8; // Move to the start position of the next target data
                  }
              }

              // Output target information
              // debug_serial.println(targetInfo);

              // Output raw data
              // debug_serial.print("Raw data: ");
              for (int j = i; j < i + 30; j++) {
                  if (j < len) {
                      // debug_serial.print(rec_buf[j], HEX);
                      // debug_serial.print(" ");
                  }
              }
              // debug_serial.println("\n"); // Wrap, prepare to output the next frame of data

              i = index; // Update the index of the outer loop
          }
          // else return 0; // If the data is incomplete, return -1
      }
      return 1;
  // }
  // else return 0;  // The serial port buffer is empty, and returns 0
}


void setup() {
  // Initialize LEDs
  pinMode(ledPin, OUTPUT);
  pinMode(relayPin, OUTPUT);
  digitalWrite(ledPin, HIGH);

  Serial.begin(115200);    // Serial port for PC communication  ... 74880 funktioniert
  Serial2.begin(115200); // Serial port for communicating with radar module, baud rate 256000
  delay(10);

  Serial.println("People counting system... Start");
  Serial.println("Start - Start - Start - Start - Start - Start - Start - Start");

  digitalWrite(relayPin, HIGH);
  digitalWrite(ledPin, HIGH);
  Serial.println("HIGH");
  delay(666);
  digitalWrite(relayPin, LOW);
  digitalWrite(ledPin, LOW);
  Serial.println("LOW");
  delay(666);

  digitalWrite(relayPin, HIGH);
  digitalWrite(ledPin, HIGH);
  Serial.println("HIGH");
  delay(666);
  digitalWrite(relayPin, LOW);
  digitalWrite(ledPin, LOW);
  Serial.println("LOW");
  delay(666);

  digitalWrite(relayPin, HIGH);
  digitalWrite(ledPin, HIGH);
  Serial.println("HIGH");
  delay(666);
  digitalWrite(relayPin, LOW);
  digitalWrite(ledPin, LOW);
  Serial.println("LOW");
  delay(666);

  digitalWrite(relayPin, HIGH);
  digitalWrite(ledPin, HIGH);
  Serial.println("HIGH");
  delay(666);
  digitalWrite(relayPin, LOW);
  //digitalWrite(ledPin, LOW);
  Serial.println("LOW");
  delay(666);

  // Read data and initialize it to the last stored crowd count
  Serial.println("Data read from EEPROM: ");
  Serial.print("Counting people flow from left to right: ");  
  Serial.println(readCountFromEEPROM(leftToRightAddress));
  Serial.print("Counting people flow from right to left: ");
  Serial.println(readCountFromEEPROM(rightToLeftAddress));
  Serial.print("Statistical time in seconds: ");
  Serial.println(readCountFromEEPROM(countTimeAddress));

  countLeftToRight = readCountFromEEPROM(leftToRightAddress);
  countRightToLeft = readCountFromEEPROM(rightToLeftAddress);
  countTime = readCountFromEEPROM(countTimeAddress);

  // Setting the watchdog - used when in arduino !
  /// MCUSR = 0;
  /// wdt_disable();
  Serial.println("BOOTED - BOOTED - BOOTED - BOOTED - BOOTED - BOOTED - BOOTED - BOOTED");
}


void loop() {
  // digitalWrite(ledPin, LOW);
  Serial.println();
  // Serial.print("system time: ");
  // Serial.println(millis());

  if (Serial2.available() > 0) {
    byte rec_buf[256] = "";
    int len = Serial2.readBytes(rec_buf, sizeof(rec_buf));

    int radar_flag = readRadarData(rec_buf, len, nowTargets, 3);
    Serial.print("radar_flag: ");
    Serial.println(radar_flag);

    if (radar_flag == 1) {
      digitalWrite(ledPin, HIGH);
      for (int i = 0; i < 3; i++) {  // Output radar data read
        Serial.print("Target ");
        Serial.print(nowTargets[i].id);
        Serial.print(": X = ");
        Serial.print(nowTargets[i].x);
        Serial.print("mm, Y = ");
        Serial.print(nowTargets[i].y);
        Serial.print("mm, speed = ");
        Serial.print(nowTargets[i].speed);
        Serial.print("cm/s, Distance resolution = ");
        Serial.print(nowTargets[i].resolution);
        Serial.print("mm; \n");
      }

      // Count the flow of people from left to right and from right to left
      for (int i = 0; i < 3; i++) { // Check each target
        if (nowTargets[i].y != 0) { // Assume that the y coordinate is 0, indicating that the target does not exist.
            // Check if the target moves from left to right
            if (abs(nowTargets[i].speed) >= v_th && abs(lastTargets[i].speed) >= v_th  && nowTargets[i].x < lastTargets[i].x) {
                countLeftToRight++;
                // countLeftToRight+=10;
            }
            // Check if the target moves from right to left
            else if (abs(nowTargets[i].speed) >= v_th && abs(lastTargets[i].speed) >= v_th  && nowTargets[i].x > lastTargets[i].x) {
                countRightToLeft++;
                // countRightToLeft+=10;
            }
        }
        lastTargets[i] = nowTargets[i]; // Update the target information of the previous frame
      }    

      // Print statistics results
      Serial.print("Number of people from left to right: ");
      Serial.println(countLeftToRight);
      Serial.print("Number of people from right to left: ");
      Serial.println(countRightToLeft);

      // Check if 3 minutes have passed
      Serial.print("Intervals: ");
      Serial.println(millis() - lastUpdateTime);
      
      if ((millis() - lastUpdateTime) >= updateIntervalEeprom) {
        countTime = countTime + (int)(millis() - lastUpdateTime)/1000;
        Serial.println(countTime);
        // Update data in EEPROM
        Serial.println("Update data in EEPROM");
        if (countLeftToRight != readCountFromEEPROM(leftToRightAddress)) saveCountToEEPROM(leftToRightAddress, countLeftToRight);
        if (countRightToLeft != readCountFromEEPROM(rightToLeftAddress)) saveCountToEEPROM(rightToLeftAddress, countRightToLeft);
        if (countTime != readCountFromEEPROM(countTimeAddress)) saveCountToEEPROM(countTimeAddress, countTime);

        // Update last updated time
        lastUpdateTime = millis();

        // Reading Data
        Serial.println("Data read from EEPROM: ");
        Serial.print("Count of people flow from left to right: ");
        Serial.println(readCountFromEEPROM(leftToRightAddress));
        Serial.print("Count of people flow from right to left: ");
        Serial.println(readCountFromEEPROM(rightToLeftAddress));
        Serial.print("Statistical time seconds: ");
        Serial.println(readCountFromEEPROM(countTimeAddress));
      }
    }


  }
  else {
    digitalWrite(ledPin, LOW);
    delay(1);
  }

  if (Serial.available() > 0) { // reset
        digitalWrite(ledPin, HIGH);
        // If there is data to read from the serial port, read the string until a newline character is encountered
        String command = Serial.readStringUntil('\n');

        // Check if the received command is "FAC"
        if (command == "FAC") {
            clearEEPROM();
            Serial.println();
            Serial.println("EEPROM cleared");
            Serial.println("Restart . . .");
            softwareReset();  // Restart Arduino
        }
        else {
          // Reset EEPROM or so?
            Serial.println();
            Serial.println("Invalid command");
            Serial.println("Send FAC to restore factory settings");
            digitalWrite(ledPin, LOW);
        }
    }

    else digitalWrite(ledPin, LOW);


    // if (Serial1.available() > 0) {
    //     byte rec_buf[256] = "";
    //     int len = Serial1.readBytes(rec_buf, sizeof(rec_buf));

    //     for (int i = 0; i < len; i++) {
    //         if (rec_buf[i] == 0xAA && rec_buf[i + 1] == 0xFF && rec_buf[i + 2] == 0x03 && rec_buf[i + 3] == 0x00 && rec_buf[i + 28] == 0x55 && rec_buf[i + 29] == 0xCC) {
    //             String targetInfo = ""; // 存储目标信息的字符串
    //             int index = i + 4; // 跳过帧头和帧内数据长度字段

    //             for (int targetCounter = 0; targetCounter < 3; targetCounter++) {
    //                 if (index + 7 < len) {
    //                     RadarTarget target;
    //                     target.x = (int16_t)(rec_buf[index] | (rec_buf[index + 1] << 8));
    //                     target.y = (int16_t)(rec_buf[index + 2] | (rec_buf[index + 3] << 8));
    //                     target.speed = (int16_t)(rec_buf[index + 4] | (rec_buf[index + 5] << 8));
    //                     target.resolution = (uint16_t)(rec_buf[index + 6] | (rec_buf[index + 7] << 8));

    //                     // 检查x和y的最高位，调整符号
    //                     Serial.println(target.x);
    //                     Serial.println(target.y);
    //                     Serial.println(target.speed);
    //                     if (rec_buf[index + 1] & 0x80) target.x -= 0x8000;
    //                     else target.x = -target.x;
    //                     if (rec_buf[index + 3] & 0x80) target.y -= 0x8000;
    //                     else target.y = -target.y;
    //                     if (rec_buf[index + 5] & 0x80) target.speed -= 0x8000;
    //                     else target.speed = -target.speed;

    //                     // // 输出目标信息
    //                     // Serial.print("目标 ");
    //                     // Serial.print(++targetCounter); // 增加目标计数器并输出
    //                     // Serial.print(": X: ");
    //                     // Serial.print(target.x);
    //                     // Serial.print("mm, Y: ");
    //                     // Serial.print(target.y);
    //                     // Serial.print("mm, 速度: ");
    //                     // Serial.print(target.speed);
    //                     // Serial.print("cm/s, 距离分辨率: ");
    //                     // Serial.print(target.resolution);

    //                     // 添加目标信息到字符串
    //                     targetInfo += "目标 " + String(targetCounter + 1) + ": X: " + target.x + "mm, Y: " + target.y + "mm, 速度: " + target.speed + "cm/s, 距离分辨率: " + target.resolution + "mm; ";

    //                     index += 8; // 移动到下一个目标数据的开始位置
    //                 }
    //             }

    //             // 输出目标信息
    //             Serial.println(targetInfo);

    //             // 输出原始数据
    //             Serial.print("原始数据: ");
    //             for (int j = i; j < i + 30; j++) {
    //                 if (j < len) {
    //                     Serial.print(rec_buf[j], HEX);
    //                     Serial.print(" ");
    //                 }
    //             }
    //             Serial.println("\n"); // 换行，准备输出下一帧数据

    //             i = index; // 更新外部循环的索引
    //         }
    //     }
    // }


}
