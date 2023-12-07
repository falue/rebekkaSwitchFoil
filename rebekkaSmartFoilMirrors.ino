/*

  Example-01_Basic.ino

  This demo shows a basic use of a TMF882X device. The device is connected to, 
  and a single reading is taken for each loop iteration. 

  Supported Boards:
  
   SparkFun Qwiic dToF Imager - TMF8820        https://www.sparkfun.com/products/19036
   SparkFun Qwiic Mini dToF Imager - TMF8820   https://www.sparkfun.com/products/19218
   SparkFun Qwiic Mini dToF Imager - TMF8821   https://www.sparkfun.com/products/19451
   SparkFun Qwiic dToF Imager - TMF8821        https://www.sparkfun.com/products/19037
   
  Written by Kirk Benell @ SparkFun Electronics, April 2022

  Repository:
     https://github.com/sparkfun/SparkFun_Qwiic_TMF882X_Arduino_Library

  Documentation:
     https://sparkfun.github.io/SparkFun_Qwiic_TMF882X_Arduino_Library/

  SparkFun code, firmware, and software is released under the MIT License(http://opensource.org/licenses/MIT).
*/

#include "SparkFun_TMF882X_Library.h" //http://librarymanager/All#SparkFun_Qwiic_TMPF882X

SparkFun_TMF882X  myTMF882X;

// Structure to hold the measurement results - this is defined by the TMF882X SDK.

static struct tmf882x_msg_meas_results myResults;

// xxx rollingAvg[9] = [0, 0, 0, 0, 0, 0, 0, 0, 0];
const int numSensors = 9;
const int numMeasurements = 2;
int rollingAverages[numSensors] = {0}; // 1D array for rolling averages
int sensorValues[numSensors][numMeasurements] = {0}; // 2D array to store sensor values
int distanceStartDimCm = 300;  // cm distance from where it should start to fade out from maxDimValue (fully clear)
int distanceStopDimCm = 150;   // cm distance from where dimming is 0 (fully opaque)
int maxDimValue = 1024;  // if furthest, this value is used

void setup() {
    delay(1000);
    Serial.begin(115200);
    Serial.println("");
    Serial.println("In setup");
    Serial.println("==============================");

    // Initialize the TMF882X device
    if(!myTMF882X.begin()) {
        Serial.println("Error - The TMF882X failed to initialize - is the board connected?");
        while(1);
    } else {
      Serial.println("TMF882X started.");
    }
    // The device is now ready for operations
}

void loop() {
    // get a Measurement
    if(myTMF882X.startMeasuring(myResults)) {
        // print out results
        // Serial.println("Measurements!!!\t");
        // Serial.print("     Result Number: "); Serial.print(myResults.result_num);
        // Serial.print("  Number of Results: "); Serial.println(myResults.num_results);       

        for (int i = 0; i < myResults.num_results; ++i) {
            // Serial.print("       conf: "); Serial.print(myResults.results[i].confidence);
            // Serial.print(" distance mm: "); Serial.print(myResults.results[i].distance_mm);
            // Serial.print(" channel: "); Serial.print(myResults.results[i].channel);
            // Serial.print(" sub_capture: "); Serial.println(myResults.results[i].sub_capture);
            updateRollingAverage(myResults.results[i].channel-1, myResults.results[i].distance_mm);
            // updateRollingAverageWithConfidence(myResults.results[i].channel-1, myResults.results[i].confidence, myResults.results[i].distance_mm);
        }
        // Serial.print("     photon: "); Serial.print(myResults.photon_count);    
        // Serial.print(" ref photon: "); Serial.print(myResults.ref_photon_count);
        // Serial.print(" ALS: "); Serial.println(myResults.ambient_light); Serial.println();
    }
    //printAverages();
    int averageCm = averageOfAverages()/10;
    int switchFoil = amountToDim(averageCm);
    Serial.print(averageCm);
    Serial.print("\t");
    Serial.print(switchFoil);
    Serial.println();
    
    delay(15);
}

void updateRollingAverage(int sensorNumber, int newValue) {
  // Shift the old values to make room for the new value
  for (int i = numMeasurements - 1; i > 0; i--) {
    sensorValues[sensorNumber][i] = sensorValues[sensorNumber][i - 1];
  }
  // Add the new value to the array
  sensorValues[sensorNumber][0] = newValue;
  // Recalculate the rolling average
  int sum = 0;
  for (int i = 0; i < numMeasurements; i++) {
    sum += sensorValues[sensorNumber][i];
  }
  rollingAverages[sensorNumber] = sum / numMeasurements;
}

// "Confidence" takes too long to catch up because its low on further distances. means, it takes ages to reset to max distance
void updateRollingAverageWithConfidence(int sensorNumber, int confidence, int newValue) {
  // Calculate the weight based on confidence (range 0 to 1)
  float weight = confidence / 255.0;
  // Shift the old values to make room for the new weighted value
  for (int i = numMeasurements - 1; i > 0; i--) {
    sensorValues[sensorNumber][i] = sensorValues[sensorNumber][i - 1];
  }
  // Calculate the weighted new value
  int weightedNewValue = sensorValues[sensorNumber][0] * (1 - weight) + newValue * weight;
  // Add the weighted new value to the array
  sensorValues[sensorNumber][0] = weightedNewValue;
  // Recalculate the rolling average
  int sum = 0;
  for (int i = 0; i < numMeasurements; i++) {
    sum += sensorValues[sensorNumber][i];
  }
  rollingAverages[sensorNumber] = sum / numMeasurements;
  // Serial.print(sensorNumber);
  // Serial.print(": ");
  // Serial.println(rollingAverages[sensorNumber]);
}

void printAverages() {
  for (int i = 0; i < numSensors; i++) {
    // Serial.print(i+1);
    // Serial.print(": ");
    Serial.print(rollingAverages[i]/10);  // in cm
    Serial.print("\t");
  }
  Serial.print(averageOfAverages()/10);
  Serial.println();
}

int averageOfAverages() {
  int sum = 0;
  for (int i = 0; i < numSensors; i++) {
    sum += rollingAverages[i];
  }
  return sum / numSensors;
}

int amountToDim(int average) {
    if (average >= distanceStartDimCm) {
        return maxDimValue; // Max value
    } else if (average >= distanceStopDimCm && average < distanceStartDimCm) {
        // Map from distanceStopDimCm-distanceStartDimCm to 0-1024
        return map(average, distanceStopDimCm, distanceStartDimCm, 0, maxDimValue);
    } else {
        return 0; // Min value
    }
}


