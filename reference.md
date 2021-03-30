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
Generators provide a define-able `generate()` method (instead of `contents()`) that is run after its parent (enclosing) hierarchy blocks have been solved, and can get the Python value (eg, float) of parameters of itself, its ports, and links.

In addition to the primitives that can be called inside `Block`'s `contents()`, these can be called inside `generate()`: 
- `self.get(self.parameter)`: returns the Python value (eg, `bool`, `float`, `Tuple[float, float]`, `str`) of a parameter.
  - Optional argument: `default=default_value`: returns a default value (instead of raising an exception) if the parameter has no value 

### CircuitBlock
CircuitBlocks are a block that is associated with one PCB footprint.

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
The libraries listed here are primarily abstract parts, which are recommended so designs can be generic and leaves the selection of concrete parts to later.
Some of these will have a default refinement (eg, passives) widely applicable for an intermediate level design (eg, 0603 SMD parts), while more specialized parts (eg, boost converters) will not. 

### Discrete (as application wrapper)
- `PullupResistor(resistance)`, `PulldownResistor(resistance)`: one port connected to a voltage rail or ground, the other port connected to the digital signal line
- `DecouplingCapacitor(capacitance)` (voltage is inferred from connected ports): one port connected to a voltage rail, the other connected to ground
- `VoltageDivider(output_voltage, ratio, impedance)` (either `output_voltage` or `ratio`, input voltage inferred from connected ports): power and ground connected to voltage rails, with the divided output as an AnalogSource with the appropriate parallel impedance
  - `SignalDivider(ratio, impedance)`: similar to VoltageDivider, but with an input AnalogSink instead of a voltage rail
- `DigitalLowPassRc(impedance, cutoff_freq)`: low-pass RC filter with a DigitalSink input and DigitalSource output 
- `DigitalSwitch()`: one port connected to ground, the other to the digital line, and pressing the button shorts the digital line low
- `I2cPullup()`: one port connected to a voltage rail, the other port connected to the I2C bus
- `OscillatorCrystal(frequency)`: one port connected to ground, the other to a crystal driver
- TVS diodes: `UsbEsdDiode()`, `CanEsdDiode()`: one port connected to ground, the other to the signal line(s)
- `IndicatorLed()`: LED-resistor circuit, one port connected to ground, the other to a digital signal
- `IndicatorSinkRgbLed()`: RGB LED with resistors, on port connected to ground, and a digital signal for each of R, G, B 

### Power Converters
- `DcDcConverter(output_voltage)` (output current inferred from connected ports): abstract DC-DC converter with common ground that provides the target voltage
- `LinearRegulator(output_voltage)` (output current inferred from connected ports): linear regulator that provides the target voltage
- `DcDcSwitchingConverter(output_voltage, ripple_current_factor, input_ripple_limit, output_ripple_limit)` (all ripple arguments have sensible defaults): switching (high efficiency) DC-DC converters with common ground
  - `BuckConverter(output_voltage, ...)`, `BoostConverter(output_voltage, ...)` (shares full argument list with DcDcSwitching converter)
 
### Connectors
- `SdSocket()`, `MicroSdSocket()`: SD card socket
- `SwdCortexTargetConnector()`: 10-pin SWD target connector, with power modeled as going into the port from the DUT (but actually bidirectional - it's a direct copper connection)
- `PowerBarrelJack(voltage_out, current_limits)`: barrel jack that provides the specified voltage
- `UsbDeviceConnector()`: USB device-side connector, providing power (Vbus) and data (USB D+/D-) lines, including any adapter circuitry as necessary (eg, CC pull resistors for a type-C receptacle) 

### Microcontrollers
Microcontrollers are modeled as a grab-bag of IOs.
Call `.new_io(RequestedPortType)` to return a fresh (new) IO of a given type, optionally also passing in a `pin=...` argument to specify the pin(s) to assign.

- `Lpc1549_48()`, `Lpc1549_64()`: LPC1549 Cortex-M3 microcontroller in QFP-48 or -64 package with switch matrix for peripheral pin mapping
- `Stm32f103_48()`: STM32F103Cxxx microcontroller in QFP-48 package
- `Nucleo_F303k8()`: Nucleo-32 (pinned, breadboardable module) F303K8 that also sources power from USB 

### Other Components
- `Qt096t_if09()`: 0.96" 160x80 color LCD module with FPC socket
- `E2154f2091()`: tri-color (red / black / white) E-ink display with FPC socket
- `Lm4871()`: speaker driver with AnalogSink input
- `BlueSmirf()`, `Xbee_S3b()`: various RF modules
- `CanTransceiver()`: abstract CAN transceiver 


## Advanced Core Primitives
These are core primitives needed to model new ports and links

### Ports
Ports can have parameters and may be connected to each other via a Link.

Skeleton structure:
```python
class MyPort(Port[MyPortLinkType]):
  def __init__(self) -> None:
    super().__init__()  # essential to call the superclass method beforehand to initialize state
    self.link_type = MyPortLinkType  # required
    self.bridge_type = MyPortBridgeType  # optional, if a bridge is needed
    self.adapter_types = [MyPortToOtherAdapter]  # optional, for any adapters
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
  def __init__(self) -> None:
    super().__init__()  # essential to call the superclass method beforehand to initialize state
    self.link_type = MyBundleLinkType
    self.bridge_type = MyBundleBridgeType  # optional, if a bridge is needed
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
