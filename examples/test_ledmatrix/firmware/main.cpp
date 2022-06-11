#include <Arduino.h>

const uint8_t kNumLedDrivers = 7;
const uint8_t kNumCols = 5;  // X size, each element goes through a resistor so only one may be lit
const uint8_t kNumRows = 6;  // Y size
const int LedDrivers[kNumLedDrivers] = {4, 5, 6, 7, 1, 3, 10};  // GPIO pin numbers
const int sw1 = 0;  // GPIO0

void charlieplex(const uint8_t arr[kNumCols * kNumRows]) {
  for (size_t col=0; col<kNumCols; col++) {
    digitalWrite(LedDrivers[col], 0);  // drive the cathode low
    pinMode(LedDrivers[col], OUTPUT);

    for (size_t driver=0; driver<kNumLedDrivers; driver++) {
      if (driver != col) {
        bool driveMode = false;
        if (driver >= col) {
          driveMode = arr[(driver - 1) * kNumCols + col];
        } else {
          driveMode = arr[driver * kNumCols + col];
        }
        
        if (driveMode) {
          digitalWrite(LedDrivers[driver], 1);
          pinMode(LedDrivers[driver], OUTPUT);
        } else {
          pinMode(LedDrivers[driver], INPUT);
        }
      }
    }
    delay(2);

    for (size_t driver=0; driver<kNumLedDrivers; driver++) {  // blank before driving the next column
      pinMode(LedDrivers[driver], INPUT);
    }
  }
}

void setup() {
}
  
void loop() {
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

  uint64_t lastMillis = millis();
  while (1) {
    if (millis() % 2000 < 1000) {
      charlieplex(smile);
    } else {
      charlieplex(frown);
    }
  }
}
