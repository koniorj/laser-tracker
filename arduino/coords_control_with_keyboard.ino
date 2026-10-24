#include <Servo.h>
#include <math.h>
#define LASER 8

Servo horizontal;
Servo vertical; 

int posX = 90;
int posY = 90;
int laserStatus = 0;
int val;

void setup() {
  Serial.begin(9600);
  horizontal.attach(9);
  vertical.attach(10);
  pinMode(LASER, OUTPUT);
}

void loop() {
  if(Serial.available() > 0){
    val = Serial.read();
    
    if(val == 'd')
      posX += 5;
    if(val == 'a')
      posX -= 5;
    if(val == 'w')
      posY -= 5;
    if(val == 's')
      posY += 5; 
    if(val == 'l')
      if(laserStatus == 0){
        digitalWrite(LASER, HIGH);
        laserStatus = 1;
      }
      else{
        digitalWrite(LASER, LOW);
        laserStatus = 0;
      }
  
    posX = constrain(posX, 0, 180);
    posY = constrain(posY, 0, 180);

    horizontal.write(posX);
    vertical.write(posY);
  }
}