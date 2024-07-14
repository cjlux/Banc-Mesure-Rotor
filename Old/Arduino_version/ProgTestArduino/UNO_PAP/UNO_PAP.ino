
#define STOP while(1) {;}

///////////////////////////////////////////////
// pins for the stepper motor driver A4988   //
///////////////////////////////////////////////
const int pinDIR = 2;  // pin for direction of rotation
const int pinPUL = 3;  // pin for stepping
const int pinENA = 4;  // pin for Enable/disable torque

unsigned long t0, t1;

///////////////////////////////////////////////////
/////// stepper motors parameters /////////////////
///////////////////////////////////////////////////
#define step_mode 1                                                 // used for 1/2, 1/4, 1/8.... step mode

#define STEPPER_ANGLE 1.8
// NBSTEP defines the numbers steps of the stepper motor for one rotor rotation:
#define NBSTEP 8              // 4 -> step angle of the ROTOR = 4*1.6/6 = 1.2°
                                // 8 -> step angle of the ROTOR = 8*1.6/6 = 2.4°

#define RATIO 6.

const int nbStepPerRevol  = int(360./STEPPER_ANGLE);                // number of steps for a full revolution

// macros usefull to write on digital pins:
#define CLR(x,y) (x &= (~(1 << y)))
#define SET(x,y) (x |= (1 << y))


const float step_angle = STEPPER_ANGLE*NBSTEP/RATIO;
# define NB_REVOL_PER_SEC 0.5

const float time_delay_ms = 1e3/(NB_REVOL_PER_SEC*nbStepPerRevol);

void setup() 
{
  // set up the switch pin as an input and Leds as output
  pinMode(pinDIR, OUTPUT);
  pinMode(pinPUL, OUTPUT);
  pinMode(pinENA, OUTPUT);

  digitalWrite(pinDIR, LOW);
  digitalWrite(pinENA, HIGH); // disable torque
  digitalWrite(pinPUL, LOW);
  
  // Start the serial link:
  Serial.begin(9600);
}

void loop() 
{
  // Enable motor current:
  digitalWrite(pinENA, LOW);
  
  float angle = 0;

  // scan angle from 0 to 360°:
  int count = 0;
  while(angle < 360)
  {
    t0 = millis();
    
    // Make the stepper motor do the steps:
    for(int i=0; i < NBSTEP; i++) 
    {
      digitalWrite(pinPUL, HIGH);
      delayMicroseconds(20);
      digitalWrite(pinPUL, LOW);
      delay(time_delay_ms);
    }

    angle = step_angle*count;

    t1 = millis();
    while (t1 - t0 < 1000UL)
    {
      t1 = millis();
    }

    count += 1;
  }
  // release motor torque:
  digitalWrite(pinENA, HIGH);
 
  STOP
}
