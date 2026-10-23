#include <Servo.h>
#include <math.h>
#define LASER 8

Servo horizontal;
Servo vertical;

float posX = 90;
float posY = 90;
float theta = 0.0; // Angle for the circular path

void setup() {
  Serial.begin(9600);
  horizontal.attach(9);
  vertical.attach(10);
  pinMode(LASER, OUTPUT);

  horizontal.write(posX);
  vertical.write(posY);

  // Turn the laser on continuously to draw the shape
  digitalWrite(LASER, HIGH);
}

void loop() {
  // 1. CALCULATE TARGET COORDINATES
  // Center is (0, 3, 0), radius is 2 on the XZ plane (y is constant at 3)
  float xT = 2.0 * cos(theta);
  float yT = 3.0;
  float zT = 2.0 * sin(theta);

  // 2. INVERSE KINEMATICS
  float panRad = atan2(xT, yT);
  float distanceXY = sqrt((xT * xT) + (yT * yT));
  float tiltRad = atan2(zT, distanceXY);

  // 3. CONVERT TO DEGREES AND MAP
  posX = (panRad * (180.0 / PI)) + 90.0;
  posY = (tiltRad * (180.0 / PI)) + 90.0;

  // 4. CONSTRAIN AND MOVE
  posX = constrain(posX, 10, 170);
  posY = constrain(posY, 10, 170);

  horizontal.write(posX);
  vertical.write(posY);

  // 5. INCREMENT ANGLE FOR NEXT FRAME
  // Change 0.05 to adjust the speed (larger = faster, smaller = smoother/slower)
  theta += 0.03;
  if (theta >= 2.0 * PI) {
    theta -= 2.0 * PI; // Keep theta from overflowing indefinitely
  }

  // Brief delay to give servos time to reach the incremental position
  delay(20);
}
