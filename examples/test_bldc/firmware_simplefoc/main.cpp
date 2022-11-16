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
BLDCMotor motor = BLDCMotor(14);
BLDCDriver3PWM driver = BLDCDriver3PWM(PA7, PB1, PB10, PB0, PB2, PB11);
LowsideCurrentSense cs = LowsideCurrentSense(0.050f, 20.5f, PA5, PA4, PA6);

SoftwareSerial mySerial(0, PB3);


int startMillis = 0;

void setup() {
  mySerial.begin(76800 * 0.66);
  // mySerial.begin(1000000 * 0.66);
  mySerial.println("\r\nstart");

  pinMode(resetDout, OUTPUT);
  digitalWrite(resetDout, 0);
  _delay(10);
  digitalWrite(resetDout, 1);
  _delay(10);

  // power supply voltage
  // default 12V
  driver.voltage_power_supply = 7;
  driver.pwm_frequency = 15000;
  driver.init();
  // link the motor to the driver
  motor.linkDriver(&driver);
  cs.linkDriver(&driver);

  // These were the first example setup, which use an encoder / position sensor
  // // set control loop to be used
  // motor.controller = MotionControlType::velocity;
  
  // // controller configuration based on the control type 
  // // velocity PI controller parameters
  // // default P=0.5 I = 10
  // motor.PID_velocity.P = 0.2;
  // motor.PID_velocity.I = 20;
  
  // //default voltage_power_supply
  // motor.voltage_limit = 6;

  // // velocity low pass filtering
  // // default 5ms - try different values to see what is the best. 
  // // the lower the less filtered
  // motor.LPF_velocity.Tf = 0.02;


  // These are the configs from the DRV8302 on STM32, which uses low-side current sensing
  // align voltage
  motor.voltage_sensor_align = 0.5;
  
  // control loop type and torque mode 
  motor.torque_controller = TorqueControlType::foc_current;
  motor.controller = MotionControlType::torque;
  motor.motion_downsample = 0.0;

  // velocity loop PID
  motor.PID_velocity.P = 0.2;
  motor.PID_velocity.I = 5.0;
  // Low pass filtering time constant 
  motor.LPF_velocity.Tf = 0.02;
  // angle loop PID
  motor.P_angle.P = 20.0;
  // Low pass filtering time constant 
  motor.LPF_angle.Tf = 0.0;
  // current q loop PID 
  motor.PID_current_q.P = 3.0;
  motor.PID_current_q.I = 100.0;
  // Low pass filtering time constant 
  motor.LPF_current_q.Tf = 0.02;
  // current d loop PID
  motor.PID_current_d.P = 3.0;
  motor.PID_current_d.I = 100.0;
  // Low pass filtering time constant 
  motor.LPF_current_d.Tf = 0.02;


  // angle P controller 
  // default P=20
  // motor.P_angle.P = 20;

  //  maximal velocity of the position control
  // default 20
  motor.velocity_limit = 100;
  motor.current_limit = 2.0;    // 2 Amp current limit
  
  // initialize motor
  mySerial.println("init motor");
  motor.init();
  cs.init();

  motor.linkCurrentSense(&cs);

  // align encoder and start FOC
  mySerial.println("init FOC");
  motor.initFOC();

  // monitoring port
  mySerial.println("done");
  motor.useMonitoring(mySerial);
  motor.monitor_variables = _MON_CURR_Q | _MON_CURR_D | _MON_VEL; // monitor the two currents d and q

  _delay(1000);

  startMillis = millis();
}

void loop() {
  // iterative FOC function
  motor.loopFOC();

  PhaseCurrent_s  current = cs.getPhaseCurrents();
  // mySerial.print((int)(current.a * 1000));
  // mySerial.print(" ");
  // mySerial.print((int)(current.b * 1000));
  // mySerial.print(" ");
  // mySerial.print((int)(current.c * 1000));
  // mySerial.println("");

  // motor.monitor();

  // function calculating the outer position loop and setting the target position 
  motor.move(0.25);
  // motor.move(min(millis() * 2 / 1000, 40UL));

}