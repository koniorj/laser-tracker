#include <Servo.h>
#include <math.h>
#define LASER 8

Servo horizontal;
Servo vertical; 

int posX = 126;
int posY = 124;
int laserStatus = 1;

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(10);
  horizontal.attach(9);
  vertical.attach(10);
  horizontal.write(posX);
  vertical.write(posY);
  pinMode(LASER, OUTPUT);
  digitalWrite(LASER, HIGH);
}

void loop() {
  if(Serial.available() > 0){
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command.length() > 0) {
      char val = command.charAt(0); 
      int move = command.substring(1).toInt();
    
    
      if(val == 'd')
        posX -= move;
      if(val == 'a')
        posX += move;
      if(val == 'w')
        posY -= move;
      if(val == 's')
        posY += move; 
      if(val == 'l')
        if(laserStatus == 0){
          digitalWrite(LASER, HIGH);
          laserStatus = 1;
        }
        else{
          digitalWrite(LASER, LOW);
          laserStatus = 0;
        }
    
      posX = constrain(posX, 90, 180);
      posY = constrain(posY, 90, 180);
      Serial.print(posX);
      Serial.print(", "); 
      Serial.println(posY);

      horizontal.write(posX);
      vertical.write(posY);
    }
  }
}