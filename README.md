# Polymorphic Blocks

Polymorphic Blocks is an open-source, Python-based [hardware description language (HDL)](https://en.wikipedia.org/wiki/Hardware_description_language) for [printed circuit boards (PCBs)](https://en.wikipedia.org/wiki/Printed_circuit_board).
Unlike some existing PCB HDLs, our goal is not just "schematics in text" (or "Verilog for PCBs" 😨), but to increase design automation and accessibility by improving on the fundamental design model.
Expressing designs and libraries in code not only allows basic automation like step-and-repeat with `for` loops, but also allows subcircuits to be reactive to their usage like automatically sizing power converters by output voltage and current draw.
Adding programming language concepts, like type systems, interfaces, and inheritance, can also raise the level of design, while polymorphism allows libraries to be generic while retaining fine-grained control for system designers.

Check out the [the getting started tutorial](getting-started.md) document for a more usage-focused introduction.
Consider using the [IntelliJ plugin](https://github.com/BerkeleyHCI/edg-ide) that provides HDL compilation integration, side-by-side block diagram visualization, and graphical schematic-like HDL generation actions. 
A [reference document](reference.md) is also available, listing selected ports, links, and parts.

For a slightly deeper technical overview, including summaries of example projects, check out our [UIST'20 paper and recorded talks](http://dx.doi.org/10.1145/3379337.3415860).

**While this can produce real boards with much more automation than in mainstream schematic flows, this is still a work-in-progress.**
**APIs may change, though we will try to maintain backwards compatibility (eg, through deprecation phases) where possible.**
See [Project Status](#project-status) for more details.


## Example
From [the getting started tutorial](getting-started.md), this code defines a board with a USB Type-C connector powering (through a buck converter for 3.3V step-down) a microcontroller which drives a LED and reads a switch.

```python
self.usb = self.Block(UsbDeviceCReceptacle())

with self.implicit_connect(
    ImplicitConnect(self.usb.pwr, [Power]),
    ImplicitConnect(self.usb.gnd, [Common]),
) as imp:
  self.usb_reg = imp.Block(BuckConverter(output_voltage=3.3*Volt(tol=0.05)))

with self.implicit_connect(
    ImplicitConnect(self.usb_reg.pwr_out, [Power]),
    ImplicitConnect(self.usb.gnd, [Common]),
) as imp:
  self.mcu = imp.Block(Lpc1549_48())
  (self.swd, ), _ = self.chain(imp.Block(SwdCortexTargetHeader()), self.mcu.swd)
     
  (self.led, ), _ = self.chain(self.mcu.new_io(DigitalBidir), imp.Block(IndicatorLed()))
  (self.sw, ), _ = self.chain(imp.Block(DigitalSwitch()), self.mcu.new_io(DigitalBidir))
```

To get to a PCB, the user would then:
- Drop the HDL into a top-level block and compile it.
- Select block refinements as needed, eg choosing a TPS561201 regulator for the abstract BuckConverter.
- Generate the netlist.
- Import into [KiCad](https://kicad-pcb.org/) for board layout.
- As circuit changes are needed, re-generate the netlist and update the board layout. 


## Selected Features
Circuit Design Features
- An electronics model that performs circuit checks above ERC, like checking voltage compatibility and current limits.
- Automatic parts selection for discrete components, using E-series for resistors and parts tables for capacitors, inductors, and discrete semiconductors.
  - ... including E-series resistive dividers.
- Common subcircuit blocks that implement well-known design practices:
  - ... including buck and boost converters that automatically run component sizing calculations.
  - ... including some analog circuits like resistive dividers, low-pass RCs, and certain opamp topologies.
- Common subcircuit blocks that implement the datasheet application circuits:
  - ... including microcontrollers, like STM32F103, ESP32 modules, and nRF52840 modules, and supporting manual (but checked) pin assignment.
  - ... including a USB Type C receptacle (USB 2.0 type), so you can't forget the CC pull-down resistors.

Layout Integration Features
- Stable netlists for KiCad 6.0, allowing in-progress board layouts to be updated from modified HDL.
  - Note: this depends on stable names in the HDL. We've got some thoughts for a more powerful version of this, though.
  - Hierarchical support, including for KiCad's builtin Select Hierarchical Sheet and the [Replicate Layout plugin](https://github.com/MitjaNemec/ReplicateLayout).


## Setup
See the [setup documentation](setup.md).

### Unit Tests
You can run the unit test suite to verify that everything works - all tests should be green.
The test suite includes both unit level tests and example boards.

```
python -m unittest discover
```

If a bunch of things are failing but it isn't clear why from excessive console spam, consider just running one test:

```python
python -m unittest examples.test_blinky.BlinkyTestCase.test_design_complete
```

### Getting Started Tutorial
Check out [the getting started tutorial](getting-started.md), once you have a working installation.


## Additional Resources 

### Project Status
**This is functional and produces boards, but is still a continuing work-in-progress.**
**APIs may change, though we will try to maintain backwards compatibility (eg, through deprecation phases) where possible.**

If you're looking for a mature PCB design tool that just works, this currently isn't it (yet).
For a mature and open-source graphical schematic capture and board layout tool, check out [KiCad](https://kicad-pcb.org/).
**However, if you are interested in trying something new, we're happy to help you and answer questions.**

**If you're interested in collaborating or contributing, please reach out to us**, and we do take pull requests.
Ultimately, we'd like to see an open-source PCB HDL that increases design automation, reduces tedious work, and makes electronics more accessible to everyone. 

Current development focuses on supporting intermediate-level PCB projects, ie those an advanced hobbyist would make.
Typical systems would involve power conditioning circuits, a microcontroller, and supporting peripherals (possibly including analog blocks).
Note that there is no hard-coded architecture, eg, a microcontroller is not needed, and you can make pure analog boards.
We believe that the system should be able to handle projects that are much more or much less complex, as long as supporting libraries exist.

We have no plans to address board layout - KiCad's board layout tool is very functional for manual layout.
However, there are cross-cutting concerns (eg, layout-aware pin assignment, HDL-to-layout diff and update, multipack devices) that we may address.

### Examples
Example boards, including layouts, are available in the [examples/](examples/) directory, structured as unit tests and including board layouts:
- [Blinky](examples/test_blinky.py): all variations of blinky from [the getting started tutorial](getting-started.md).
- [LED Matrix](examples/test_ledmatrix.py): a 6x5 LED matrix display made up of discrete [charlieplexed](https://en.wikipedia.org/wiki/Charlieplexing) LEDs with a ESP32-C3 WiFi + RISC-V microcontroller, and demonstrating a charlieplexing array generator and packed resistors.
- [Simon](examples/test_simon.py): a [Simon memory game](https://en.wikipedia.org/wiki/Simon_(game)) implementation with a speaker and [12v illuminated dome buttons](https://www.sparkfun.com/products/9181).
- [CANdapter](examples/test_can_adapter.py): an isolated [CANbus](https://en.wikipedia.org/wiki/CAN_bus) to USB (type-C, USB-FS) adapter.
- [SWD Debugger](examples/test_swd_debugger.py): an [SWD (Serial Wire Debug)](https://developer.arm.com/architectures/cpu-architecture/debug-visibility-and-trace/coresight-architecture/serial-wire-debug) programmer / debugger that is partially firmware-compatible with ST-Link/V2 clones.
- [BLE Multimeter](examples/test_multimeter.py): a BLE (Bluetooth Low Energy) compact (stick form factor) multimeter, supporting volts / ohms / diode / continuity test mode, for low voltage applications.
- [USB Source-Measure Unit](examples/test_usb_source_measure.py): a USB PD (type-C power delivery) source-measure unit -- which can both act as a DC power supply with configurable voltage and current, and as a DC load. More precisely, it's a digitally-controlled 2-quadrant (positive voltage, positive or negative current) power source.  


### Developing
See [developing.md](developing.md) for developer documentation.

### Misc
- **_What is EDG?_**:
  [Embedded Device Generation](https://dl.acm.org/doi/10.1145/3083157.3083159) (or more generally Electronic Device Generation) was a prior version of this project that focused on algorithms and models for embedded device synthesis, though it lacked a user-facing component.
  This project is a continuation of that work focusing on an end-to-end system, and for most of its development cycle has been called `edg`.
  But, for the purposes of writing research papers, naming collisions are confusing and bad, and we chose to keep the repo and paper name consistent.
- **_Why is there so much CANbus stuff?_**:
  Many of the example designs were built for a [solar car project](https://calsol.berkeley.edu/).  
- **_Why is there so much USB Type-C stuff?_**:
  USB Type-C is the one connector to rule them all.
