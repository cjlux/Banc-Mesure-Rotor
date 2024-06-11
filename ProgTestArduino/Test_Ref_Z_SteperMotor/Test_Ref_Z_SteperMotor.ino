// 
// Copyright 2024 Jean-luc CHARLES (jean-luc.charles@mailo.com)
// 

///////////////////////////////////////////////////
/////// stepper motors parameters     /////////////
///////////////////////////////////////////////////

// Stepper motor 2: to move vertically the magnetic field sensor
#define STEP_MODE2 1               // used for 1/2, 1/4, 1/8.... microstep mode
#define STEPPER_ANGLE2 1.8         // the angle of one step of the stepper motor
#define DIAM2 9.                   // The diameter (mm) of the stepper motor reductor
#define NBSTEP_PER_REVOL2 200      // number of steps for a full revolution

#define UP 1                       // moves the sensor upward
#define DOWN -1                    // moves the sensor downward
///////////////////////////////////////////////////

#define Zref_velocity 5         // the velocity [mm/s] for reaching the limit switch sensor
#define Z_velocity    10        // the velocity [mm/s] for reaching the limit switch sensor

///////////////////////////////////////////////
// pins for the stepper motor driver A4988   //
///////////////////////////////////////////////
#define pinDIR2 5  // pin for direction of rotation
#define pinPUL2 6  // pin for stepping
#define pinENA2 7  // pin for Enable/disable torque

// The pin of the limit switch sensor:
#define pinLimitSwitch 8 

#define STOP while(1) {;}

/**********************************************************************
/  Declaration of functions functions used in the program
/**********************************************************************/

// Zref_sensor: move the sensor th reach the zero reference:
int Zref_sensor(bool hold_torque=true);

void setup() 
{  
  // set up the stepper motor2 (vertical axis for the magnetic sensor):
  pinMode(pinDIR2, OUTPUT);
  pinMode(pinPUL2, OUTPUT);
  pinMode(pinENA2, OUTPUT);

  digitalWrite(pinDIR2, LOW);
  digitalWrite(pinENA2, HIGH); // disable torque
  digitalWrite(pinPUL2, LOW);

  // The limit switch sensor:
  pinMode(pinLimitSwitch, INPUT_PULLUP);
  
  // Start the serial link:
  Serial.begin(9600);
  
  // Move the sensor to the ref position:
  bool hold_stepper_torque = false;
  Zref_sensor(hold_stepper_torque);
}


void loop() 
{  
  STOP
}

int Zref_sensor(bool hold_torque)
{
  /* To make the stepper motor move the sensor until it reaches the limit switch sensor */

  Serial.print("Stepper motor Z referencing...");

  // move upward:
  digitalWrite(pinDIR2, LOW);

  // apply the motor holding torque:
  digitalWrite(pinENA2, LOW);

  // the required revolution speed [revol/sec] and corresponding period:
  float N_Hz = 2 * Zref_velocity / (M_PI * DIAM2);
  const long unsigned int T_ms = int(1e3 / (N_Hz * NBSTEP_PER_REVOL2));
  String mess = "\nN_Hz: " + String(N_Hz) + ", T_ms: " + String(T_ms);
  Serial.println(mess);

  int limit_state = digitalRead(pinLimitSwitch);
  while (limit_state != HIGH)
  {
    // Send a 5 micro-step pulse with period equals to Tms:
    digitalWrite(pinPUL2, HIGH);
    delayMicroseconds(5);
    digitalWrite(pinPUL2, LOW);
    delay(T_ms);

    limit_state = digitalRead(pinLimitSwitch);
  }

  if (hold_torque == false)
  {
    // disable the motor holding torque:
    digitalWrite(pinENA2, HIGH);
  }
  
  Serial.println(" OK !");

  return 0.;
}
