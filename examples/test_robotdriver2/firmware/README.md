Building
- Install Arduino IDE 2
- Add the ESP32 boards to Arduino IDE:
  - File > Preferences > Additional Board Manager URLs = `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
    `
  - Tools > Boards > Boards Manager
  - Search for `ESP32` and install `esp32` by Espressif Systems
  - Wait for the install to finish, this can take a while
  - Tools > Boards > esp32 > ESP32 Dev Module
- Install libraries
  - Tools > Manage Libraries, and install:
    - `PS3 Controller Host` by Jeffrey van Pernis
    - `Freenove WS2812 Lib for ESP32` by Freenove
    - `PCF8574 library` by Renzo Mischianti
- Power on the board with SW1 pressed (to enter the bootloader)
- Select upload serial port: Tools > Port > ...
- Upload
