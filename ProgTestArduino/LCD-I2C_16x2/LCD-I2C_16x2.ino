#include <Wire.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x20,16,2);  // objet lcd: 2 lignes x 16 caractères à l'adresse I2C 0x20

void setup() 
{
  lcd.init();                      // initialize the lcd 
  lcd.backlight();
  
  lcd.setCursor(0, 0);
  lcd.print("    Hello MERI    ");
  lcd.setCursor(0, 1);
  lcd.print("nice to meet you...");
  }

void loop() 
{
  // put your main code here, to run repeatedly:

}
