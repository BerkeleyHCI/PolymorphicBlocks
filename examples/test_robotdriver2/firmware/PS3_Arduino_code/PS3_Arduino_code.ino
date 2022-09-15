#include <Ps3Controller.h>

// Motor Pins
const int motor1A1 = 18;
const int motor1A2 = 19;
const int motor1B1 = 22;
const int motor1B2 = 21;
const int motor2A1 = 4;
const int motor2A2 = 16;
const int motor2B1 = 5;
const int motor2B2 = 17;

// PWM Properties
const int freq = 30000;
const int resolution = 8; // range of [0-255]

int player = 0;
int battery = 0;

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

  pinMode(motor1A1, OUTPUT);
  pinMode(motor1A2, OUTPUT);
  pinMode(motor1B1, OUTPUT);
  pinMode(motor1B2, OUTPUT);
  pinMode(motor2A1, OUTPUT);
  pinMode(motor2A2, OUTPUT);
  pinMode(motor2B1, OUTPUT);
  pinMode(motor2B2, OUTPUT);

  // Assign LED pins to a PWM channel
  ledcAttachPin(motor1A1, 0);
  ledcAttachPin(motor1A2, 1);
  ledcAttachPin(motor1B1, 2);

  // configure LED PWM functionalitites
  ledcSetup(0, freq, resolution);

  Ps3.attach(notify);
  Ps3.attachOnConnect(onConnect);
  Ps3.begin("b0:fc:36:5b:cf:08"); // Nathan's PS3 Controller

  Serial.println("Ready.");
}

void loop()
{
  if (!Ps3.isConnected())
    return;

    if (Ps3.data.analog.stick.ly < 0)   // Pulling the stick up makes ly -> negative
    {
      digitalWrite(motor1A2, 0);
      ledcWrite(0, abs(Ps3.data.analog.stick.ly / 2));
      Serial.println("FORWARD");
    }

    else if (Ps3.data.analog.stick.ly > 0)
    {
      digitalWrite(motor1A1, 0);
      ledcWrite(1, abs(Ps3.data.analog.stick.ly / 2));
      Serial.println("BACKWARD");
    }
    else
    {
      digitalWrite(motor1A1, 0);
      digitalWrite(motor1A2, 0);
      Serial.println("BRAKE");
    }


  delay(500);
}
