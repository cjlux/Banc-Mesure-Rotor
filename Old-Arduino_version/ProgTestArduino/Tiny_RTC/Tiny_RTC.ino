//
// Copyright jean-luc.charles@mailo.com
//
// 
#include <Wire.h>
#include "RTClib.h"
RTC_DS1307 RTC;

char time_buff[20]; // "yyyy/mm/dd hh:mm:ss" -> 19 characters

void setup () 
{
  // Start the serial link:
  Serial.begin(9600);

  // Start the I2C bus:
  Wire.begin();
  
  // Start the TRC module:
  RTC.begin();
  
  if (! RTC.isrunning()) 
  {
    Serial.println("RTC is NOT running!");
    // following line sets the RTC to the date & time this sketch was compiled
    RTC.adjust(DateTime(__DATE__, __TIME__));
  }
}

void loop () 
{
    DateTime now = RTC.now(); 
    sprintf(time_buff, "%2u/%02u/%02u %02u:%02u:%02u", now.year()-2000, now.month(), now.day(), now.hour(), now.minute(), now.second());
    Serial.println(time_buff); 
    delay(1000);
}