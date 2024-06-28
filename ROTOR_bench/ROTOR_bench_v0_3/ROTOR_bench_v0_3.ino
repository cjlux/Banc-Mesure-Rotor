//
// 
// Copyright 2024 Jean-luc CHARLES (jean-luc.charles@mailo.com)
// 
// v0.3  2024/06/27 JLC Version with dialog with Python master program.
//

#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <RTClib.h>
#include <SPI.h>
#include <SD.h>

///////////////////////////////////////////////////
/////// stepper motors parameters       ///////////
/////// DO NOT MODIFY THESE PARAMETERS  ///////////
///////////////////////////////////////////////////

// Stepper motor 1 : to rotate the ROTOR around the vertical axis
#define STEP_MODE1 1               // used for 1/2, 1/4, 1/8.... microstep mode
#define STEPPER_ANGLE1 1.8         // the angle of one step of the stepper motor
#define RATIO1 6.                  // The ratio of the stepper motor reductor
#define NBSTEP_PER_REVOL1 200      // number of steps for a full revolution

// Stepper motor 2: to move vertically the magnetic field sensor
#define STEP_MODE2 1               // used for 1/2, 1/4, 1/8.... microstep mode
#define STEPPER_ANGLE2 1.8         // the angle of one step of the stepper motor
#define DIAM2 9.                   // The diameter (mm) of the stepper motor reductor
#define NBSTEP_PER_REVOL2 200      // number of steps for a full revolution

///////////////////////////////////////////////////

///////////////////////////////////////////////////
/////// Parameters that can be modified ///////////
///////////////////////////////////////////////////
// NBSTEP defines the numbers steps of the stepper motor for one rotor rotation:
#define NBSTEP1 8               // 4 -> step angle of the ROTOR = 4*1.6/6 = 1.2°
                                // 8 -> step angle of the ROTOR = 8*1.6/6 = 2.4°

// NB_REVOL_PER_SEC: the rotation speed of the stepper motor when making NBSTEP steps:
#define NB_REVOL_PER_SEC1 0.5     

// ZMOVE_EVERY_ROTATIONSTEP: make a Z referencing every ZMOVE_EVERY_ROTATIONSTEP rotations of the ROTOR
#define ZREF_EVERY_ROTATIONSTEP 10

#define Zref_velocity 5         // the velocity [mm/s] for reaching the limit switch sensor
#define Z_velocity    15        // the velocity [mm/s] for reaching the limit switch sensor
#define MIN_NB_ZPOS   1         // The min number of vertical position for the magnetic field sensor
#define MAX_NB_ZPOS   5         // The max number of vertical position for the magnetic field sensor
#define ZPOS_MIN      0         // The minimum value of Zpos [mm] for the sensor
#define ZPOS_MAX      130       // The maximum value of Zpos [mm] for the sensor

///////////////////////////////////////////////////

///////////////////////////////////////////////////
////////// Computed parameters ////////////////////
///////////////////////////////////////////////////
const float rotor_step_angle = STEPPER_ANGLE1*NBSTEP1/RATIO1;
const float time_delay_ms = 1e3/(NB_REVOL_PER_SEC1*NBSTEP_PER_REVOL1);
///////////////////////////////////////////////////

///////////////////////////////////////////////
// pins for the stepper motor driver B6600   //
///////////////////////////////////////////////
#define pinDIR1 2  // pin for direction of rotation
#define pinPUL1 3  // pin for stepping
#define pinENA1 4  // pin for Enable/disable torque

///////////////////////////////////////////////
// pins for the stepper motor driver A4988   //
///////////////////////////////////////////////
#define pinDIR2 5  // pin for direction of rotation
#define pinPUL2 6  // pin for stepping
#define pinENA2 7  // pin for Enable/disable torque

// The pin of the limit switch sensor:
#define pinLimitSwitch 8 

///// Emergency STOP button //////
#define pinEmergencyStop 2

// The RTC clock:
RTC_DS1307 RTC;

// The LCD display : 2 lines of 16 characters, I2C adresse : 0x20
LiquidCrystal_I2C lcd(0x20,16,2);  

struct LCD_message
{
  String line0;
  String line1;
} LCD_mess;

// micro SD card AddaFruiton Arduino MEGA2560:
// CLK -> 52
// DO  -> 50
// DI  -> 51
// CS  -> 53
#define chipSelect 53

// set up variables using the SD utility library functions:
Sd2Card card;
SdVolume volume;
SdFile root;
File dataFile;

#define STOP while(1) {;}

bool emergencyStopRequired = false;
int nb_sensor_pos;          // the number of vertical sensor positions
char uniq_file_name[13];    // a uniq file name to write data on SD card
char buff[20];              // "yymmd  hh:mm:ss" -> 16 characters
// char buffers to store sensor values:
char buff16[17], a_buff[6], X_buff[8], Y_buff[8], Z_buff[8];  
String mess;
const String semicol(";");
unsigned long t0, t1;

// Global bariables for Z position:
int Zpos_mm[MAX_NB_ZPOS+1];
int curr_Zpos_mm, next_Zpos_mm;
bool hold_stepper_torque = true;

/**********************************************************************
/  Declaration of functions functions used in the program
/**********************************************************************/

void LCD_display(const String &, int line_number, bool serialprint=true);

// Do_Zmove_sensor: To move the sensor carriage along the Z axis.
void Do_Zmove_sensor(int & curr_pos_mm, int n, bool verbose=false);

// Do_sensor_measurement: make the magnetic field measurements with the sensor
void Do_sensor_measurement(String & line);

// Zmove sensor: core function to move vertically the magnectic sensor:
void Zmove_sensor(int height_mm, int speed_mm_per_sec=10, bool hold_torque=true, bool verbose=false);

// Zref_sensor: move the sensor th reach the zero reference:
int Zref_sensor(bool hold_torque=true, bool verbose=false);

// init_SD_card: initialise the SD reader/writer and chacks if a micro-SD is present:
void init_SD_card();

// terminal Character user interface to get some parameters values:
int get_param_from_user(String &, int min_value, int max_value, bool confirm);

// to write headers in the data file:
void write_headers(char * file_name, int nb_sensor_pos, int * Z_pos_array);

// to clear the serial buffer:
void clearSerialBuffer();

// To read data from the serial line:
String readCharsFromSerial(int nbChars=0);

// The emergency stop ISR:
void emergencyStop();

// To stop the ROTOR bench:
void stopMiniApterros();

// macros usefull to write on digital pins:
#define CLR(x,y) (x &= (~(1 << y)))
#define SET(x,y) (x |= (1 << y))

void setup() 
{
  // set up the stepper motor1 (rotation of the ROTOR):
  pinMode(pinDIR1, OUTPUT);
  pinMode(pinPUL1, OUTPUT);
  pinMode(pinENA1, OUTPUT);

  digitalWrite(pinDIR1, LOW);
  digitalWrite(pinENA1, HIGH); // disable torque
  digitalWrite(pinPUL1, LOW);
  
  // set up the stepper motor2 (vertical axis for the magnetic sensor):
  pinMode(pinDIR2, OUTPUT);
  pinMode(pinPUL2, OUTPUT);
  pinMode(pinENA2, OUTPUT);

  digitalWrite(pinDIR2, LOW);
  digitalWrite(pinENA2, HIGH); // disable torque
  digitalWrite(pinPUL2, LOW);

  // The limit switch sensor:
  pinMode(pinLimitSwitch, INPUT_PULLUP);

  // Since version 0.3, the pinEmergencyStop is pulled up to 5 volt . The Emergency stop button 
  // (normally closed) applies the GND to the pinEmergencyStop: when the emergency button is pressed, 
  // or when the cable is cut, the input level on pinEmergencyStop raises from 0 V to 5 V. That's why 
  // the attachInterrupt() trigers the EmergencyStop function if the level of PinUrgence has a rising edge.
  pinMode(pinEmergencyStop, INPUT_PULLUP);  

  // Configure a "rising edge" signal on pinEmergencyStop to emit an interrupt associated with emergencyStop:
  attachInterrupt(digitalPinToInterrupt(pinEmergencyStop), emergencyStop, RISING);    

  // Start the serial link:
  Serial.begin(115200);
  //Serial.setTimeout(10000000);

  // Start the I2C bus:
  Wire.begin();

  // Start the TRC module:
  RTC.begin();

  // Sets the RTC to the date & time this sketch was compiled
  RTC.adjust(DateTime(__DATE__, __TIME__));

  // Start the LCD display:
  lcd.init();              
  lcd.backlight();

  // Welcome message:
  LCD_display("Welcome to the ", 0, false);
  LCD_display("ROTOR test bench", 1, false);
  Serial.println("[INFO] Welcome to the ROTOR measurement bench");
  delay(3000);
  
  // Initialize SD car reader/writer:
  init_SD_card();

  // Empty USB buffer to begin with a clean buffer...
  clearSerialBuffer();
  delay(500);
  
  // Send hello to the RPi:
  Serial.println("Arduino OK"); Serial.flush();

  // Set the first pos to zero:
  Zpos_mm[0] = 0.;
  
  LCD_display("readChars...", 0, false);
  clearSerialBuffer();
  String positions = readCharsFromSerial(26); // "POS:1%ZMM:10;POS:2%ZMM:30;POS:3%ZMM:40;"
  String ack;
  LCD_display("readChars... OK", 0, false);
  delay(2000);
  LCD_display("decode...", 0, false);
  int ok = decodeZPositions(positions, ack);
  Serial.println(ack);
  LCD_display("decode...OK", 0, false);

  // Move the sensor to the ref position:
  curr_Zpos_mm = 0; //Zref_sensor(hold_stepper_torque);  

  LCD_display("Entering main loop...", 0, false);
  String mess = "Zpos number: " + String(nb_sensor_pos);
  LCD_display(mess, 1, false);
  Serial.println("[INFO] entering main loop...");
}


void loop() 
{
  if (emergencyStopRequired) 
  {
    STOP;
  }

  //String  data = readCharsFromSerial();

  // Enable motor current:
  digitalWrite(pinENA1, LOW);
  
  DateTime now;
  float angle = 0;

  // Open the file for the data:note that only one file can be open at a time,
  // The fine name is "MMDDhhmm.txt" aka "Month Day hour minute.txt" (format FAT 8.3):
  now = RTC.now(); 
  sprintf(uniq_file_name, "%02u%02u%02u%02u.txt", now.month(), now.day(), now.hour(), now.minute());
  
  LCD_display("Uniq file name:", 0);
  LCD_display(uniq_file_name, 1);
  delay(2000);
  
  // open the data filewith the uniq name:
  dataFile = SD.open(uniq_file_name, FILE_WRITE);
  write_headers(uniq_file_name, nb_sensor_pos, Zpos_mm);

  // scan angle from 0 to 360°:
  int count = 0;

  while(true)
  {
    t0 = millis();
    now = RTC.now(); 
    
    angle = rotor_step_angle*count;
    if (angle > 360) break;

    // write the float number in a char buffer on 5 digits with 1 digits after the decimal point:
    dtostrf(angle, 5, 1, a_buff);

    // First line on the LCD display:
    sprintf(buff, "%02u:%02u:%02u", now.hour(), now.minute(), now.second());    
    String line0 = String(buff) + "  " + a_buff;
    LCD_display(line0, 0, false);

    // Now make the mmagnetic field measurement for all the positions of the sensor:
    String line = buff + semicol + a_buff;

    bool Zpos_move_required = count % ZREF_EVERY_ROTATIONSTEP;
    
    if (Zpos_move_required == 0) curr_Zpos_mm = Zref_sensor(hold_stepper_torque);

    int go = count % 2;
    if ( go == 0)
    {
      // Move the sensor donward along Z axis:
      for (int n=1; n<= nb_sensor_pos; n++)
      {
        // Move the sensor to the right Z position:
        Do_Zmove_sensor(curr_Zpos_mm, n, false);
        // Make the sensor measuremnts:
        Do_sensor_measurement(line);
        delay(200);
      }
    }
    else
    {
      // Move the sensor upward along Z axis:
      for (int n=nb_sensor_pos; n >= 1 ; n--)
      {
        // Move the sensor to the right Z position:
        Do_Zmove_sensor(curr_Zpos_mm, n, false);
        // Make the sensor measuremnts:
        Do_sensor_measurement(line);
        delay(200);
      }

    }

    // Write data:
    dataFile.println(line.c_str());
    dataFile.flush();
    Serial.println(line.c_str());

    // Make the stepper motor do the steps to turn the ROTOR of the 'rotor_step_angle' value:
    for(int i=0; i < NBSTEP1; i++) 
    {
      digitalWrite(pinPUL1, HIGH);
      delayMicroseconds(10);
      digitalWrite(pinPUL1, LOW);
      delay(time_delay_ms);
    }
    delay(500);
    // If there is only 1 Z position for the sensor, wait 1 seconde:
    if (nb_sensor_pos == 1)
    {
      t1 = millis();
      while (t1 - t0 < 1000UL)
      {
        t1 = millis();
      }
    }
    count += 1;
  }

  // release motor torque:
  digitalWrite(pinENA1, HIGH);
  
  dataFile.close();

  LCD_display("END of measure", 1);
  STOP
}

void LCD_display(const String & mess, int line_num, bool serialprint)
{
  //
  // Display a message on one of the 2 LCD lines (N°0 ou 1).
  // The line is padded if needed with spaces up to 16 charceters.
  // - mess: the message to display.
  // - line_num: the line numver, 0 or 1.
  // - serialprint: boolean (default: true) to display or not 'mess' on the Serial monitor.
  //
  
  static const String blanks_16 = "                ";   // Blank line of 16 characters ' '
  String mess_16;

  int L = mess.length();
  if (L <16)
    mess_16 = mess + blanks_16.substring(L);
  else 
    mess_16 = mess.substring(0,16);
  
  if (line_num == 1)
  {
    LCD_mess.line1 = String(mess_16);
    lcd.setCursor(0,1);
    lcd.print(LCD_mess.line1);
  }
  else if (line_num == 0)
  {
    LCD_mess.line0 = String(mess_16);
    lcd.setCursor(0,0);
    lcd.print(LCD_mess.line0);
  }
  if (serialprint) Serial.println(mess_16);
}

void Zmove_sensor(int dist_mm, int speed_mm_per_sec, bool hold_torque, bool verbose)
{
  /* To make the sensor cart move of 'dist_mm' upward if 'dist_mm' < 0, 
     downward if it is > 0. 
  */

  if (verbose) 
  {
    Serial.print("Zmove_sensor, dist: "); Serial.println(dist_mm);
  }
  
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

  if (verbose) 
  { 
    Serial.print("N_Hz: "); Serial.println(N_Hz); Serial.flush();
  }

  // the required number of steps: 
  const int nb_step = int(2. * 180 * dist_mm / (STEPPER_ANGLE2 * M_PI * DIAM2));

  // Let's do the job:

  digitalWrite(pinENA2, LOW);    // apply the motor holding torque:
  digitalWrite(pinPUL2, LOW);    // set the step line LOW

  for (int n=0; n < nb_step; n++)
  {   
    // Send a pulse with period equals to Tms:
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

int Zref_sensor(bool hold_torque, bool verbose)
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
  if (verbose) 
  {
    Serial.print("N_Hz: "); Serial.println(N_Hz); Serial.flush();
    Serial.print("T_ms: "); Serial.println(T_ms); Serial.flush();
  }

  int limit_state = digitalRead(pinLimitSwitch);
  while (limit_state != HIGH)
  {
    // Send a pulse with period equals to Tms:
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
  
  if (verbose) Serial.println(" OK !");

  return 0.;
}

void init_SD_card()
{
  Serial.println("[INFO] Init SD card...");
  LCD_display("Init SD card...", 0, false);
  LCD_display("", 1, false);
  delay(2000);
     
  if (!SD.begin(chipSelect)) 
  {
    LCD_display("ERROR: SD card", 0, false);
    LCD_display("", 1, false);
    delay(2000);

    LCD_display("Insert a SD card", 0, false);
    LCD_display("and press RESET", 1, false);
    delay(2000);

    Serial.println("[ERROR] Init SD card.. insert a SD card and press RESET");
    STOP
  }
  else
  {
    Serial.println("[INFO] Init SD card OK");
    LCD_display("Init SD card OK", 0, false);
    LCD_display("", 1, false);
    delay(2000);
  }

  // we'll use the initialization code from the utility libraries
  // since we're just testing if the card is working!
  if (!card.init(SPI_HALF_SPEED, chipSelect)) 
  {
    LCD_display("ERROR: SD card", 0, false);
    LCD_display("       not found", 1, false);
    delay(2000);

    LCD_display("Insert a SD card", 0, false);
    LCD_display("and press RESET", 1, false);
    delay(2000);

    Serial.println("[ERROR] SD card not found: insert a SD card and press RESET");
    STOP
  } 
}

void clearSerialBuffer()
{
  // read characters from the serial line until there is nothing to read:
  while(Serial.available() > 0) 
  {
    char t = Serial.read();
  }
}

String readCharsFromSerial(int nbChars)
{
  //
  // to read chars from USB line. 
  // if nbChars is not null, nbChars characters are red from the serial line, else
  // chars are red until a '\n' is found.
  //
  String data = "";

  if (nbChars > 0)
  {
    // wait for nbChars received in serial buffer:
    while (Serial.available() < nbChars) {;}

    // then read all of them:
    while (Serial.available() > 0) 
    {
      int inChar = Serial.read();
      if ((nbChars == 0) && (inChar == int("\n"))) break;
      data += (char)inChar; 
    }
  }
  else
  {
    // read chars until we get '\n':'
    while (true) 
    {
      int inChar = 0;
      if (Serial.available()) 
        inChar = Serial.read();
      if (inChar == int("\n")) 
        break;
      data += (char)inChar; 
    }    
  }
  
  if (data == "EMERGENCY-STOP")   // End of transmission
  {
    emergencyStopRequired = true;
    stopROTOR_Bench();
  }      
  
  return data;
}

void write_headers(char * file_name, int nb_pos, int * Zpos)
{
  // open the data filewith the uniq name:
  dataFile = SD.open(file_name, FILE_WRITE);

  // Write columns header:
  String line = String("# YYMMDD_hh:mm:ss ; Angle[°]");
  for (int n=1; n<= nb_pos; n++)
  {
    line += " ; X" + String(n) + "_magn [mT] ; Y" + String(n) + "_magn [mT] ; Z" + String(n) + "_magn [mT]";
  }
  line += "\n";
  dataFile.write(line.c_str());
  Serial.print(line.c_str());

  // Write all the Z positions in the header file:
  for (int n=1; n<= nb_pos; n++)
  {
    line = "#  pos " + String(n) + ": " + String(Zpos[n]) + " mm\n";
    dataFile.write(line.c_str());
    Serial.print(line.c_str());
  }
}

void Do_Zmove_sensor(int & curr_pos_mm, int n, bool verbose)
{
  /* To move the sensor carriage along the Z axis.
     Parameters:
     - curr_pos_mm: the current position (in mm) of the sensor along the Z axis,
     - n: the rank of the Z position
     The functions updates the value of 'curr_pos_mm'.
  */

  String mess = "Current pos is " + String(curr_pos_mm) + "mm, moving to pos#" + String(n) + " at " + String(Zpos_mm[n]) + " mm";
  //Serial.print(mess);
  
  // compute the distance of the move to do:
  int dist = Zpos_mm[n] - curr_pos_mm;

  mess = " - dist: " + String(dist) + " mm";
  if (dist == 0) mess += " SKIPPING";
  if (verbose) Serial.println(mess);

  // make the displacement for real: 
  // (Z_velocity & hold_stepper_torque are global variables)
  Zmove_sensor(dist, Z_velocity, hold_stepper_torque, verbose);

  // Update the Z position
  curr_pos_mm = Zpos_mm[n];

  return ;
}

void Do_sensor_measurement(String & line)
{
  // make tke measure (simulations only for now):
  float mag_field_X = random(1, 2000);
  float mag_field_Y = random(1, 2000);
  float mag_field_Z = random(1, 2000);

  mag_field_X /= 1.1;
  mag_field_Y /= 1.2;
  mag_field_Z /= 1.1;

  // write the float number in a char buffer on 7 digits with 2 digits after the decimal point:
  // (X_buff, Y_buff, Z_buff and buff16 are global variables)
  dtostrf(mag_field_X, 7, 2, X_buff);
  line += semicol + X_buff;

  dtostrf(mag_field_Y, 7, 2, Y_buff);
  line += semicol + Y_buff;

  dtostrf(mag_field_Z, 7, 2, Z_buff);
  line += semicol + Z_buff;

  sprintf(buff16, "X%sY%s", X_buff, Y_buff);
  LCD_display(buff16, 1, false);

  return;
}

void emergencyStop() 
{
  Serial.println("EMERGENCY-STOP required");
  emergencyStopRequired = true;
  stopROTOR_Bench();
}

void stopROTOR_Bench()
{
  //
  // This function is called when the emergency-stop button is pressed.
  // It should stop the motors and left the ROTOR bench in s safe state.

  digitalWrite(pinENA1, HIGH);    // release the torque of the shaft stepper motor
  digitalWrite(pinENA2, HIGH);    // release the torque of the Z stepper motor:

  LCD_display("Emergency STOP", 0, false);
  LCD_display("received.", 1, false);

}

int decodeZPositions(const String & data, String & ack)
{
  //
  // To decode the string emitted by the RPi to give the Z positions of the magnetic sensor
  //
  // Arguments:
  //  data -> [IN] const reference to the String like "POS:1%ZMM:10;POS:2%ZMM:30;POS:3%ZMM:40;"
  //  ack  -> [OUT]contains the  acknowlegde string
  //
  // Returned value:
  //  0   -> OK
  // -1   -> malformed data string. No character '%' or ';' or ':' found !
  
  ack = String("");    // empty the ack string
  int start  = 0;      // start processing data at rank 0
  int nb_pos = 0;
  
  int semicol_rank = data.indexOf(";", start);
  if (semicol_rank == -1)
  {
    ack = "ERROR: malformed <Positions> string: missing char ';'.";
    return -1;
  }
  
  while (semicol_rank != -1)
  {
    Serial.print("data: "); Serial.println(data.substring(start, semicol_rank));
   
    const String & POS_ZMM = data.substring(start, semicol_rank);
    // we've got a bloc like "POS:1%ZMM:10"
    Serial.print("POS_ZMM: "); Serial.println(POS_ZMM);
   
    int percent_rank = POS_ZMM.indexOf("%", 0);       
    if (percent_rank == -1)
    {
      ack = "ERROR: malformed <Positions> string: missing char '%'.";
      return -1;
    }
    
    const String & pos_label = POS_ZMM.substring(0, percent_rank);
    const String & zmm_label = POS_ZMM.substring(percent_rank+1);
    Serial.print("pos_label: "); Serial.println(pos_label);
    Serial.print("zmm_label: "); Serial.println(zmm_label);
    nb_pos++;

    // Process pos_label:
    int colon_rank = pos_label.indexOf(":", 0);
    const String & pos_val = pos_label.substring(colon_rank+1);
    int num_pos = pos_val.toInt();

    // Process zmm_label:
    colon_rank = zmm_label.indexOf(":", 0);
    const String & zmm_val = zmm_label.substring(colon_rank+1);
    int zmm = zmm_val.toInt();

    String info = "[INFO]  Pos#" + String(num_pos) + ", " + String(zmm) + " mm\n";
    Serial.print(info);
    if ( num_pos < MAX_NB_ZPOS )
    {
      Zpos_mm[num_pos] = zmm;
    }
    else
    {
      ack = "# of positions is greater than MAX_NB_ZPOS";
      return -2;
    }
    start = semicol_rank+1;
    semicol_rank = data.indexOf(";", start);
  }

  nb_sensor_pos = nb_pos;
  ack = "[INFO] decodeZPositions returns OK";
  return 0;
}