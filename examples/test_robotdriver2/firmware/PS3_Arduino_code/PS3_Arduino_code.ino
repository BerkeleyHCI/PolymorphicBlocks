#include <Ps3Controller.h>


class LedcMotor {
public:
  LedcMotor(int out1, int out2, int ledc) : out1_(out1), out2_(out2), ledc_(ledc) {
  }

  void setup() {
    pinMode(out1_, OUTPUT);
    pinMode(out2_, OUTPUT);
    digitalWrite(out1_, 0);
    digitalWrite(out2_, 0);
    ledcSetup(ledc_, kPwmFreq, kPwmBits);
    ledcAttachPin(out1_, ledc_);  
  }

  void setPwm(int pwm) {
    if (pwm >= 0 && !fwdAttached_) {  // zero case just produces zero PWM
      ledcDetachPin(out2_);
      ledcAttachPin(out1_, ledc_);
      fwdAttached_ = true;
    } else if (pwm < 0 && fwdAttached_) {
      ledcDetachPin(out1_);
      ledcAttachPin(out2_, ledc_);
      fwdAttached_ = false;
    }

    ledcWrite(ledc_, abs(pwm));
  }

protected:
  const int out1_, out2_, ledc_;  // pin assignments for 1 and 2, and LEDC channel

  const int kPwmFreq = 24000;  // fast enough to not brown out the motor drivers but out of audible range
  const int kPwmBits = 8; // range of [0-255]

  bool fwdAttached_ = true;  // is the forward direction was the last attached PWM configuration
};

// Motor Pins
const int motor1A1 = 18;
const int motor1A2 = 19;
const int motor1B1 = 22;
const int motor1B2 = 21;
const int motor2A1 = 4;
const int motor2A2 = 16;
const int motor2B1 = 5;
const int motor2B2 = 17;

LedcMotor motor1A(18, 19, 0);
LedcMotor motor1B(22, 21, 1);
LedcMotor motor2A(4, 16, 2);
LedcMotor motor2B(5, 17, 3);


// PWM Properties


int player = 0;
int battery = 0;

int forward = 0;
int turn = 0;
int left_PWM = 0;
int right_PWM = 0;

// PWM acceleration
const int acceleration = 5;
int prev_left_PWM;
int prev_right_PWM;


const int kPwmLimit = 191;

int limitPwm (int pwm) {
  if (abs(pwm) > kPwmLimit) {
    return kPwmLimit * (pwm / abs(pwm));
  } else if (abs(pwm) < 15) {
    return 0;
  } else {
    return pwm;
  }
}

void applyAccleration (int *PWM, int *prev_PWM) {

  if (abs(*PWM - *prev_PWM) > acceleration)
  {
    *PWM = *PWM + acceleration * (*PWM - *prev_PWM) / abs(*PWM - *prev_PWM);
  }

  *prev_PWM = *PWM;

}


void notify()
{
  //---------------------- Battery events ---------------------
  if ( battery != Ps3.data.status.battery ) {
    battery = Ps3.data.status.battery;
    Serial.print("The controller battery is ");
    if ( battery == ps3_status_battery_charging )      Serial.println("charging");
    else if ( battery == ps3_status_battery_full )     Serial.println("FULL");
    else if ( battery == ps3_status_battery_high )     Serial.println("HIGH");
    else if ( battery == ps3_status_battery_low)       Serial.println("LOW");
    else if ( battery == ps3_status_battery_dying )    Serial.println("DYING");
    else if ( battery == ps3_status_battery_shutdown ) Serial.println("SHUTDOWN");
    else Serial.println("UNDEFINED");
  }

}

void onConnect() {
  Serial.println("Connected.");
}

void setup()
{
  Serial.begin(115200);

  motor1A.setup();
  motor1B.setup();
  motor2A.setup();
  motor2B.setup();

  Ps3.attach(notify);
  Ps3.attachOnConnect(onConnect);
  Ps3.begin("b0:fc:36:5b:cf:08"); // Nathan's PS3 Controller

  Serial.println("Ready.");
}

void loop() {
  if (!Ps3.isConnected())
    return;

  forward = Ps3.data.analog.stick.ly;
  turn = Ps3.data.analog.stick.lx;

  left_PWM = forward * 3 / 2 + turn;
  right_PWM = forward * 3 / 2 - turn;

  applyAccleration(&left_PWM, &prev_left_PWM);
  applyAccleration(&right_PWM, &prev_right_PWM);

  Serial.printf("Motors: %i %i\n", left_PWM, right_PWM);
  motor1A.setPwm(limitPwm(left_PWM));
  motor1B.setPwm(limitPwm(right_PWM));

  delay(50);
}
