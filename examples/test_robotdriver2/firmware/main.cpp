#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClient.h>
#include <WiFiAP.h>


const int motor1A1 = 18;
const int motor1A2 = 19;
const int motor1B1 = 22;
const int motor1B2 = 21;
const int motor2A1 = 4;
const int motor2A2 = 16;
const int motor2B1 = 5;
const int motor2B2 = 17;

const int ledArrayData = 36;

const int lcdReset = 25;
const int lcdDc = 33;
const int lcdCs = 26;
const int lcdSpiSck = 32;
const int lcdSpiMosi = 35;

bool state = false;  // false=off, true=on


// Wifi code adapted from https://dronebotworkshop.com/esp32-intro/
const char *ssid = "RobotDriverAP";
const char *password = "password";
 
WiFiServer server(80);

void setup() {
  Serial.begin(115200);
  Serial.println("Robot Driver " __DATE__ " " __TIME__);
  WiFi.softAP(ssid);
  Serial.println(WiFi.softAPIP());
  server.begin();

  pinMode(motor1A1, OUTPUT);
  pinMode(motor1A2, OUTPUT);
  pinMode(motor1B1, OUTPUT);
  pinMode(motor1B2, OUTPUT);
  pinMode(motor2A1, OUTPUT);
  pinMode(motor2A2, OUTPUT);
  pinMode(motor2B1, OUTPUT);
  pinMode(motor2B2, OUTPUT);

  analogWrite(motor1A1, 0.1);
  digitalWrite(motor1A2, 0);
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
            // TODO relevant code
            if (state) {
              client.print("ON<br/>");
            } else {
              client.print("OFF<br/>");
            }
            client.print("<a href=\"/tog\">Toggle</a><br>");

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

        if (currentLine.endsWith("GET /tog")) {
          if (!state) {
            analogWrite(motor1A1, 0);
            digitalWrite(motor1A2, 0);
          } else {
            analogWrite(motor1A1, 0.1);
            digitalWrite(motor1A2, 0);
          }
          state = !state;
        }
      }
    }
    // close the connection:
    client.stop();
  }
}
