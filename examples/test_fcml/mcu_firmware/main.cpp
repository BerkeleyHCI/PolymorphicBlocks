/* PIO does not support RPi + mbed
#include <mbed.h>

DigitalOut led0(22);
DigitalOut led1(23);
DigitalOut led2(24);
DigitalOut led3(25);

DigitalIn sw1(18, PinMode::PullUp);

Serial serial(0, 1);  // txd, rxd
*/

#include <Arduino.h>

const int led0 = 22;
const int led1 = 23;
const int led2 = 24;
const int led3 = 25;

const int sw = 18;

void setup() {
  //Serial.begin(115200);
  //Serial.println("RPi FCML Test " __DATE__ " " __TIME__);
  
  pinMode(led0, OUTPUT);
  pinMode(led1, OUTPUT);
  pinMode(led2, OUTPUT);
  pinMode(led3, OUTPUT);
  pinMode(sw, INPUT_PULLUP);
  digitalWrite(led0, 0);
  digitalWrite(led1, 0);
  digitalWrite(led2, 1);
  digitalWrite(led3, 1);
}

void loop() {
  while (!digitalRead(sw)) {
  }  // freeze while switch is held down
  
  digitalWrite(led0, !digitalRead(led0));
  digitalWrite(led1, !digitalRead(led0));
  
  delay(100);
}

/*
int main() {
  led0 = 0;
  led1 = 0;
  led2 = 0;
  led3 = 0;

  while(1) {
      if (timer.read_ms() > 50) {
          timer.reset();
          
          led0 = !led0;
      }
      while (sw1) {
      }
  }
}
*/