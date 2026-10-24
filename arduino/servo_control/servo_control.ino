#include <Servo.h>
#include <math.h>
#define LASER 8

Servo horizontal;
Servo vertical;

float posX = 90;
float posY = 90;

void setup() {
  Serial.begin(9600);
  horizontal.attach(9);
  vertical.attach(10);
  pinMode(LASER, OUTPUT);

  // initial position
  horizontal.write(posX);
  vertical.write(posY);

  // turn the laser on continuously to draw the shape
  digitalWrite(LASER, HIGH);
}

void loop() {
    // check if there is some data in the buffer
    if (Serial.available() > 0) {
        // we will be sending frames to Arduino, which will look like: H10V10 (H[coords]V[coords])
        String coord_input = Serial.readStringUntil('\n');
        coord_input.trim();

        int H_index = coord_input.indexOf("H");
        int V_index = coord_input.indexOf("V");

        // if index found, then proceed
        if (H_index != -1 && V_index != -1) {
            String H_coords = coord_input.substring(H_index+1, V_index);
            String V_coords = coord_input.substring(V_index+1);

            int H_constrained_coords = constrain(H_coords.toInt(), 0, 180);
            int V_constrained_coords = constrain(V_coords.toInt(), 0, 180);

            horizontal.write(H_constrained_coords);
            vertical.write(V_constrained_coords);
        }
    }
}