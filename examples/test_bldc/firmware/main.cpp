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

// SoftSerial serial(B3, NC);  // can't do SWO serial on STM32, also broken since start bit is too long

Timer timer;

int main() {
  // pixel format:                      RRGGBB
  int pixelBuf[kPixelBufferSize] = {0x00101010};

  buckPwm.period_us(50);
  boostPwm.period_us(50);

  float lastPwm = 0;
  timer.start();

  while (1) {
    while (timer.read_ms() < (100 * 1.5));  // clock is fast by 1.5x
    timer.reset();

    ws.write(pixelBuf);

    if (!sw1.read()) {
      lastPwm = lastPwm + 0.02;

      // Sweep the entire buck output range
      if (lastPwm > 1.0) {
        lastPwm = 0;
      }
      buckPwm = lastPwm;
      boostPwm = 0;

      // Sweep part of the boost output range, up to 1.5x
      // if (lastPwm > 0.25) {
      //   lastPwm = 0;
      // }
      // buckPwm = 1.0;
      // boostPwm = lastPwm;

      pixelBuf[0] = 0x00201000;
    } else {
      lastPwm = 0;
      buckPwm = 0;
      boostPwm = 0;
      pixelBuf[0] = 0x00100010;
    }
  }
}
