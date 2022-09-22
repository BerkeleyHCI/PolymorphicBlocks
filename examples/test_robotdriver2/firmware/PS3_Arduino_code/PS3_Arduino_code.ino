#include <Ps3Controller.h>
#include <Freenove_WS2812_Lib_for_ESP32.h>
#include <PCF8574.h>

#define IDLE -1
#define LEFT  1
#define RIGHT	2
#define FORWARD 3
#define BACKWARD 4

// Freenove_ESP32_WS2812 strip = Freenove_ESP32_WS2812(LEDS_COUNT, LEDS_PIN, CHANNEL, TYPE_GRB);

PCF8574 pcf8574(0x38, 12, 13);
int expander_led0 = 4;
int expander_led1 = 5;
int expander_led2 = 6;
int expander_led3 = 7;

class NeoPixelArray{
  public:
    NeoPixelArray(int led_count, int mcu_pin) : LEDS_COUNT(led_count), LEDS_PIN(mcu_pin), CHANNEL(0) {
      strip = Freenove_ESP32_WS2812(LEDS_COUNT, LEDS_PIN, CHANNEL, TYPE_GRB);
      
    }

    void setup(){
      strip.begin();
      strip.setBrightness(10);

      // start up with all lights red	
      for (int i = 0; i < LEDS_COUNT; i++) {
        strip.setLedColorData(i, 255, 0, 0);
      }
      strip.show();
    }

    void set_state(int state){
      switch(state){

        case LEFT: 
          for (int j = 0; j < LEDS_COUNT; j++) {
            for (int i = 0; i < LEDS_COUNT; i++) {
              if(i == j)
                strip.setLedColorData(i, 255, 95, 31);
              else
                strip.setLedColorData(i, 0, 0, 0);
            }
            strip.show();
            delay(2);
          } 
          break;

        case RIGHT: 
          for (int j = LEDS_COUNT-1; j >= 0; j--) {
            for (int i = LEDS_COUNT-1; i >= 0; i--) {
              if(i == j)
                strip.setLedColorData(i, 255, 95, 31);
              else
                strip.setLedColorData(i, 0, 0, 0);
            }
            strip.show();
            delay(2);
          } 
          break;
        
        case 0: 
          for (int j = 0; j < 255; j += 2) {
            for (int i = 0; i < LEDS_COUNT; i++) {
              strip.setLedColorData(i, strip.Wheel((i * 256 / LEDS_COUNT + j) & 255));
            }
            strip.show();
            delay(2);
          } 
          break;

        default:
          for (int i = 0; i < LEDS_COUNT; i++) {
            strip.setLedColorData(i, 0, 0, 0);
          }
          strip.show();
      }
    }    

  protected:
    Freenove_ESP32_WS2812 strip;  
    const int LEDS_COUNT;
    const int LEDS_PIN;
    const int CHANNEL;

};

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
  const int kPwmBits = 8; // range of [0-255]

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

  ledArray.setup();

  Ps3.attach(notify);
  Ps3.attachOnConnect(onConnect);
  Ps3.begin("b0:fc:36:5b:cf:08"); // Nathan's PS3 Controller

  Serial.println("Ready.");

  // Set pinMode to OUTPUT
	pcf8574.pinMode(expander_led0, OUTPUT);
  pcf8574.pinMode(expander_led1, OUTPUT);
  pcf8574.pinMode(expander_led2, OUTPUT);
  pcf8574.pinMode(expander_led3, OUTPUT);


	Serial.print("Init pcf8574...");
	if (pcf8574.begin()){
		Serial.println("OK");
	}else{
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

    if(turn < 0){
      ledArray.set_state(LEFT);
    }
    else if (turn > 0){
      ledArray.set_state(RIGHT);
    }
    else{
      ledArray.set_state(IDLE);
    }
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
  }

  else{
    ledArray.set_state(0);
  }
  delay(50);
}
