#include <mbed.h>

//RawSerial serial(D1, D0);

DigitalOut led(LED1);

DigitalOut rgb_r(D12);
DigitalOut rgb_g(D11);
DigitalOut rgb_b(D10);

DigitalOut led1(D2);
DigitalIn btn1(D3);
DigitalOut led2(D4);
DigitalIn btn2(D5);
DigitalOut led3(D6);
DigitalIn btn3(D7);
DigitalOut led4(D8);
DigitalIn btn4(D9);

AnalogOut spk(A3);

const float pi = 3.14159;

const uint32_t kReferenceDurationUs = 500 * 1000;
const uint32_t kReferenceDelayUs = 50 * 1000;
const uint32_t kPressDurationUs = 300 * 1000;

DigitalIn* btns[4] = {&btn1, &btn2, &btn3, &btn4};
DigitalOut* leds[4] = {&led1, &led2, &led3, &led4};
uint32_t tones[4] = {310, 415, 209, 252};

void tone(uint32_t freq, uint32_t durationUs) {
    Timer timer;
    float periodUs = 2 * pi / (1000.0 * 1000.0 / freq);
    timer.start();
    uint32_t holdTargetUs = 0;
    while (timer.read_us() < durationUs) {
        float target = sin(holdTargetUs * periodUs) / 4.0 + 0.5;
        holdTargetUs += 500;  // sample output at 2kHz
        while (timer.read_us() < holdTargetUs);
        spk = target;
    }
}

void playReference(uint8_t button) {
    if (button >= 4) {
        return;
    }
    
    *leds[button] = 1;
    tone(tones[button], kReferenceDurationUs);
    *leds[button] = 0;
}

uint8_t readButton() {
    while (true) {
        for (uint8_t i=0; i<4; i++) {
            if (!(*btns[i])) {
                *leds[i] = 1;
                tone(tones[i], kPressDurationUs);
                *leds[i] = 0;
                return i;
            }
        }
    }
}

int main() {
  rgb_r = 1;
  rgb_g = 0;
  rgb_b = 0;
    
  *leds[1] = 1;
  while (*btns[0] && *btns[1] && *btns[2] && *btns[3]);
  *leds[1] = 0;
    
  while(1) {
    uint8_t seq[4];
    seq[0] = rand() % 4;
    seq[1] = rand() % 4;
    seq[2] = rand() % 4;
    seq[3] = rand() % 4;
    
    wait_us(kReferenceDelayUs);
    playReference(seq[0]);
    wait_us(kReferenceDelayUs);
    playReference(seq[1]);
    wait_us(kReferenceDelayUs);
    playReference(seq[2]);
    wait_us(kReferenceDelayUs);
    playReference(seq[3]);
    
    uint8_t press[4];
    press[0] = readButton();
    press[1] = readButton();
    press[2] = readButton();
    press[3] = readButton();
    
    if (press[0] == seq[0] && press[1] == seq[1] && press[2] == seq[2] && press[3] == seq[3]) {
        *leds[1] = 1;
    } else {
        *leds[0] = 1;
    }
    while (*btns[0] && *btns[1] && *btns[2] && *btns[3]);
    *leds[0] = 0;
    *leds[1] = 0;
  }
}
