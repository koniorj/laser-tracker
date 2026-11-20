#include <Servo.h>
#include <math.h>
#define LASER 8

Servo horizontal;
Servo vertical;

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(10);
  horizontal.attach(9);
  vertical.attach(10);
  horizontal.write(126);
  vertical.write(124);
  delay(1000);
  pinMode(LASER, OUTPUT);
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
        if (H_index != -1 && V_index != -1 && H_index < V_index) {
            String H_coords = coord_input.substring(H_index+1, V_index);
            String V_coords = coord_input.substring(V_index+1);

            int H_constrained_coords = constrain(H_coords.toInt(), 90, 180);
            int V_constrained_coords = constrain(V_coords.toInt(), 90, 180);

            horizontal.write(H_constrained_coords);
            vertical.write(V_constrained_coords);
        }
    }
}