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
#define MIN_NB_ZPOS   1         // The min number of vertical position for the magnetic field sensor
#define MAX_NB_ZPOS   5         // The max number of vertical position for the magnetic field sensor
#define ZPOS_MIN      0         // The minimum value of Zpos [mm] for the sensor
#define ZPOS_MAX      130       // The maximum value of Zpos [mm] for the sensor

///////////////////////////////////////////////
// pins for the stepper motor driver A4988   //
///////////////////////////////////////////////
#define pinDIR2 5  // pin for direction of rotation
#define pinPUL2 6  // pin for stepping
#define pinENA2 7  // pin for Enable/disable torque

// The pin of the limit switch sensor:
#define pinLimitSwitch 8 

#define STOP while(1) {;}

char buff[20];              // 
int nb_sensor_pos;          // the number of vertical sensor positions
unsigned long t0, t1;
int Zpos_mm[MAX_NB_ZPOS+1];
int curr_pos, next_pos;
bool hold_stepper_torque = false;

/**********************************************************************
/  Declaration of functions functions used in the program
/**********************************************************************/

// Zmove sensor: move evertically the magnectic sensor:
void Zmove_sensor(int height_mm, int speed_mm_per_sec=10, bool hold_torque=true);

// Zref_sensor: move the sensor th reach the zero reference:
int Zref_sensor(bool hold_torque=true);

// terminal Character user interface to get some parameters values:
int get_param_from_user(String &, int min_value, int max_value, bool confirm);

// to clear the serial buffer:
void clearSerialBuffer();

// macros usefull to write on digital pins:
#define CLR(x,y) (x &= (~(1 << y)))
#define SET(x,y) (x |= (1 << y))

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
  Serial.setTimeout(10000000);

  // Set the first pos to zero:
  Zpos_mm[0] = 0.;
  
  while (true)
  {
    String question("# of vertical positions for the sensor in range [1,5] ? ");
    nb_sensor_pos = get_param_from_user(question, MIN_NB_ZPOS, MAX_NB_ZPOS, false);

    for (int n=1; n <= nb_sensor_pos; n++)
    {
      question = "position #" + String(n) + " from top in mm ? ";
      Zpos_mm[n] = get_param_from_user(question, ZPOS_MIN, ZPOS_MAX, false);
    }

    clearSerialBuffer(); 

    Serial.println("Positions along Z (from top):"); 
    for (int n=1; n <= nb_sensor_pos; n++)
    {
      sprintf(buff, "   pos #%1d: %03u mm", n, Zpos_mm[n]);
      Serial.println(buff);
    }
    
    Serial.println("Do you confirm these values ? y/n ?");
    clearSerialBuffer();     
    while (Serial.available() <= 0) {;}  // wait until user press a key...    
    String input = Serial.readStringUntil('\n');
    if (input == String('y') || input == String('Y'))
    {
      break;
    }
  }
  hold_stepper_torque = false;
  Serial.println("Do you want to hold stepper motor torque ? y/n ?");
  clearSerialBuffer();     
  while (Serial.available() <= 0) {;}  // wait until user press a key...    
  String input = Serial.readStringUntil('\n');
  if (input == String('y') || input == String('Y'))
  {
    hold_stepper_torque = true;
  }

  // Move the sensor to the ref position:
  curr_pos = Zref_sensor(hold_stepper_torque);
}


void loop() 
{  
  int dir;

  // Make some vertical displacements: 
  for (int n=1; n<= nb_sensor_pos; n++)
  {
    String mess = "Current pos is " + String(curr_pos) + "mm, moving to pos#" + String(n) + " at " + String(Zpos_mm[n]) + " mm";
    Serial.print(mess);
    
    // compute the distance of the move:
    int dist = Zpos_mm[n] - curr_pos;

    mess = " - dist: " + String(dist) + " mm";
    if (dist == 0) mess += " SKIPPING";
    Serial.println(mess);

    // make the displacement:
    Zmove_sensor(dist, Z_velocity, hold_stepper_torque);
    curr_pos = Zpos_mm[n];
    
    delay(500);
  }

  for (int n=nb_sensor_pos; n >= 0; n--)
  {
    String mess = "Current pos is " + String(curr_pos) + "mm, moving to pos#" + String(n) + " at " + String(Zpos_mm[n]) + " mm";
    Serial.print(mess);
    
    // compute the distance of the move:
    int dist = Zpos_mm[n] - curr_pos;
    
    mess = " - dist: " + String(dist) + " mm";
    if (dist == 0) mess += " SKIPPING";
    Serial.println(mess);

    // make the displacement:
    Zmove_sensor(dist, Z_velocity, hold_stepper_torque);
    curr_pos = Zpos_mm[n];
    
    delay(500);
  }

  STOP
}

void Zmove_sensor(int dist_mm, int speed_mm_per_sec, bool hold_torque)
{
  /* To make the sensor cart move of 'dist_mm' upward if 'dist_mm' < 0, 
     downward if it is > 0. 
  */

  Serial.print("Zmove_sensor, dist: "); Serial.println(dist_mm);
  
  // nothing to do if dist is null:
  if (dist_mm == 0) return;

  // Set the direction of move:
  if (dist_mm > 0)
  {
    // direction of move is downward:
    digitalWrite(pinDIR2, HIGH);
  }
  else if (dist_mm < 0)
  {
    // direction of move is upward:
    digitalWrite(pinDIR2, LOW);
    dist_mm = -dist_mm;
  }

  // the required revolution speed [revol/sec] and corresponding period:
  const float N_Hz = 2. * speed_mm_per_sec / (M_PI * DIAM2);
  const long unsigned int T_ms = int(1.e3 / (N_Hz * NBSTEP_PER_REVOL2));

  Serial.print("N_Hz: "); Serial.println(N_Hz); Serial.flush();

  // the required number of steps: 
  const int nb_step = int(2. * 180 * dist_mm / (STEPPER_ANGLE2 * M_PI * DIAM2));

  // Let's do the job:

  digitalWrite(pinENA2, LOW);    // apply the motor holding torque:
  digitalWrite(pinPUL2, LOW);    // set the step line LOW

  for (int n=0; n < nb_step; n++)
  {
    t0 = millis();
    
    // Send a 5 micro-step pulse with period equals to Tms:
    digitalWrite(pinPUL2, HIGH);
    delayMicroseconds(10);
    digitalWrite(pinPUL2, LOW);
    delay(T_ms);
  }

  if (hold_torque == false)
  {
    // disable the motor holding torque:
    digitalWrite(pinENA2, HIGH);
  }

  return;
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
  Serial.print("N_Hz: "); Serial.println(N_Hz); Serial.flush();
  Serial.print("T_ms: "); Serial.println(T_ms); Serial.flush();

  int limit_state = digitalRead(pinLimitSwitch);
  while (limit_state != HIGH)
  {
    // Send a 5 micro-step pulse with period equals to Tms:
    digitalWrite(pinPUL2, HIGH);
    delayMicroseconds(10);
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

void clearSerialBuffer()
{
  // read characters from the serial line until there is nothing to read:
  while(Serial.available() > 0) 
  {
    char t = Serial.read();
  }
}

int get_param_from_user(String & m, int min_value, int max_value, bool confirm)
{
  /* To get value for some usefull parameters.
     The value must be in the range [min_value, max_value].
     If confirm is true, a confirmation yes/no about the value is proposed
  */
  clearSerialBuffer();
  int value;                      
  while (true)
  {
    value = min_value -1;                      
    Serial.print(m);
    // wait until data is available on the serial line:
    while (Serial.available() <= 0) {;}  

    while(value < min_value || value > max_value)
    {
      value = Serial.parseInt(); 
    }
    Serial.print(" ");
    Serial.println(value);

    if (confirm)
    {
      clearSerialBuffer();
      Serial.print("You typed "); Serial.print(value); Serial.print(", confirm: y/n ? ");
      // wait until data is available on the serial line:
      while (Serial.available() <= 0) {;}  

      String input = Serial.readStringUntil('\n');
      if (input == String('y') || input == String('Y'))
      {
        break;
      }
    }
    else
      break;
  }
  clearSerialBuffer();
  return value;
}
