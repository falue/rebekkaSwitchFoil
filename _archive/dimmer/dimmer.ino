//Libraries
#include <RBDdimmer.h> //https://github.com/RobotDynOfficial/RBDDimmer
#include <math.h> // Make sure to include this for the sin() function


//Parameters
const int zeroCrossPin  = 7;  // D7 (NOT CHANGABLE) in m0
const int acdPin  = 4;  // PWM PIN!!??
int MIN_POWER  = 15;
int MAX_POWER  = 40;  // 100
int POWER_STEP  = 1;
int speed = 666;

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

void testDimmer() {
  // Assuming MIN_POWER, MAX_POWER, and POWER_STEP are defined somewhere in your code.
  // Also assuming 'speed' is defined somewhere as the delay time in milliseconds.
  // 'totalSteps' defines the number of steps you want to take to complete one sine wave cycle.
  int totalSteps = 360; 
  double radianStep = (2 * PI) / totalSteps; // Converts steps to radians for the sin function
  for(int step = 0; step < totalSteps; step++) {
    // Calculate the sine value for this step, scaled to the power range.
    double sineValue = sin(step * radianStep); // Sine value ranges from -1 to 1
    double power = ((sineValue + 1) / 2) * (MAX_POWER - MIN_POWER) + MIN_POWER; // Scale and shift

    acd.setPower((int)power); // Assuming setPower expects an integer
    Serial.print("lampValue --> \t");
    Serial.print(acd.getPower());
    Serial.print("\t");
    Serial.print(power);
    Serial.println("");
    delay(speed);
  }
}

void testDimmerXXX(){/* function testDimmer */ 
////Sweep light power to test dimmer
  for(power=MIN_POWER;power<=MAX_POWER;power+=POWER_STEP){
    acd.setPower(power); // setPower(0-100%);
      Serial.print("lampValue --> \t");
      Serial.print(acd.getPower());
      Serial.print("\t");
      Serial.print(power);
      Serial.print("\t");
      Serial.println("");
    delay(speed);
  }

  for(power=MAX_POWER;power>=MIN_POWER;power-=POWER_STEP){
    acd.setPower(power); // setPower(0-100%);
      Serial.print("lampValue --> \t");
      Serial.print(acd.getPower());
      Serial.print("\t");
      Serial.print(power);
      Serial.println("");
    delay(speed);
  }
}
