#include <Servo.h>

// Servo objects
Servo x_servo;
Servo y_servo;

// Servo pins
int x_servo_pin = 6;
int y_servo_pin = 5;

int angle = 0;

void setup() {
  x_servo.attach(x_servo_pin);
  y_servo.attach(y_servo_pin);

  Serial.begin(9600);
  Serial.setTimeout(10000);  // Allow 10 seconds for new incoming data before resetting position
}

void loop() {
  if (Serial.available() > 0) {
    char designation = Serial.read();  // Which servo should be controlled?

    if (designation == 'x') {
      angle = Serial.parseInt();
      if (angle >= 0 && angle <= 180) {
        x_servo.write(angle);
      }
    } else if (designation == 'y') {
      angle = Serial.parseInt();
      if (angle >= 0 && angle <= 180) {
        y_servo.write(angle);
      }
    }
  }
}