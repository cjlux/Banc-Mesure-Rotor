void setup() 
{
  Serial.begin(115200);
  while(!Serial) {;}
  Serial.println("Serial0 avalaible !");

  Serial1.begin(9600);
  while(!Serial1) {;}
  Serial.println("Serial1 avalaible !");

  delay(1000);

  Serial.println("Reading Serial1...");
  while(Serial1.available()>0)
  { 
    Serial.println((char)Serial1.read());
  }

  delay(1000);

  Serial.println("Writing Serial1...");
  Serial1.print("PC\n");
  
  delay(100);

  Serial.println("Reading Serial1...");
  while(Serial1.available()>0)
  { 
    Serial.println((char)Serial1.read());
  }

  delay(1000);

  Serial.println("STOP");
  while(true) {;}
}
 
void loop() 
{

  
}

