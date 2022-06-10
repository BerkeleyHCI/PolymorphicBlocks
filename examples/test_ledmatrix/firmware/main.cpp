#include <Arduino.h>

const auto led0 = 4;  // GPIO4
const auto led1 = 5;  // GPIO5
const auto led2 = 6;  // GPIO6
const auto led3 = 7;  // GPIO7
const auto led4 = 1;  // GPIO1
const auto led5 = 3;  // GPIO3
const auto led6 = 10;  // GPIO10
const auto sw1 = 0;  // GPIO0

void setup() {
  pinMode(led0, OUTPUT);
  digitalWrite(led0, 0);
  pinMode(led1, OUTPUT);
  digitalWrite(led1, 1);
  pinMode(led2, OUTPUT);
  digitalWrite(led2, 1);
}
  
void loop() {
  uint8_t lastMode = 0;
  while (1) {
    pinMode(led3, OUTPUT);
    digitalWrite(led3, lastMode);    
    lastMode = !lastMode;
    delay(100);
  }
}
