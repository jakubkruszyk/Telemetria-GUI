int packVol[28] = {0}; // voltages of battery packages in [mV]
size_t packVolSize = sizeof(packVol)/sizeof(packVol[0]);
double battVol; // battery voltage in [V]
int temp[12] = {0}; // temperatures in battery
size_t tempSize = sizeof(temp)/sizeof(temp[0]);
int soc; // state of charge in [%]
  
void setup() {
  Serial.begin(115200, SERIAL_8N1); // UART comfiguration, 8 data bits, no parity, one stop bit 
  for(int i = 0; i < packVolSize; i++){
    packVol[i] = 3500;
  }
  battVol = 0;
  for(int i = 0; i < tempSize; i++){
    temp[i] = 40;
  }
  soc = 50;
}

void loop() {
  Serial.print("V;");
  for(int i = 0; i < packVolSize; i++){
    packVol[i] += random(-5, 6);
    if(packVol[i]< 3400){
      packVol[i]= 3400;
    }else if(packVol[i] > 3600){
      packVol[i] = 3600;
    }
    Serial.print(packVol[i]);
    Serial.print(';');
    battVol += (packVol[i] / 1000.0);
  }
  Serial.print("\r\n");
  delay(1000);

  Serial.print("B;");
  Serial.print(battVol);
  Serial.print(';');
  Serial.print("\r\n");
  battVol = 0;
  delay(1000);
  
  Serial.print("T;");
  for(int i = 0; i < tempSize; i++){
    temp[i] += random(-1, 2);
    if(temp[i]< 30){
      temp[i]= 30;
    }else if(temp[i] > 50){
      temp[i] = 50;
    }
    Serial.print(temp[i]);
    Serial.print(';');
  }
  Serial.print("\r\n");
  delay(1000);

  Serial.print("S;");
  soc += random(-1, 2);
  Serial.print(soc);
  Serial.print(';');
  Serial.print("\r\n");
  delay(1000);
}
