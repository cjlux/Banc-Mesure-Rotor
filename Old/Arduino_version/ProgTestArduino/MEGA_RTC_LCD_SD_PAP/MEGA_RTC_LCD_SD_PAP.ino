
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <RTClib.h>
#include <SPI.h>
#include <SD.h>

// The RTC clock:
RTC_DS1307 RTC;

// The LCD display : 2 lines of 16 characters, I2C adresse : 0x20
LiquidCrystal_I2C lcd(0x20,16,2);  

// Définition de la variable LCD_mess de type LCD_message
struct LCD_message
{
  String line0;
  String line1;
} LCD_mess;


// set up variables using the SD utility library functions:
Sd2Card card;
SdVolume volume;
SdFile root;
File dataFile;

// micro SD card AddaFruiton Arduino MEGA2560:
// CLK -> 52
// DO  -> 50
// DI  -> 51
// CS  -> 53
#define chipSelect 53

#define STOP while(1) {;}

///////////////////////////////////////////////
// pins for the stepper motor driver A4988   //
///////////////////////////////////////////////
const int pinDIR = 2;  // pin for direction of rotation
const int pinPUL = 3;  // pin for stepping
const int pinENA = 4;  // pin for Enable/disable torque

char file_name[13];
char buff[20]; // "yymmd  hh:mm:ss" -> 16 characters
char a_buff[6], X_buff[8];
String line;
String mess;
const String semicol(";");
unsigned long t0, t1;

///////////////////////////////////////////////////
/////// stepper motors parameters /////////////////
///////////////////////////////////////////////////
#define step_mode 1                                                 // used for 1/2, 1/4, 1/8.... step mode

#define STEPPER_ANGLE 1.8
// NBSTEP defines the numbers steps of the stepper motor for one rotor rotation:
#define NBSTEP 4              // 4 -> step angle of the ROTOR = 4*1.6/6 = 1.2°
                                // 8 -> step angle of the ROTOR = 8*1.6/6 = 2.4°

#define RATIO 6.

const int nbStepPerRevol  = int(360./STEPPER_ANGLE);                // number of steps for a full revolution


// macros usefull to write on digital pins:
#define CLR(x,y) (x &= (~(1 << y)))
#define SET(x,y) (x |= (1 << y))


const float step_angle = STEPPER_ANGLE*NBSTEP/RATIO;
# define NB_REVOL_PER_SEC 0.5
const float time_delay_ms = 1e3/(NB_REVOL_PER_SEC*nbStepPerRevol);

void LCD_display(const String & mess, int line, bool serialprint=true);

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
  LCD_display("Welcome to the ", 0);
  LCD_display("ROTOR test bench", 1);
  delay(3000);

  LCD_display("Init SD card...", 0);
  LCD_display("", 1);
  delay(2000);
     
  if (!SD.begin(chipSelect)) 
  {
    LCD_display("ERROR: SD card", 0);
    LCD_display("", 1);
    delay(2000);

    LCD_display("Insert a SD card", 0);
    LCD_display("and press RESET", 1);
    delay(2000);
    STOP
  }
  else
  {
    LCD_display("Init SD card OK", 0);
    LCD_display("", 1);
    delay(2000);
  }

  // we'll use the initialization code from the utility libraries
  // since we're just testing if the card is working!
  if (!card.init(SPI_HALF_SPEED, chipSelect)) 
  {
    LCD_display("ERROR: SD card", 0);
    LCD_display("       not found", 1);
    delay(2000);

    LCD_display("Insert a SD card", 0);
    LCD_display("and press RESET", 1);
    delay(2000);
    STOP
  } 
}


void loop() 
{
  // Enable motor current:
  digitalWrite(pinENA, LOW);
  
  DateTime now;
  float angle = 0;

  // Open the file for the data:note that only one file can be open at a time,
  // The fine name is "MMDDhhmm.txt" aka "Month Day hour minute.txt" (format FAT 8.3):
  now = RTC.now(); 
  sprintf(file_name, "%02u%02u%02u%02u.txt", now.month(),now.day(), now.hour(), now.minute());
  
  LCD_display("Uniq file name:", 0);
  LCD_display(file_name, 1);
  delay(2000);

  dataFile = SD.open(file_name, FILE_WRITE);
  dataFile.write("#YYMMDD hh:mm:ss;Angle[°];X_magn[mT];Y_magn[mT]\n");

  // scan angle from 0 to 360°:
  int count = 0;
  while(angle < 360)
  {
    t0 = millis();
    //
    // First line on the LCD display:
    //
    now = RTC.now(); 
    sprintf(buff, "%02u%02u%02u %02u:%02u:%02u", now.year()-2000, now.month(), now.day(), now.hour(), now.minute(), now.second());
    LCD_display(buff, 0);

    //
    // Second line on the LCD display:
    //
    float mag_field_X = random(1, 2000);
    mag_field_X /= 1.1;

    // write the float number in a char buffer on 7 digits with 2 digits after the decimal point:
    dtostrf(mag_field_X, 7, 2, X_buff);

    // Make the stepper motor do the steps:
    for(int i=0; i < NBSTEP; i++) 
    {
      digitalWrite(pinPUL, HIGH);
      delayMicroseconds(40);
      digitalWrite(pinPUL, LOW);
      delay(4*time_delay_ms);
    }

    angle = step_angle*count;
    // write the float number in a char buffer on 5 digits with 1 digits after the decimal point:
    dtostrf(angle, 5, 1, a_buff);

    mess = String(a_buff) + (char)223 + " " + X_buff + "mT";
    LCD_display(mess, 1);

    line = buff + semicol + String(a_buff) + semicol + X_buff + semicol + X_buff;
    dataFile.println(line);

    t1 = millis();
    while (t1 - t0 < 1000UL)
    {
      t1 = millis();
    }

    count += 1;
  }

  // release motor torque:
  digitalWrite(pinENA, HIGH);
  
  dataFile.close();

  LCD_display("END of measure", 1);
  STOP
}

void LCD_display(const String & mess, int line, bool serialprint)
{
  //
  // Display a message on one of the 2 LCD lines (N°0 ou 1).
  // The line is padded if needed with spaces up to 16 charceters.
  // - mess: the message to display.
  // - line: the line numver, 0 or 1.
  // - serialprint: boolean (default: true) to display or not 'mess' on the Serial monitor.
  //

  int L = mess.length();
  const String blanks_16 = "                ";
  String mess_16;
  if (L <16)
    mess_16 = mess + blanks_16.substring(L);
  else 
    mess_16 = mess.substring(0,16);
  
  if (line == 1)
  {
    LCD_mess.line1 = mess_16;
    lcd.setCursor(0,1);
    lcd.print(LCD_mess.line1);
  }
  else if (line == 0)
  {
    LCD_mess.line0 = mess_16;
    lcd.setCursor(0,0);
    lcd.print(LCD_mess.line0);
  }
  if (serialprint) Serial.println(mess_16);
}
