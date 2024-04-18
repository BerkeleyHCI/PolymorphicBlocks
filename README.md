# Polymorphic Blocks

Polymorphic Blocks is an open-source, Python-based [hardware description language (HDL)](https://en.wikipedia.org/wiki/Hardware_description_language) for [printed circuit boards (PCBs)](https://en.wikipedia.org/wiki/Printed_circuit_board).
The goal is to **make use of programming concepts and capabilities to increase design automation and re-use**, instead of being just a representational change like 'schematics but in text'.

The overall focus is on supporting subcircuit libraries that are general enough to be used in many different applications, much like what makes software development so productive and approachable.
While graphical schematic tools have varying degrees of support for re-use, from copy-paste to hierarchical schematics, the subcircuits are static and typically specialized to one application.
Baked-in choices like component values, footprint, and part number selection may not meet requirements for a different application that might, for example, call for 1206 instead of 0402, or has different voltage rails.

Defining libraries as code enables that kind of logic, generating the subcircuit to fit the particular application. 
This also allows encoding datasheet and application note instructions as part of the library, ensuring that boards can be correct-by-construction where design gotchas can be automated. 
Further programming concepts like type hierarchies and interfaces enable abstract components like generic resistors to be used in generic subcircuit libraries, while allowing the system designer the option to specify the particular type of resistor.

We've been using this system to create a variety of boards of different complexities, [examples](#examples) range from a charlieplexed LED matrix to a USB source-measure unit.
Do note that work continues on this project and APIs and libraries may change, though the core has largely stabilized.

This project started as an academic project, though with the goal of broader adoption.
Check out our papers (all open-access):
- [System overview, UIST'20](http://dx.doi.org/10.1145/3379337.3415860)
- [Mixed block-diagram / textual code IDE, UIST'21](https://dl.acm.org/doi/10.1145/3472749.3474804)
- [Array ports and multi-packed devices, SCF'22](https://doi.org/10.1145/3559400.3561997)


## Demonstration by Example
<table>
<tr >
<td><b>User input</b></td>
<td><b>What this tool does</b></td>
</tr>

<tr style="vertical-align:top">
<td>

Define the board using high-level library blocks (subcircuits) and connections, optionally also specifying internal component choices as refinements (for example, using Kailh mechanical keyswitch sockets for generic switches):
```python
class Keyboard(SimpleBoardTop):
  def contents(self) -> None:
    super().contents()

    self.usb = self.Block(UsbCReceptacle())
    self.reg = self.Block(Ldl1117(3.3*Volt(tol=0.05)))
    self.connect(self.usb.gnd, self.reg.gnd)
    self.connect(self.usb.pwr, self.reg.pwr_in)

    with self.implicit_connect(
            ImplicitConnect(self.reg.pwr_out, [Power]),
            ImplicitConnect(self.reg.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(Stm32f103_48())

      self.sw = self.Block(SwitchMatrix(nrows=3, ncols=2))
      self.connect(self.sw.cols, self.mcu.gpio.request_vector())
      self.connect(self.sw.rows, self.mcu.gpio.request_vector())

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      class_refinements=[
        (Switch, KailhSocket),
      ],
    )
```

from [USB-C keyboard test case](examples/test_keyboard.py)

</td>
<td>

Produces a netlist that can be imported into KiCad for board layout and ultimately Gerber generation for manufacturing:
![](docs/keyboard.png)
_Placement and routing are out of scope of this project. Components above manually placed._

Featuring:
- Correct-by-construction subcircuits blocks
  - ... so there's no forgetting that the USB-C port requires CC pulldown resistors (or a connected PD controller)
- Automatic selection of generic parts like resistors, capacitors, and diodes against a parts table
  - ... including BoM generation for assembly
- Electrical correctness checks including voltage and current limits, and signal level compatibility.
- Stable netlists, allowing incremental updates to in-progress board layouts 

</td>
</tr>
</table>


## Getting Started
See the [setup documentation](setup.md), then work through the [getting started tutorial](getting-started.md).

**Setup tl;dr**: install the Python package from pip: `pip install edg`, and optionally run the [IDE plugin with block diagram visualizer](setup.md#ide-setup).


## Additional Notes 

### Examples
Example boards, including layouts, are available in the [examples/](examples/) directory, structured as unit tests and including board layouts:
- [Blinky](examples/test_blinky.py): all variations of blinky from [the getting started tutorial](getting-started.md).
- [LED Matrix](examples/test_ledmatrix.py): a 6x5 LED matrix display made up of discrete [charlieplexed](https://en.wikipedia.org/wiki/Charlieplexing) LEDs with a ESP32-C3 WiFi + RISC-V microcontroller, and demonstrating a charlieplexing array generator and packed resistors.
- [Simon](examples/test_simon.py): a [Simon memory game](https://en.wikipedia.org/wiki/Simon_(game)) implementation with a speaker and [12v illuminated dome buttons](https://www.sparkfun.com/products/9181).
- [SWD Debugger](examples/test_swd_debugger.py): an [SWD (Serial Wire Debug)](https://developer.arm.com/architectures/cpu-architecture/debug-visibility-and-trace/coresight-architecture/serial-wire-debug) programmer / debugger that is partially firmware-compatible with ST-Link/V2 clones.
- [BLE Multimeter](examples/test_multimeter.py): a BLE (Bluetooth Low Energy) compact (stick form factor) multimeter, supporting volts / ohms / diode / continuity test mode, for low voltage applications.
- [USB Source-Measure Unit](examples/test_usb_source_measure.py): a USB PD (type-C power delivery) source-measure unit -- which can both act as a DC power supply with configurable voltage and current, and as a DC load. More precisely, it's a digitally-controlled 2-quadrant (positive voltage, positive or negative current) power source.  

### Developing
**If you're interested in collaborating or contributing, please reach out to us**, and we do take pull requests.
Ultimately, we'd like to see an open-source PCB HDL that increases design automation, reduces tedious work, and makes electronics more accessible to everyone.

See [developing.md](developing.md) for developer documentation.

### Project Status
**This is functional and produces boards, but is still a continuing work-in-progress.**

If you're looking for a mature PCB design tool that just works, this currently isn't it (yet).
For a mature and open-source graphical schematic capture and board layout tool, check out [KiCad](https://kicad-pcb.org/).
**However, if you are interested in trying something new, we're happy to help you and answer questions.**

Current development focuses on supporting intermediate-level PCB projects, ie those an advanced hobbyist would make.
Typical systems would involve power conditioning circuits, a microcontroller, and supporting peripherals (possibly including analog blocks).
There is no hard-coded architecture (a microcontroller is not needed), and pure analog boards are possible.
The system should also be able to handle projects that are much more or much less complex, especially if supporting libraries exist.

### Misc
- **_What is EDG?_**:
  [Embedded Device Generation](https://dl.acm.org/doi/10.1145/3083157.3083159) (or more generally Electronic Device Generation) was a prior version of this project that focused on algorithms and models for embedded device synthesis, though it lacked a user-facing component.
  This project is a continuation of that work focusing on an end-to-end system, and for most of its development cycle has been called `edg`.
  But, for the purposes of writing research papers, naming collisions are confusing and bad, and we chose to keep the repo and paper name consistent.
