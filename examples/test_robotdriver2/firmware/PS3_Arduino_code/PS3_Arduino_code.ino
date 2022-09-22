#include <Ps3Controller.h>
#include <Freenove_WS2812_Lib_for_ESP32.h>
#include <PCF8574.h>

#define DISCONNECTED -1
#define IDLE 0
#define UP 1
#define DOWN 2
#define LEFT 3
#define RIGHT 4
#define FORWARD 5
#define BACKWARD 6

int loop_count = 0;

PCF8574 pcf8574(0x38, 12, 13);
int expander_led0 = 4;
int expander_led1 = 5;
int expander_led2 = 6;
int expander_led3 = 7;


class NeoPixelArray {
public:
  NeoPixelArray(int led_count, int mcu_pin)
    : LEDS_COUNT(led_count), LEDS_PIN(mcu_pin), CHANNEL(0), half_led_count(LEDS_COUNT / 2){
    strip = Freenove_ESP32_WS2812(LEDS_COUNT, LEDS_PIN, CHANNEL, TYPE_GRB);
  }

  void setup() {
    strip.begin();
    strip.setBrightness(25);

    // start up with all lights white
    for (int i = 0; i < LEDS_COUNT; i++) {
      strip.setLedColorData(i, 255, 255, 255);
    }
    strip.show();
  }

  void set_state(int state, int color_state) {
    int delay_val = 50;


    if (state == DISCONNECTED) {
      for (int i = 0; i < LEDS_COUNT; i++) {
        strip.setLedColorData(i, 255, 0, 0);
      }
      strip.show();
    } else {
      if (loop_count % 5 == 0) {
        switch (state) {

          case LEFT:
            for (int j = 0; j < LEDS_COUNT; j++) {
              for (int i = 0; i < LEDS_COUNT; i++) {
                if (i == j)
                  strip.setLedColorData(i, colors[color_state][0], colors[color_state][1], colors[color_state][2]);
                else
                  strip.setLedColorData(i, 0, 0, 0);
              }
              strip.show();
              delay(delay_val);
            }
            break;

          case RIGHT:
            for (int j = LEDS_COUNT - 1; j >= 0; j--) {
              for (int i = LEDS_COUNT - 1; i >= 0; i--) {
                if (i == j)
                  strip.setLedColorData(i, colors[color_state][0], colors[color_state][1], colors[color_state][2]);
                else
                  strip.setLedColorData(i, 0, 0, 0);
              }
              strip.show();
              delay(delay_val);
            }
            break;

          case BACKWARD:
            for (int j = 0; j <= half_led_count; j++) {
              for (int i = 0; i < LEDS_COUNT; i++) {
                if (i == j || i == LEDS_COUNT - 1 - j)
                  strip.setLedColorData(i, colors[color_state][0], colors[color_state][1], colors[color_state][2]);
                else
                  strip.setLedColorData(i, 0, 0, 0);
              }
              strip.show();
              delay(delay_val * 2);
            }
            break;

          case FORWARD:
            for (int j = half_led_count; j >= 0; j--) {
              for (int i = 0; i < LEDS_COUNT; i++) {
                if (i == j || i == LEDS_COUNT - 1 - j)
                  strip.setLedColorData(i, colors[color_state][0], colors[color_state][1], colors[color_state][2]);
                else
                  strip.setLedColorData(i, 0, 0, 0);
              }
              strip.show();
              delay(delay_val * 2);
            }
            break;

          default:
            for (int j = 0; j < 255; j += 2) {
              for (int i = 0; i < LEDS_COUNT; i++) {
                strip.setLedColorData(i, strip.Wheel((i * 256 / LEDS_COUNT + j) & 255));
              }
              strip.show();
              delay(5);
            }
            break;
        }
      }
    }
  }

protected:
  Freenove_ESP32_WS2812 strip;
  const int LEDS_COUNT;
  const int LEDS_PIN;
  const int CHANNEL;
  const int half_led_count;
  byte colors[3][3] = {
    { 255, 95, 31 },  // amber color
    { 0, 255, 0 },    // green color
    { 0, 0, 255 }     // blue color
  };
};

class LedcMotor {
public:
  LedcMotor(int out1, int out2, int ledc)
    : out1_(out1), out2_(out2), ledc_(ledc) {
  }

  void setup() {
    pinMode(out1_, OUTPUT);
    pinMode(out2_, OUTPUT);
    digitalWrite(out1_, 0);
    digitalWrite(out2_, 0);
    ledcSetup(ledc_, kPwmFreq, kPwmBits);
    ledcWrite(ledc_, 0);
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
  const int kPwmBits = 8;      // range of [0-255]

  bool fwdAttached_ = true;  // is the forward direction was the last attached PWM configuration
};

// Motor Pins
LedcMotor motor1A(18, 19, 0);
LedcMotor motor1B(22, 21, 1);
LedcMotor motor2A(4, 16, 2);
LedcMotor motor2B(5, 17, 3);


// PWM Properties
int player = 0;
int battery = 0;

// PWM acceleration
const int acceleration = 5;
int prev_left_PWM;
int prev_right_PWM;
int prev_left_up_PWM;
int prev_right_up_PWM;

const int kPwmLimit = 191;

NeoPixelArray ledArray(5, 15);

int limitPwm(int pwm) {
  if (abs(pwm) > kPwmLimit) {
    return kPwmLimit * (pwm / abs(pwm));
  } else if (abs(pwm) < 15) {
    return 0;
  } else {
    return pwm;
  }
}

void applyAccleration(int *PWM, int *prev_PWM) {
  if (abs(*PWM - *prev_PWM) > acceleration) {
    *PWM = *PWM + acceleration * (*PWM - *prev_PWM) / abs(*PWM - *prev_PWM);
  }

  *prev_PWM = *PWM;
}


void notify() {
  //---------------------- Battery events ---------------------
  if (battery != Ps3.data.status.battery) {
    battery = Ps3.data.status.battery;
    Serial.print("The controller battery is ");
    if (battery == ps3_status_battery_charging) Serial.println("charging");
    else if (battery == ps3_status_battery_full) Serial.println("FULL");
    else if (battery == ps3_status_battery_high) Serial.println("HIGH");
    else if (battery == ps3_status_battery_low) Serial.println("LOW");
    else if (battery == ps3_status_battery_dying) Serial.println("DYING");
    else if (battery == ps3_status_battery_shutdown) Serial.println("SHUTDOWN");
    else Serial.println("UNDEFINED");
  }
}

void onConnect() {
  Serial.println("Connected.");
}

void setup() {
  Serial.begin(115200);

  motor1A.setup();
  motor1B.setup();
  motor2A.setup();
  motor2B.setup();

  ledArray.setup();

  Ps3.attach(notify);
  Ps3.attachOnConnect(onConnect);
  Ps3.begin("b0:fc:36:5b:cf:08");  // Nathan's PS3 Controller

  Serial.println("Ready.");

  // Set pinMode to OUTPUT
  pcf8574.pinMode(expander_led0, OUTPUT);
  pcf8574.pinMode(expander_led1, OUTPUT);
  pcf8574.pinMode(expander_led2, OUTPUT);
  pcf8574.pinMode(expander_led3, OUTPUT);


  Serial.print("Init pcf8574...");
  if (pcf8574.begin()) {
    Serial.println("OK");
  } else {
    Serial.println("KO");
  }

  pcf8574.digitalWrite(expander_led0, HIGH);
  pcf8574.digitalWrite(expander_led1, HIGH);
  pcf8574.digitalWrite(expander_led2, HIGH);
  pcf8574.digitalWrite(expander_led3, HIGH);
}


void loop() {
  if (Ps3.isConnected()) {
    int forward = Ps3.data.analog.stick.ly;
    int turn = Ps3.data.analog.stick.lx;

    int left_PWM = forward * 3 / 2 + turn;
    int right_PWM = forward * 3 / 2 - turn;

    applyAccleration(&left_PWM, &prev_left_PWM);
    applyAccleration(&right_PWM, &prev_right_PWM);

    motor1A.setPwm(limitPwm(left_PWM));
    motor1B.setPwm(limitPwm(right_PWM));

    int up = Ps3.data.analog.stick.ry;
    int roll = Ps3.data.analog.stick.rx;

    int left_up_PWM = up * 3 / 2 + roll;
    int right_up_PWM = up * 3 / 2 - roll;

    applyAccleration(&left_up_PWM, &prev_left_up_PWM);
    applyAccleration(&right_up_PWM, &prev_right_up_PWM);

    motor2A.setPwm(limitPwm(left_up_PWM));
    motor2B.setPwm(limitPwm(right_up_PWM));

    Serial.printf("Motors: % 3i % 3i    % 3i % 3i\n", left_PWM, right_PWM, left_up_PWM, right_up_PWM);

    int joystick_threshold = 10;
    int color_state = 0;

    if (up < (-1 * joystick_threshold))
      color_state = DOWN;
    else if (up > joystick_threshold)
      color_state = UP;
    else
      color_state = IDLE;

    if (turn < (-1 * joystick_threshold) && turn < (-1 * abs(forward))) {
      ledArray.set_state(LEFT, color_state);
    } else if (turn > joystick_threshold && turn > abs(forward)) {
      ledArray.set_state(RIGHT, color_state);
    } else if (forward > joystick_threshold && forward > abs(turn)) {
      ledArray.set_state(FORWARD, color_state);
    } else if (forward < (-1 * joystick_threshold) && forward < (-1 * abs(turn))) {
      ledArray.set_state(BACKWARD, color_state);
    } else {
      ledArray.set_state(IDLE, color_state);
    }

  } else {
    ledArray.set_state(DISCONNECTED, DISCONNECTED);
  }

  loop_count++;
  if (loop_count > 1000000)
    loop_count = 0;
  delay(50);
}