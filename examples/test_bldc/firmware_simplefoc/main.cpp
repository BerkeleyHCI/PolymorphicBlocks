#include <SoftwareSerial.h>
#include <SimpleFOC.h>

// #include <mbed.h>
// #include "WS2812.h"


// I2C i2c(B7, B6);  // sda, scl

// AnalogIn curr3(A6);
// AnalogIn curr2(A4);
// AnalogIn curr1(A5);
// AnalogIn convSense(A6);

// PwmOut buckPwm(A1);
// PwmOut boostPwm(A2);

// DigitalIn bldcFault(B12);

// DigitalIn sw1(A15, PinMode::PullUp);


// const size_t kPixelBufferSize = 1;
// WS2812 ws(B4, kPixelBufferSize, 1, 6, 6, 1);

// // SoftSerial serial(B3, NC);  // can't do SWO serial on STM32, also broken since start bit is too long

// Timer timer;




// init BLDC motor
int resetDout = PB13;
BLDCMotor motor = BLDCMotor(11);
BLDCDriver3PWM driver = BLDCDriver3PWM(PA7, PB1, PB10, PB0, PB2, PB11);

SoftwareSerial mySerial (0, PB3);


void setup() {
  pinMode(resetDout, OUTPUT);
  digitalWrite(resetDout, 0);
  _delay(10);
  digitalWrite(resetDout, 1);
  _delay(10);


  // power supply voltage
  // default 12V
  driver.voltage_power_supply = 8;
  driver.pwm_frequency = 15000;
  driver.init();
  // link the motor to the driver
  motor.linkDriver(&driver);

  // set control loop to be used
  motor.controller = MotionControlType::velocity_openloop;
  
  // controller configuration based on the control type 
  // velocity PI controller parameters
  // default P=0.5 I = 10
  motor.PID_velocity.P = 0.2;
  motor.PID_velocity.I = 20;
  
  //default voltage_power_supply
  motor.voltage_limit = 6;

  // velocity low pass filtering
  // default 5ms - try different values to see what is the best. 
  // the lower the less filtered
  motor.LPF_velocity.Tf = 0.02;

  // angle P controller 
  // default P=20
  // motor.P_angle.P = 20;

  //  maximal velocity of the position control
  // default 20
  motor.velocity_limit = 50;
  
  // initialize motor
  motor.init();
  // align encoder and start FOC
  motor.initFOC();

  // monitoring port
  Serial.begin(9600);
  Serial.println("Start");
  _delay(1000);
}

void loop() {
  // iterative FOC function
  motor.loopFOC();

  // function calculating the outer position loop and setting the target position 
  motor.move(25);

}