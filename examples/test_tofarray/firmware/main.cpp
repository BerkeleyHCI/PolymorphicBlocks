#include <mbed.h>
#include "SoftSerial.h"
#include "VL53L0X.h"

I2C i2c(B11, B10);  // sda, scl
VL53L0X vlSensor0(&i2c);
VL53L0X vlSensor1(&i2c);
VL53L0X vlSensor2(&i2c);
VL53L0X vlSensor3(&i2c);
VL53L0X vlSensor4(&i2c);

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

DigitalOut swoPin(B3);
// SoftSerial serial(B3, NC);  // can't do SWO serial on STM32 =(


int main() {
  shut0 = 0;
  shut1 = 0;
  shut2 = 0;
  shut3 = 0;
  shut4 = 0;

  Timer timer;
  timer.start();

  wait_ms(10);

  shut0 = 1;
  wait_ms(10);
  vlSensor0.init();
  vlSensor0.setDeviceAddress(0x42);
  vlSensor0.setModeContinuous();
  vlSensor0.startContinuous();
  
  shut1 = 1;
  wait_ms(10);
  vlSensor1.init();
  vlSensor1.setDeviceAddress(0x44);
  vlSensor1.setModeContinuous();
  vlSensor1.startContinuous();

  shut2 = 1;
  wait_ms(10);
  vlSensor2.init();
  vlSensor2.setDeviceAddress(0x46);
  vlSensor2.setModeContinuous();
  vlSensor2.startContinuous();
  
  shut3 = 1;
  wait_ms(10);
  vlSensor3.init();
  vlSensor3.setDeviceAddress(0x48);
  vlSensor3.setModeContinuous();
  vlSensor3.startContinuous();
  
  shut4 = 1;
  wait_ms(10);
  vlSensor4.init();
  vlSensor4.setDeviceAddress(0x4a);
  vlSensor4.setModeContinuous();
  vlSensor4.startContinuous();
  

  while(1) {
      if (timer.read_ms() > 50) {
          timer.reset();
          uint16_t range0 = vlSensor0.getRangeMillimeters();
          led0.write(range0 > 200 && range0 < 4000);
          uint16_t range1 = vlSensor1.getRangeMillimeters();
          led1.write(range1 > 200 && range1 < 4000);
          uint16_t range2 = vlSensor2.getRangeMillimeters();
          led2.write(range2 > 200 && range2 < 4000);
          uint16_t range3 = vlSensor3.getRangeMillimeters();
          led3.write(range3 > 200 && range3 < 4000);
          uint16_t range4 = vlSensor4.getRangeMillimeters();
          led4.write(range4 > 200 && range4 < 4000);

          led5 = !led5;
          led6 = !led5;
          led7 = !led6;
      }
  }
}
