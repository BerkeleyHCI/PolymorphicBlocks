#include <mbed.h>
#include "WS2812.h"


I2C i2c(B7, B6);  // sda, scl

AnalogIn curr3(A6);
AnalogIn curr2(A4);
AnalogIn curr1(A5);
AnalogIn convSense(A6);

PwmOut buckPwm(A1);
PwmOut boostPwm(A2);

DigitalIn bldcFault(B12);

DigitalIn sw1(A15, PinMode::PullUp);


const size_t kPixelBufferSize = 1;
WS2812 ws(B4, kPixelBufferSize, 1, 6, 6, 1);

DigitalOut swoPin(B3);
// SoftSerial serial(B3, NC);  // can't do SWO serial on STM32 =(, SoftSerial also seems broken


int main() {
  // pixel format:                      RRGGBB
  int pixelBuf[kPixelBufferSize] = {0x00101010};

  buckPwm.period_us(20);
  boostPwm.period_us(20);

  while (1) {
    ws.write(pixelBuf);
    wait(0.1);

    if (!sw1.read()) {
      buckPwm = 1.0;
      boostPwm = 0.25;
      pixelBuf[0] = 0x00201000;
    } else {
      buckPwm = 0;
      boostPwm = 0;
      pixelBuf[0] = 0x00100010;
    }
  }
}
