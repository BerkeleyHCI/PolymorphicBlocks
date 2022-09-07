#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClient.h>
#include <WiFiAP.h>


// Wifi code adapted from https://dronebotworkshop.com/esp32-intro/
const char *ssid = "RobotDriverAP";
const char *password = "password";
 
WiFiServer server(80);

void setup() {
  Serial.begin(115200);
  Serial.println("Robot Driver " __DATE__ " " __TIME__);
  WiFi.softAP(ssid, password);
  Serial.println(WiFi.softAPIP());
  server.begin();
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
          // TODO relevant code
        }
      }
    }
    // close the connection:
    client.stop();
  }
}
