//Libraries
#include <RBDdimmer.h> //https://github.com/RobotDynOfficial/RBDDimmer

//Parameters
const int zeroCrossPin  = 7;  // D7 (NOT CHANGABLE) in m0
const int acdPin  = 4;  // PWM PIN!!??
int MIN_POWER  = 0;
int MAX_POWER  = 100;
int POWER_STEP  = 2;
int speed = 50;

//Variables
int power  = 0;

//Objects
dimmerLamp acd(acdPin);

void setup(){
  //Init Serial USB
  Serial.begin(9600);
  Serial.println(F("Initialize System"));
  pinMode(zeroCrossPin, INPUT);
  pinMode(acdPin, OUTPUT);
  acd.begin(NORMAL_MODE, ON);
}

void loop(){
  testDimmer();
}

void testDimmer(){/* function testDimmer */ 
////Sweep light power to test dimmer
  for(power=MIN_POWER;power<=MAX_POWER;power+=POWER_STEP){
    acd.setPower(power); // setPower(0-100%);
      Serial.print("lampValue --> \t");
      Serial.print(acd.getPower());
      Serial.print("\t");
      Serial.println("");
    delay(speed);
  }

  for(power=MAX_POWER;power>=MIN_POWER;power-=POWER_STEP){
    acd.setPower(power); // setPower(0-100%);
      Serial.print("lampValue --> \t");
      Serial.print(acd.getPower());
      Serial.print("\t");
      Serial.println("");
    delay(speed);
  }
}
