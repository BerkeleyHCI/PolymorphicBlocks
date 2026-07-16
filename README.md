# Polymorphic Blocks

![](https://github.com/BerkeleyHCI/PolymorphicBlocks/actions/workflows/pr-python.yml/badge.svg?branch=master)
![](https://github.com/BerkeleyHCI/PolymorphicBlocks/actions/workflows/pr-scala.yml/badge.svg?branch=master)
![](https://img.shields.io/github/license/BerkeleyHCI/PolymorphicBlocks.svg)
![Python](https://img.shields.io/badge/python-3.9-blue.svg)

_subcircuit generator library based hardware description language for circuit board design_

Polymorphic Blocks is an open-source, Python-based [hardware description language (HDL)](https://en.wikipedia.org/wiki/Hardware_description_language) for schematic-equivalent design of printed circuit boards (PCBs).
Its library of components provide a high-level abstraction for circuit design while subcircuit generators automate the calculation of fine details.
Abstract component interfaces enable these libraries to be general across applications and component vendors.

Many boards have been built with this system, from mechanical keyboard macropads, to battery-powered IoT devices, to a USB source-measure unit. 
Check out the [examples page](examples.md)!


### Example by Keyboard

A simplified version of the [getting started tutorial](getting-started.md) is this snippet for a 3x4 mechanical keyboard:

```python
class Keyboard(SimpleBoardTop):
    def contents(self) -> None:
        super().contents()

        self.usb = self.Block(UsbCReceptacle())
        self.reg = self.Block(LinearRegulator(3.3 * Volt(tol=0.05)))
        self.connect(self.usb.gnd, self.reg.gnd)
        self.connect(self.usb.pwr, self.reg.pwr_in)

        with self.implicit_connect(
            ImplicitConnect(self.reg.pwr_out, [Power]),
            ImplicitConnect(self.reg.gnd, [Common]),
        ) as imp:
            self.mcu = imp.Block(IoController())
            self.connect(self.usb.usb, self.mcu.usb.request())

            self.sw = self.Block(SwitchMatrix(ncols=3, nrows=4))
            self.connect(self.sw.cols, self.mcu.gpio.request_vector("sw_col"))
            self.connect(self.sw.rows, self.mcu.gpio.request_vector("sw_row"))

            self.enc = imp.Block(DigitalRotaryEncoder())
            self.connect(self.enc.a, self.mcu.gpio.request("enc_a"))
            self.connect(self.enc.b, self.mcu.gpio.request("enc_b"))
            self.connect(self.enc.with_mixin(DigitalRotaryEncoderSwitch()).sw, self.mcu.gpio.request("enc_sw"))

    def refinements(self) -> Refinements:
        return super().refinements() + Refinements(
            class_refinements=[
                (IoController, Ch32v203),
                (Switch, KailhSocket),
            ])
```

The system:
- provides a library of subcircuit generators, like switch matrices and USB-C ports, that automatically include supporting components like decoupling capacitors and pullup resistors
- automatically selects generic parts like resistors and diodes against builtin parts tables
- performs basic electrical checks on the design, including voltage and current limits, automating some common datasheet parameter checking

This generates:
- a netlist that can be imported into the KiCad PCB editor
  - ... including hierarchical data, allowing subcircuit replication / channelization
  - ... and have stable tstamps, allowing incremental updates to in-progress board layouts
- a JLCPCB-compatible BoM
  - including a [postprocessing script](edg/tools/jlc_pcba/__main__.py) to shift part rotations from KiCad-generated component placements for JLC PCBA

Advanced capabilities include:
- multi-board support including connector-pair management
- cross-hierarchy packing of multi-pack devices like dual op-amps and quad resistors
- standard abstract component interfaces, allowing for custom implementations of parts like resistors (including from a parts table), and microcontrollers
- full support for user component definition; very little is hard-coded into the infrastructure


## Getting Started
See the [setup documentation](setup.md), then work through building a mechanical keyboard (including subcircuit layout replication) in the [getting started tutorial](getting-started.md).

**Setup tl;dr**: install the Python package from pip: `pip install edg`, and optionally run the [IDE plugin with block diagram visualizer](setup.md#ide-setup).

Also check out the [reference documentation](reference.md) for a concise list of capabilities.


## Additional Notes 

### Project Status
**This is functional has been used to [produce a wide variety of boards](examples.md) over the years.**
While the core is reasonably stable, as a pre-v1.0-release there are no formal guarantees of API stability.
In practice, deprecation shims are / will be maintained for common features if APIs change.

### Scope
The current libraries best support intermediate-level and simple PCB designs.
This includes circuits with discrete microcontrollers, microcontroller modules (like ESP32s), and socketed dev boards.
Libraries include common subcircuits like switch matrices, digitally attached peripherals like I2C sensors, voltage converters, and some analog signal conditioning circuit.
Check out the [component library folder](edg/parts/).
ESPHome boards are a great fit.

There is no prescribed architecture and microcontrollers are not required.

Designs that do not decompose into subcircuits blocks are a poor fit.

There is no support for high-speed digital design (like DDR memories).
There are some experimental RF subcircuits.

### Developing
We take pull requests and would love to see contributions and collaborations!

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### How this works

While degrees of library-based design are possible in graphical schematic tools, either informally with copy-paste or with hierarchical sheets, the main limitation is that these subcircuits are static and tuned for one particular application.
Baked-in choices like component values, footprint, and part number selection may not meet requirements for a different application that might, for example, call for through-hole components instead of surface-mount, or has different voltage rails.

The HDL provides two mechanisms to enable general subcircuit libraries: _generators_ and _abstract parts_.
Defining the subcircuit as code enables the library to contain logic to _generate_ the implementation to support many applications.
For instance, instead of a keyboard switch matrix with a fixed number of rows and columns, the library can take in user-specified `nrows` and `ncols` parameters and generate the matrix for that configuration.
A more complex example would be a buck converter generator, which automatically sizes its inductor and capacitors based on the current draw of connected components.

While generators enable the subcircuit to adapt to its environment, _abstract parts_ formalize and automate the concept of generic parts within subcircuits.
Instead of requiring baked in part numbers and footprints in subcircuits, library builders can instead place an abstract part like generic resistors, generic diodes, and even generic microcontrollers.
These only define the parts' interface but have no implementation; instead other library blocks can implement (subtype) the interface.
For example, the abstract interface can be implemented by a SMT resistor generator, a through-hole resistor generator, or a resistor that picks from a vendor part table.
_Refinements_ allow the system designer to choose how parts are replaced with subtypes.

An _electronics model_ performs basic checks on the design, including voltage limits, current limits, and signal level compatibility.
Advanced features like cross-hierarchy packing allows the use of multipack devices, like dual-pack op-amps and quad-pack resistors to optimize for space and cost.

### Papers
This started as an academic project, though with the goal of broader adoption.
Check out our papers (all open-access), which have more details:
- [System overview, UIST'20](http://dx.doi.org/10.1145/3379337.3415860) (some details may be out of date)
- [Mixed block-diagram / textual code IDE, UIST'21](https://dl.acm.org/doi/10.1145/3472749.3474804)
- [Array ports and multi-packed devices, SCF'22](https://doi.org/10.1145/3559400.3561997)

### Misc
- **_What is EDG?_**:
  [Embedded Device Generation](https://dl.acm.org/doi/10.1145/3083157.3083159) (or more generally Electronic Device Generation) was a prior version of this project that focused on algorithms and models for embedded device synthesis, though it lacked a user-facing component.
  This project is a continuation of that work focusing on an end-to-end system, and for most of its development cycle has been called `edg`.
  But, for the purposes of writing research papers, naming collisions are confusing and bad, and we chose to keep the repo and paper name consistent.
