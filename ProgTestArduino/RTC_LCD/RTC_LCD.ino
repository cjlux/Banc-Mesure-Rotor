#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include "RTClib.h"

// The RTC clock:
RTC_DS1307 RTC;

// The LCD display : 2 lines of 16 characters, I2C adresse : 0x20
LiquidCrystal_I2C lcd(0x20,16,2);  

char time_buff[27]; // "yymmd  hh:mm:ss" -> 16 characters
char angle_buff[6], X_buff[8];

void setup() 
{
  // Start the serial link:
  Serial.begin(9600);

  // Start the I2C bus:
  Wire.begin();

  // Start the LCD display:
  lcd.init();              
  lcd.backlight();

  // Start the TRC module:
  RTC.begin();

  // Sets the RTC to the date & time this sketch was compiled
  RTC.adjust(DateTime(__DATE__, __TIME__));
    
  lcd.setCursor(0, 0);
  lcd.print("Welcome to the ");
  lcd.setCursor(0, 1);
  lcd.print("ROTOR test bench");

  delay(3000);
  }

void loop() 
{
  // scan angle from 0 to 360°:
  for (float a=0; a <= 360; a += 2)
  {
    //
    // First line on the LCD display:
    //
    DateTime now = RTC.now(); 
    sprintf(time_buff, "%02u%02u%02u  %02u:%02u:%02u", now.year()-2000, now.month(), now.day(), now.hour(), now.minute(), now.second());
    lcd.setCursor(0, 0);
    lcd.print(time_buff);

    //
    // Second line on the LCD display:
    //
    float mag_field_X = random(1, 2000);
    mag_field_X /= 1.1;

    // write the float number in a char buffer on 7 digits with 2 digits after the decimal point:
    dtostrf(mag_field_X, 7, 2, X_buff);
     
    float angle = 1.8*a/3.;   // the ratio factor 1:3
    // write the float number in a char buffer on 5 digits with 1 digits after the decimal point:
    dtostrf(angle, 5, 1, angle_buff);

    String mess = String(angle_buff) + (char)223 + " " + X_buff + "mT";
    lcd.setCursor(0, 1);
    lcd.print(mess);

    delay(1000);
  }
}
