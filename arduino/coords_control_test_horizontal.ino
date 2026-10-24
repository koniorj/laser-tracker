#include <Servo.h>
#include <math.h>
#define LASER 8

Servo horizontal;
Servo vertical; 

float posX = 90;
float posY = 90;
int laserStatus = 0;
float xT = 0;
float yT = 0;
float zT = 0;

void setup() {
  Serial.begin(9600);
  horizontal.attach(9);
  vertical.attach(10);
  pinMode(LASER, OUTPUT);

  horizontal.write(posX);
  vertical.write(posY);
}

void loop() {
  if(Serial.available() > 0){
    xT = Serial.parseFloat();
    yT = Serial.parseFloat();
    zT = Serial.parseFloat();
    
  while (Serial.available() > 0 && Serial.read() != '\n');

    float panRad = atan2(xT, yT); 
    
    // instead of xT^2 use multiplication (xT * xT)
    float distanceXY = sqrt((xT * xT) + (yT * yT));
    float tiltRad = atan2(zT, distanceXY);

    // conversion to coords and mapping
    // radians to degrees: deg * (180 / PI)
    posX = panRad * (180.0 / PI);
    posY = tiltRad * (180.0 / PI);

    posX += 90;
    posY += 90;

    posX = constrain(posX, 10, 170);
    posY = constrain(posY, 10, 170);

    horizontal.write(posX);
    vertical.write(posY);

    digitalWrite(LASER, HIGH); 
    
    // wait for the laser to point
    delay(5000); 

    // turning the laser off
    digitalWrite(LASER, LOW);
  }
}
