# Quick Reference
A simplified EDG EDSL guide, primarily as a reference for those who have been through the [getting started guide](getting-started.md).

_Some documentation may be out of date._

## Core Primitives

### Parameters
- `BoolExpr`: boolean (true / false) variable
  - Supports standard boolean operations
- `FloatExpr`: numeric variable
  - Suppers standard numeric operations
- `RangeExpr`: range (interval) variable
  - Supports standard numeric operations (multiplication and division are undefined), some set operations (`.within(other)`, `.contains(other)`, `.intersect(other)`), and get operations (`.lower()`, `.upper()`)
- `StringExpr`: string (text) variable
  - Supports equality operations only

### Blocks
Blocks represent a subcircuit (or hierarchical schematic sheet), and consist of boundary ports and internal subblocks and connections (links) between ports on those subblocks. 

Skeleton structure:
```python
class MyBlock(Block):
  def __init__(self) -> None:
    super().__init__()  # essential to call the superclass method beforehand to initialize state
    # declare ports here, and subblocks whose ports are exported

  def contents(self) -> None:
    super().contents()  # essential to call the superclass method beforehand to initialize state
    # declare subblocks and connections here
```

These are properties of Blocks:
- The Block type hierarchy defines allowed refinements
- `@abstract_block` decorates a block as abstract, which will error on netlisting

These can be called inside `__init__(...)`:
- `self.Parameter(ParameterType(optional_value))`: declare parameters, optionally with a value
- `self.Port(PortType(...))`: declare ports 
  - Optional arguments: `tags=[ImplicitTags], optional=False`
  - `self.Export(self.subblock.port)`: export a subblock's port
- `@init_in_parent` decorator is needed if `__init__(...)` takes Parameter arguments and must generate constraints in the parent Block  
  
These can be called inside `contents()`:
- `self.Block(BlockType(...))`: declare sub-blocks
  - Also allowed inside `__init__(...)`, to allow the use of `Export`s 
- `self.constrain(...)`: constrain some `BoolExpr` (which can be an inline expression, eg `self.param1 == self.param2`) to be true
- `self.connect(self.subblock1.port, self.subblock2.port, ...)`: connect own ports and/or subblock's ports
  - Naming is optional.
- `with self.implicit_connect(...) as imp:`: open an implicit connection scope
  - Implicit connection arguments of the form `ImplicitConnect(connect_to_port, [MatchingTags])`
  - `imp.Block(BlockType(...))`: similar to `self.Block(...)` but implicitly connects ports with matching tags
- `self.chain(self.Block(BlockType(...)), self.Block(BlockType(...)), ...)`: chain-connect between blocks, in `contents`
  - Return of `self.chain` can be unpacked into a tuple of chained blocks, and the chain object (itself).
    Naming of the chain object is optional.
  - Elements are chained from left (outputs) to right (inputs)
  - The first argument to chain may be a port or block with an `InOut` or `Output`-tagged port.
  - Middle elements must be a block with an `InOut`-tagged port, or `Input`- and `Output`-tagged ports.
  - The last argument to chain may be a port or block with an `InOut` or `Input`-tageed port.
- Assign names to components by assigning the object to a `self` variable:
  - `self.subblock_name = self.Block(BlockType(...))`
  - `(self.subblock_name1, self.subblock_name2, ...), self.chain_name = self.chain(...)`

### Generators
Generators allow some Python code to run that has access to the solved values of some parameters.
TODO - write this section pending generator refactoring, in the meantime see the port array section of the getting started tutorial.


### Footprint
FootprintBlock is a block that is associated with a PCB footprint.

All primitives that can be called inside `Block`'s  `__init__(...)` can be called inside `__init__(...)`

These can be called inside `contents()`:
- `self.footprint(refdes='R', footprint='Resistor_SMD:R_0603_1608Metric', pinning={...})`: associates a footprint with this block
  - Pinning argument format: `{'pin_name': self.port, ...}`: associates footprint pins with ports or subports
  - Optional arguments: `mfr='Manufacturer A', part='Part Number', value='1kOhm', datasheet='www.example.net'`


## Port and Link Libraries

### Single-wire Ports
- `VoltageLink`: voltage rail
  - `VoltageSource(voltage_out, current_limits)`: voltage source
  - `VoltageSink(voltage_limits, current_draw)`: voltage sink (power input)
- `DigitalLink`: low-speed (up to ~100 MHz) digital signals, modeling voltage limits and input / output thresholds
  - `DigitalSource(voltage_out, current_limits, output_thresholds)`: digital output-only pin
    - `output_thresholds` is the range of (maximum low output, minimum high output) 
  - `DigitalSink(voltage_limits, current_draw, input_thresholds)`: digital input-only pin
    - `input_thresholds` is the range of (maximum low input, minimum high input)
  - `DigitalBidir(...)`: digital bidirectional (eg, GPIO) pin 
     - Has all arguments of `DigitalSource` and `DigitalSink`
- `AnalogLink`: analog signal that models input and output impedance
  - `AnalogSource(voltage_out, current_limits, impedance)`: analog output
  - `AnalogSink(voltage_limits, current_draw, impedance)`: analog signal input
- `PassiveLink`: connected copper that contains no additional data
  - `Passive`: single wire port that contains no additional data, but can be adapted to other types (eg, with `.as_voltage_source(...)`).
    Useful for low-level elements (eg, resistors) that can be used in several ways in higher-level constructs (eg, pull-up resistor for digital applications).

### Bundle Ports
- `I2cLink`: I2C net, consisting of `.scl` and `.sda` Digital sub-ports.
  - `I2CMaster(model)`: I2C master port
    - `model`: DigitalBidir model for both SCL and SDA sub-ports
  - `I2CSlave(model)`: I2C slave port
- `SpiLink`: SPI net, consisting of `.sck`, `.miso`, and `.mosi` Digital sub-ports. CS must be handled separately. 
  - `SpiMaster(model, frequency)`: SPI master port
    - `frequency`: range of allowable frequencies, generally including zero
  - `SpiSlave(model, frequency)`: SPI slave port
- `UartLink`: UART net, consisting of `.tx` and `.rx` Digital sub-ports in a crossover point-to-point connection.
  - `UartPort(model)`: UART port
- `UsbLink`: USB data net, consisting of `.dp` (D+) and `.dm` (D-) Digital sub-ports in a point-to-point connection.
  - `UsbHostPort`: USB host
  - `UsbDevicePort`: USB device
  - `UsbPassivePort`: other components (eg, TVS diode) on the USB line
- `CanLogicLink`: CAN logic-level (TXD/RXD) net, consisting of `.txd` and `.rxd` Digital sub-ports in a point-to-point connection.
  - `CanControllerPort(model)`: CAN controller-side port 
  - `CanTransceiverPort(model)`: CAN transceiver-side port
- `CanDiffLink`: CAN differential (CANH/CANL) net, consisting of `.canh` and `.canl` Digital sub-ports in a bus connection.
  - `CanDiffPort(model)`: CAN node port
- `SwdLink`: SWD programming net, consisting of `.swdio`, `.swclk`, `.swo`, and `.reset` Digital sub-ports in a point-to-point connection.
  - `SwdHostPort(model)`: SWD host-side (programmer) port
  - `SwdTargetPort(model)`: SWD target-side (DUT) port 
- `CrystalLink`: crystal net, consisting of `.xi` and `.xo` sub-ports in a point-to-point connection.
  - `CrystalDriver(frequency_limits, voltage_out)`: driver-side port
  - `CrystalPort(frequency)`: crystal-side port, indicating the frequency of the crystal 


## Block Libraries
The IDE's library tab provides a categorized list of available library blocks.
Many blocks also have a short descriptive docstring.


## Advanced Core Primitives
These are core primitives needed to model new ports and links

### Ports
Ports can have parameters and may be connected to each other via a Link.

Skeleton structure:
```python
class MyPort(Port[MyPortLinkType]):
  link_type = MyPortLinkType  # required
  bridge_type = MyPortBridgeType  # optional, if a bridge is needed
  
  def __init__(self) -> None:
    super().__init__()  # essential to call the superclass method beforehand to initialize state
    # declare elements like parameters here
```

These are properties of Ports:
- The Port type hierarchy currently is not used. However, inheritance may still be useful for code re-use / de-duplication.

These can be called inside `__init__(...)`:
- `__init__(...)` may take arguments, and no decorators (as with Block) are needed
- `self.Parameter(ParameterType(optional_value))`: declare parameters, optionally with a value 

### Bundles
Bundles are a special type of Port that is made up of constituent sub-Ports.

Skeleton structure:
```python
class MyBundle(Bundle):
  link_type = MyBundleLinkType
  bridge_type = MyBundleBridgeType  # optional, if a bridge is needed
  
  def __init__(self) -> None:
    super().__init__()  # essential to call the superclass method beforehand to initialize state
    # declare elements like parameters here
```

In addition to the primitives that can be called inside `Port`'s `__init__(...)`, these can be called inside `Bundle`'s  `__init__(...)`:
- `self.Port(PortType(...))`: declare bundle sub-port

### Links
Links define propagation rules for connected Ports.

Links are structured the same as Blocks, with similar primitives (see the Block documentation for details):
```python
class MyPortLink(Link):
  def __init__(self) -> None:
    super().__init__()  # essential to call the superclass method beforehand to initialize state
    # declare ports here

  def contents(self) -> None:
    super().contents()  # essential to call the superclass method beforehand to initialize state
    # declare constraints and internal connections here
```

These are properties of Links:
- Each Port can have one type of associated link.
- The Link type hierarchy currently is not used. However, inheritance may still be useful for code re-use / de-duplication.
- Extend `CircuitLink` instead of `Link` to copper-connect all ports.

These can be called inside `__init__()`:
- `__init__()` cannot have arguments, since links are always inferred
- `self.Parameter(ParameterType(optional_value))`
- `self.Port(PortType(...))` (without tags, but can have optional)
  
These can be called inside `contents()`:
- `self.connect(self.port1.subport, self.port2.subport, ...)`: for Bundle ports, connect sub-ports and infer inner link
  - Naming is optional.
- `self.constrain(...)`

### Bridges
Bridges are a special type of `Block` that adapts from a Link-facing (inner, `self.inner_link`) port to a Block edge (outer, `self.outer_port`) port.
Extend `CircuitPortBridge` instead of `PortBridge` to copper-connect all ports.

In `__init__()` (may not take arguments), declare these two required ports.
In `contents()`, add constraints as needed.

### Adapters
PortAdapters are a special type of `Block` that adapts / converts from a source (`self.src`) port to a destination (`self.dst`) port.
Extend `CircuitPortAdapter` instead of `PortAdapter` to copper-connect all ports.

In `__init__(...)` (may take arguments, must decorate with `@init_in_parent` if arguments), declare these two required ports.
In `contents()`, add constraints as needed.
