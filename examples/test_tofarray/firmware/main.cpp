#include <mbed.h>

I2C i2c(B11, B10);  // sda, scl

DigitalOut led0(B2);
DigitalOut led1(B12);
DigitalOut led2(A8);
DigitalOut led3(A9);
DigitalOut led4(A10);
DigitalOut led5(B13);
DigitalOut led6(B14);
DigitalOut led7(B15);

DigitalOut shut0(B6);
DigitalOut shut1(B5);
DigitalOut shut2(C15);
DigitalOut shut3(C14);
DigitalOut shut4(C13);

DigitalIn sw1(B1, PinMode::PullUp);

// CAN RXD=B8, TXD=B9

int main() {
  Timer timer;
  timer.start();
  while(1) {
      if (timer.read_ms() > 250) {
          timer.reset();
          led0 = !led0;
          led1 = !led0;
      }

  }
}
