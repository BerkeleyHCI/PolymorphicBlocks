## Revision 1

Revision 1 of this board had an error, where the ESP32-C3's IO8 was pulled down instead of up.
This prevents the device from going into download mode.

Suggested fix: remove the pull-down resistor, then bridge the IO8-side resistor pad to the adjacent EN resistor pad, which is pulled up.

This has since been fixed in the ESP32-C3 definition, though that fix is currently untested.
