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
#include <Adafruit_NeoPixel.h>  // onboard LED
#define LED_PIN    40
#define LED_COUNT 1
Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);

#include "SparkFun_TMF882X_Library.h" //http://librarymanager/All#SparkFun_Qwiic_TMPF882X

SparkFun_TMF882X  myTMF882X;

// Structure to hold the measurement results - this is defined by the TMF882X SDK.

static struct tmf882x_msg_meas_results myResults;

int distanceStartDimMm = 3000;  // mm distance from where it should start to fade out from maxDimValue (fully clear)
int distanceStopDimMm = 1500;   // mm distance from where dimming is 0 (fully opaque)
int maxDimValue = 255;  // if furthest, this value is used

// Leave me alone
const int numSensors = 9;
const int numMeasurements = 3;
long rollingAverages[numSensors] = {0}; // 1D array for rolling averages
int groundTruth[numSensors] = {5000}; // 1D array for rolling averages
int deviation[numSensors] = {0}; // 1D array for differences between measurement, groundTruth
long sensorValues[numSensors][numMeasurements] = {0}; // 2D array to store sensor values
int deadZone = 100;  // +/- allowed noise/deviation
int confidenceBooster = 1;  // boost confidence in measurement. 1 = not so sure (slowly changing values), 2 = twice as sure (faster changing), etc

/*

TODO:
NEEDS TO ESTABLISH STATUS QUO / GROUND TRUTH OF CURRENT ROOM
right now it detects everything between 300 and 150cm.
if it faces a wall, that does the dimming.

have a rolling average of the whole situation (during setup()? but then the user who plugs it in is in the way).
calculate deviation to current measure, use that as dimming value.

OR:
detect deviation by change in values.
but then it's not better than a normal UV sensor.

*/

void setup() {
    strip.begin();
    strip.show();
    strip.setPixelColor(0, 0, 0, 255);
    strip.show();
    
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

    // Establish ground truth (measure room)
    for (int i = 0; i < 100; ++i) {
      strip.setPixelColor(0, 255, 255, 255);
      strip.show();
      if(myTMF882X.startMeasuring(myResults)) {
          for (int i = 0; i < myResults.num_results; ++i) {
              updateRollingAverage(true, myResults.results[i].channel-1, myResults.results[i].distance_mm);
              // updateRollingAverageWithConfidence(true, myResults.results[i].channel-1, myResults.results[i].distance_mm);
          }
      }
      Serial.print("Collecting ground truths ");
      Serial.print(i);
      Serial.print("%..\t");
      printAverages(groundTruth);
      strip.setPixelColor(0, 0, 0, 255);
      strip.show();
      delay(75);
    }

    // Set current sensor values to ground truth
    // memcpy(sensorValues, groundTruth, sizeof(sensorValues)); ==> makes garbage

    strip.setPixelColor(0, 0, 255, 0);
    strip.show();
    Serial.println("==============================");
    Serial.println("Calibration finished!");
    Serial.println("==============================");
}

void loop() {

    Serial.print(2500);
    Serial.print("\t");

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
            updateRollingAverage(false, myResults.results[i].channel-1, myResults.results[i].distance_mm);
            // updateRollingAverageWithConfidence(false, myResults.results[i].channel-1, myResults.results[i].confidence  *  confidenceBooster , myResults.results[i].distance_mm);
        }
        // Serial.print("     photon: "); Serial.print(myResults.photon_count);    
        // Serial.print(" ref photon: "); Serial.print(myResults.ref_photon_count);
        // Serial.print(" ALS: "); Serial.println(myResults.ambient_light); Serial.println();
    }

    // printAverages(rollingAverages);
    printAverages(deviation);
    if(somethingAnywhere()) {
      Serial.println("SOMETHING THERE 8==============================D'`-^_°__o.");

      int averageMm = averageOfAverages();
      int switchFoil = amountToDim(averageMm);

      /*Serial.print(averageMm);
      Serial.print("\t");
      Serial.print(switchFoil);
      Serial.println();*/

      strip.setPixelColor(0, switchFoil, 0, 0);
      // strip.setPixelColor(0, 255, 0, 0);
      strip.show();

    } else {
      Serial.println("");
      strip.setPixelColor(0, 0, 255, 0);
      strip.show();
    }

    
    delay(15);
}

void updateRollingAverage(boolean setupGroundTruth, int sensorNumber, int newValue) {
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

  if(setupGroundTruth) {
    groundTruth[sensorNumber] = sum / numMeasurements;
  }

  // remove groundTruth of measurement. should always be zero unless
  //   something is different than during startup
  //   (eg something is in the room [eg somONE is in the room])
  rollingAverages[sensorNumber] = sum / numMeasurements;
  deviation[sensorNumber] =  groundTruth[sensorNumber] - rollingAverages[sensorNumber];
}

// "Confidence" takes too long to catch up because its low on further distances. means, it takes ages to reset to max distance
void updateRollingAverageWithConfidence(boolean setupGroundTruth, int sensorNumber, int confidence, int newValue) {
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

  if(setupGroundTruth) {
    groundTruth[sensorNumber] = sum / numMeasurements;
  }

  // remove groundTruth of measurement. should always be zero unless
  //   something is different than during startup
  //   (eg something is in the room [eg somONE is in the room])
  rollingAverages[sensorNumber] = sum / numMeasurements;
  deviation[sensorNumber] =  groundTruth[sensorNumber] - rollingAverages[sensorNumber];
}

void printAverages(int data[]) {
  for (int i = 0; i < numSensors; i++) {
    // Serial.print(i+1);
    // Serial.print(": ");
    Serial.print(data[i]);  // in cm
    Serial.print("\t");
  }
  //Serial.print(averageOfAverages());
  Serial.println();
}

int averageOfAverages() {
  int sum = 0;
  for (int i = 0; i < numSensors; i++) {
    sum += rollingAverages[i];
  }
  return sum / numSensors;
}

int somethingAnywhere() {
  boolean isSomethingThere = false;
  for (int i = 0; i < numSensors; i++) {
    isSomethingThere = deviation[i] > deadZone || deviation[i] < (deadZone*-1);
  }
  return isSomethingThere;
}

int amountToDim(int average) {
    if (average >= distanceStartDimMm) {
        return maxDimValue; // Max value
    } else if (average >= distanceStopDimMm && average < distanceStartDimMm) {
        // Map from distanceStopDimMm-distanceStartDimMm to 0-1024
        return map(average, distanceStopDimMm, distanceStartDimMm, 0, maxDimValue);
    } else {
        return 0; // Min value
    }
}


