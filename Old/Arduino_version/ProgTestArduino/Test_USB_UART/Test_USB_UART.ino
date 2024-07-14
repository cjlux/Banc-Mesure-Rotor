void setup(){
  Serial.begin(115200);
  Serial1.begin(115200);
}

void loop(){
  if(Serial.available()){
    Serial1.print((char)Serial.read());
  }
  if(Serial1.available()){
    Serial.print((char)Serial1.read());
  }
}
