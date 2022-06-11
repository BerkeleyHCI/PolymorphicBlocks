#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClient.h>
#include <WiFiAP.h>

const uint8_t kNumLedDrivers = 7;
const uint8_t kNumCols = 5;  // X size, each element goes through a resistor so only one may be lit
const uint8_t kNumRows = 6;  // Y size
const int LedDrivers[kNumLedDrivers] = {4, 5, 6, 7, 1, 3, 10};  // GPIO pin numbers
const int sw1 = 0;  // GPIO0

const uint8_t smile[kNumCols * kNumRows] = {
  0, 1, 0, 1, 0,
  0, 0, 0, 0, 0,
  0, 0, 1, 0, 0,
  0, 0, 0, 0, 0,
  1, 0, 0, 0, 1,
  0, 1, 1, 1, 0,
};
const uint8_t frown[kNumCols * kNumRows] = {
  0, 1, 0, 1, 0,
  0, 0, 0, 0, 0,
  0, 0, 1, 0, 0,
  0, 0, 0, 0, 0,
  0, 1, 1, 1, 0,
  1, 0, 0, 0, 1,
};

volatile const uint8_t* pattern = smile;

// Interrupt example adapted from https://techtutorialsx.com/2017/10/07/esp32-arduino-timer-interrupts/
hw_timer_t * timer = NULL;
void IRAM_ATTR onTimer() {
  // The charlieplexing display is updated in an interrupt to keep the display refreshing
  // while the core is doing other things, like serving HTTP.
  // Each iteration here drives the next cathode from the current shared pattern variable.
  static uint8_t col = 0;
  for (size_t driver=0; driver<kNumLedDrivers; driver++) {  // blank before driving the next column
    pinMode(LedDrivers[driver], INPUT);
  }
  digitalWrite(LedDrivers[col], 0);  // drive the cathode low
  pinMode(LedDrivers[col], OUTPUT);

  for (size_t driver=0; driver<kNumLedDrivers; driver++) {
    if (driver != col) {
      bool driveMode = false;
      if (driver >= col) {
        driveMode = pattern[(driver - 1) * kNumCols + col];
      } else {
        driveMode = pattern[driver * kNumCols + col];
      }
      
      if (driveMode) {
        digitalWrite(LedDrivers[driver], 1);
        pinMode(LedDrivers[driver], OUTPUT);
      } else {
        pinMode(LedDrivers[driver], INPUT);
      }
    }
  }
  col = (col + 1) % kNumCols;
}


// Wifi code adapted from https://dronebotworkshop.com/esp32-intro/
const char *ssid = "LedMatrixAP";
const char *password = "password";
 
WiFiServer server(80);

void setup() {
  Serial.begin(115200);
  Serial.println("Charlieplexed LED Matrix " __DATE__ " " __TIME__);
  WiFi.softAP(ssid, password);
  Serial.println(WiFi.softAPIP());
  server.begin();
	
  timer = timerBegin(0, 80, true);  // prescaler of 80 on 80MHz clock gives 1 tick per us
  timerAttachInterrupt(timer, &onTimer, true);
  timerAlarmWrite(timer, 2000, true);  // interrupt per 2000us = 2ms
  timerAlarmEnable(timer);
}

void loop() {
  WiFiClient client = server.available();   // listen for incoming clients
  if (client) {
    Serial.println("New client");
    String currentLine = "";                // make a String to hold incoming data from the client
    while (client.connected()) {            // loop while the client's connected
      if (client.available()) {             // if there's bytes to read from the client,
        char c = client.read();             // read a byte, then
        if (c == '\n') {                    // if the byte is a newline character
          // if the current line is blank, you got two newline characters in a row.
          // that's the end of the client HTTP request, so send a response:
          if (currentLine.length() == 0) {
            // HTTP headers always start with a response code (e.g. HTTP/1.1 200 OK)
            // and a content-type so the client knows what's coming, then a blank line:
            client.println("HTTP/1.1 200 OK");
            client.println("Content-type:text/html");
            client.println();

            // the content of the HTTP response follows the header:
            client.print("<a href=\"/1\">Pattern 1</a><br>");
            client.print("<a href=\"/2\">Pattern 2</a><br>");

            // The HTTP response ends with another blank line:
            client.println();
            // break out of the while loop:
            break;
          } else {    // if you got a newline, then clear currentLine:
            currentLine = "";
          }
        } else if (c != '\r') {  // if you got anything else but a carriage return character,
          currentLine += c;      // add it to the end of the currentLine
        }

        if (currentLine.endsWith("GET /1")) {
          pattern = smile;
        }
        if (currentLine.endsWith("GET /2")) {
          pattern = frown;
        }
      }
    }
    // close the connection:
    client.stop();
  }
}
