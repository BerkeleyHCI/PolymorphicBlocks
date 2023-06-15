Programming
- Programming the FPGA: use [Diamond Programmer](https://www.latticesemi.com/programmer)
  - If using a FT232H-based programmer, set the Cable to HW-USBN-2B
  - For SPI flash programming: the CS jumper must be soldered closed
  - It will not auto-detect connected devices, so set the entry manually:
    - Device Family: iCE40 UltraPlus
    - Device: iCE40UP5K
  - Set the SPI flash
    - _Diamond Programmer does not have the W25Q128JV series, so we're going to configure it for a different but compatible 128M flash_  
    - Right click the device entry > Device Properties
    - SPI Flash Family: SPI Serial Flash
    - Vendor: Micron
    - Device: SPI-M25P128
    - Package: doesn't matter
  - Select a bitstream and program
- Programming the RP2040
  - SWD: TODO
  - USB: connect to the USB, drag-and-drop a .uf2 file to the flash drive
    - If the flash drive does not show up: this may be because of non-empty flash.
      The stock dev board has a BOOTSEL button to force USB bootloader by shorting the flash CS low.
      Shorting CS low here (eg, by a IC clip attached to the flash chip's pin) does the same thing here.
      The flash can then be erased by flashing [flash_nuke.uf2](https://www.raspberrypi.com/documentation/microcontrollers/raspberry-pi-pico.html#resetting-flash-memory). 
    
Errata for v1
- RP2040 does not run code from flash - perhaps it needs all 4 QSPI IO pins?
  - [Thread on flash config in second stage bootloader](https://forums.raspberrypi.com/viewtopic.php?t=317631), [similar issue](https://forums.raspberrypi.com/viewtopic.php?t=333055)
  - [Thread on using QSPI pins as GPIO and alternate second-stage bootloaders](https://forums.raspberrypi.com/viewtopic.php?t=338586)
- RP2040 does not debug with CMSIS-DAP
  - Potentially related to multidrop support in the debug probe?

Potential improvements for v2
- Converter in connectors: rotated 90 degrees, balanced lengths to V+ and V-
- Bootstrap diodes: rotated 90 so they're not protruding into the converter power path pour
- Maybe move decoupling caps closer to FPGA and MCU
- Decoupling cap 1uF on USB Vbus line, as transient suppression
