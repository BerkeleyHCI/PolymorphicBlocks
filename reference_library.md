# Quick Reference, Library Construction

A short reference specifically for building subcircuit / part library blocks.

New? Consider reading through the [getting started guide](getting-started.md), including the subsequent sections on building library blocks.

Also see the [top-level board design reference](reference.md).

This document describes primitives and design patterns, also check out the many examples in the parts libraries. 

## Dragons be Ahead

The library design experience is much less polished and more intricate than the top-level board design experience.


## Blocks

`Block`s are a subcircuit that contain boundary ports, optional parameters, internal sub-blocks, and connections between them.

```python
class IndicatorLed(Block):
    def __init__(self, current_draw: RangeLike = (1, 10) * mAmp) -> None:
        super().__init__()
        self.current_draw = self.ArgParameter(current_draw)
        self.actual_current_draw = self.Parameter(RangeExpr())
        self.gnd = self.Port(Ground())
        self.signal = self.Port(DigitalSink(...))

    def contents() -> None:
        super().contents()
        self.led = self.Block(Led(...))
        self.res = self.Block(Resistor(resistance=self.signal.link().voltage / self.current_draw))
        self.assign(self.actual_current_draw, self.signal.voltage / self.res.resistance)
        self.connect(self.signal.net, self.led.a)
        self.connect(self.res.a, self.led.k)
        self.connect(self.gnd.net, self.res.b)
```

### Port Interfaces

- Boundary ports must be defined in `__init__`.
- Ports are connected with `self.connect(...)`; these may be part of a connect:
  - Boundary ports (as a unit) or their bundle inner ports (separately).
  - Boundary ports of sub-blocks (as a unit only).

> <details>
> <summary>Common Port Types</summary>
>
> - `Passive`: a single netlist pin without electrical modeling, a building block for ports with electrical modeling on top
>
> Single Wire Port that wrap (has-a) `Passive`:
> - `VoltageSource`, `VoltageSink`: models voltage and current, and their limits.
> - `DigitalSource`, `DigitalSink`, `DigitalBidir`: models voltage, voltage thresholds, current, and their limits.
>   Checks for multiple-driver conflicts, with multiple `DigitalBidir` drivers are allowed.
> - `AnalogSource`, `AnalogSink`: models voltage, current, and input/output impedance, and their limits.
>   Arbitrary requirement that the source has 1/10 the parallel impedance of sinks.
> 
> Bundle Ports
> - `I2cController`, `I2cTarget`: models I2C as two digital ports and address.
>   Checks for address conflicts.
> - `SpiController`, `SpiPeripheral`: models the shared SPI lines (excluding CS) as three digital ports.
> - `UartPort`: models UART TX/RX as two digital ports.
>   Connections generate a crossover connection.
> - `UsbHostPort`, `UsbDevicePort`: USB D+/D- ports
> - `CanControllerPort`, `CanTransceiverPort`: controller-side and transceiver-side RXD and TXD ports.
> - `CanDiffPort`: differential-side CAN (CANH, CANL) ports
> 
> See their class docstring and constructor for details.
> 
> See Design Patterns below for adapting between (some) port types.
> 
> </details>

### Parameters

Parameters are variables that can be passed into and through blocks.

- Parameters are defined purely symbolically and concrete values are not available to (non-generator) `Block`s.
- Parameters are restricted to a set of types supported by the compiler and the operations on them:
  - `BoolExpr` / `BoolLike`: boolean (true / false) variable
  - `IntExpr` / `IntLike`: numeric variable
  - `FloatExpr` / `FloatLike`: numeric variable
  - `RangeExpr` / `RangeLike`: range (interval) variable
  - `StringExpr` / `StringLike`: string (text) variable
  - See the `xExpr` class definition for supported operations.
  - See the generator section for how to use arbitrary Python code for calculations.
- Parameters must be defined in `__init__`, either with:
  - `self.ArgParameter(arg)`, to wrap `__init__` argument `arg`.
    Use the `xLike` type for `__init__` arguments, which also allow the literal Python value.
  - `self.Parameter(ParameterType())` (for a parameter without a value, to be assigned in `contents()`).
    Use the `xExpr` type in `Parameter(...)` to declare a parameter without a value, to be assigned in `contents()`.
- `RangeExpr` types are used to represent a device tolerance or toleranced specification
  - Most operations between `RangeExpr` types are tolerance-expanding (computes the worst-case range of the inputs)
  - `a = c.shrink_multiply(b)` returns `a` such  that tolerance-expanding `a * b` is equal to `c`.
    Example: for `v = i * r`, to solve for allowable (target) `r` given requirement `i` and contributing tolerance `v`, use `r = (1/i).shrink_multiply(v)`
- Access parameters on the link of ports using `port.link().link_param`.
  Links contain the aggregated parameter of all connected ports, for example the voltage.


### Footprints

## Schematic-Defined Blocks

## Generators

## Abstract Blocks

### Mixins

### Parts Tables and Passives

## Design Patterns and Conventions

### Link Circular Dependencies
Be cognizant of circular dependencies on links, e.g. something depending on a link's current to calculate its voltage will play badly with another block on the link that calculates its voltage based on the link's current.

### Target and Actual Parameters

### _Device Footprint and Subcircuit

### Passive and Typed Layers
use passive .net and adapt_to

### PassiveConnector



## Custom Ports and Links

### Links

Design patterns: aggregation and assertion

### Bridges

Design pattern: propagation

### Adapters









## Under Construction

Parts of this reference are outdated.


## Parameters


## Blocks
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
  - The last argument to chain may be a port or block with an `InOut` or `Input`-tagged port.
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
