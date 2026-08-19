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
    
    // Zamiast xT^2 (co w C++ jest operacją bitową XOR), używamy mnożenia (xT * xT)
    float distanceXY = sqrt((xT * xT) + (yT * yT));
    float tiltRad = atan2(zT, distanceXY);

    // 3. KONWERSJA NA STOPNIE I MAPOWANIE
    // Zamiana radianów na stopnie: kąt * (180 / PI)
    posX = panRad * (180.0 / PI);
    posY = tiltRad * (180.0 / PI);

    // Przesunięcie układu współrzędnych. Wynik z atan2 może być ujemny (np. -45 do 45).
    // Dodajemy 90, aby środek ruchu wypadał na 90 stopniach serwa.
    posX += 90;
    posY += 90;

    // 4. ZABEZPIECZENIE I RUCH
    posX = constrain(posX, 10, 170);
    posY = constrain(posY, 10, 170);

    horizontal.write(posX);
    vertical.write(posY);

    digitalWrite(LASER, HIGH); 
    
    // Czekamy chwilę, aby laser poświecił w cel (np. pół sekundy)
    delay(5000); 

    // Wyłączamy laser, aby nie świecił bez przerwy i oszczędzał baterie
    digitalWrite(LASER, LOW);
  }
}
