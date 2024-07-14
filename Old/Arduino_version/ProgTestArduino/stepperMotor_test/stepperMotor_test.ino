//
// JLC v1.0 20211/01/22 Programm to test the A4988 driver.
//                      This chip is devoted to drive one stepper motor.
//

//
// GLOBAL variables
//

///////////////////////////////////////////////
// pins for the stepper motor driver A4988   //
///////////////////////////////////////////////
const int pinDir    = 5;  // pin for direction of rotation
const int pinStep   = 6;  // pin for stepping
const int pinEnable = 7;  // pin for Enable/disable torque

///////////////////////////////////////////////////
/////// stepper motors parameters /////////////////
///////////////////////////////////////////////////
#define fullStepAngle_deg 1.8                                       // the step angle of the stepper-motor

#define step_mode 1                                                 // used for 1/2, 1/4, 1/8.... step mode

const float stepAngle_deg = fullStepAngle_deg/step_mode;            // the Left Right motors step angle
const float stepAngle_rad = fullStepAngle_deg/step_mode*M_PI/180.;  // the Left Right motors step angle
const int nbStepPerRevol  = int(360./stepAngle_deg);                // number of steps for a full revolution

int dir = 1;             // stepper rotation direction
bool done = false;
bool singleShot = true; // to choose singleshot or continuous mode

// macros usefull to write on digital pins:
#define CLR(x,y) (x &= (~(1 << y)))
#define SET(x,y) (x |= (1 << y))


void makeStepperTurn(int dir, 
                     float angle, 
                     float stepAngle, 
                     float nbRevolPerSec,  
                     bool releaseTorque = true)
{
  // dir          : stepper rotation direction (1 or -1)
  // angle        : motor rotation angle to do
  // stepAngle    : stepper motor angle (degrees) for a single step
  // nbRevolPerSec: stepper motor sped -> number of revolutions per second
  // releaseTorque: to realease torque or not after the rotation ?
  
  const float nbRevol   = 360./angle;
  const float timeDelay = 1000./(nbRevolPerSec*nbStepPerRevol);   // delay (ms) between 2 steps
  const int totNbStep   = angle/stepAngle;
  
  Serial.print("RPS:");
  Serial.print(nbRevolPerSec);
  Serial.print(", timeDelay [ms]:");
  Serial.println(timeDelay);
  
  if (dir == 1) 
  {
     digitalWrite(pinDir, LOW) ;    // select rotation direction
  } 
  else 
  {
    digitalWrite(pinDir, HIGH) ;    // select rotation direction
  }

  digitalWrite(pinEnable, LOW);  // apply torque
  
  for(int i=0; i < totNbStep; i++)
  {
     digitalWrite(pinStep, HIGH);
     delayMicroseconds(2);
     digitalWrite(pinStep, LOW);
     delay(timeDelay);
  }
  if (releaseTorque) digitalWrite(pinEnable, HIGH);  // release torque
}

void setup()
{
  Serial.begin(9600);           // set up Serial link speed at 9600 bps
  Serial.println("\n\nDriver A4988 test begins...");
  Serial.print("Full step angle [°]: "); Serial.println(fullStepAngle_deg);
  Serial.print("Step mode          : 1/"); Serial.println(step_mode);
  Serial.print("Step angle      [°]: "); Serial.println(stepAngle_deg);
  Serial.print("Step angle     [rd]: "); Serial.println(stepAngle_rad);
  Serial.print("nb step per revol. : "); Serial.println(nbStepPerRevol);

  // set up the switch pin as an input and Leds as output
  pinMode(pinDir, OUTPUT);
  pinMode(pinStep, OUTPUT);
  pinMode(pinEnable, OUTPUT);

  digitalWrite(pinDir, LOW);
  digitalWrite(pinEnable, HIGH); // disable torque
}

float speedRPS = 1.;   // motor speed (Revolution Per Second)

void loop()
{
  dir = -dir;

  if (singleShot && !done)
  {
    for (speedRPS=0.5; speedRPS <= 2.; speedRPS += 0.25)
    {
      Serial.print("\nSpeedRPS [RPS]: "); Serial.println(speedRPS);
      makeStepperTurn(dir, 3*360., stepAngle_deg, speedRPS, true);
     delay(1000);
     dir = -dir;
    }
    done = true;
  }
  else if (!singleShot)
  {
    Serial.print("\nSpeedRPS [RPS]: "); Serial.println(speedRPS);
    // if singleshot is not true, run makeStepperTurn every loop turn
    makeStepperTurn(dir, 53360.*nbStepPerRevol, stepAngle_deg, speedRPS, true);
    dir = -dir;
    delay(1000);
  }
}
