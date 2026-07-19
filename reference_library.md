# Quick Reference, Library Construction

A short reference specifically for building subcircuit / part library blocks.

New? Consider reading through the [getting started guide](getting-started.md), including the subsequent sections on building library blocks.

Also see the [top-level board design reference](reference.md).

This document provides a quick reference and list of common primitives and design patterns.
However, your best resource is going to be all the examples in the parts libraries. 

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
        self.gnd = self.Port(Ground(), [Common])
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

- The `Block` API for top-level board design is also available in subcircuit `Block`s.

### Port Interfaces

- Boundary ports are defined with `self.Port(PortType(...)` and must be defined in `__init__`.
  - Boundary ports may optionally have `tags=[...]` to support implicit connections.
    Common tags are `Power` (v+), `Common` (gnd).
    Tags to support `chain` are `Input`, `Output`, and `InOut`.
  - Boundary ports may optionally define `optional=True` to indicate that the port may be left unconnected.
  - Use `PortType.empty()` to define a port without modeling, where its modeling is defined by the inner port it is connected to.
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

Quirks:
- `port.link().link_param` will be undefined for an unconnected port.
  For optional ports, gate checks with `port.is_connected().else_then(..., ...)`.
  This may be fixed eventually, see [#360](https://github.com/BerkeleyHCI/PolymorphicBlocks/issues/360).

### Footprints

The `FootprintBlock` base class is a `Block` that defines at most one footprint.

```python
class Sk6812Mini_E(FootprintBlock):
    def __init__(self) -> None:
        super().__init__()
        self.gnd = self.Port(Ground())
        self.vdd = self.Port(VoltageSink(...))
        self.din = self.Port(DigitalSink(...))
        self.dout = self.Port(DigitalSource(...))

    def contents(self) -> None:
        self.footprint(
            "D",
            "edg:LED_SK6812MINI-E",
            {"1": self.vdd, "2": self.dout, "3": self.gnd, "4": self.din},
            mfr="Opsco Optoelectronics",
            part="SK6812MINI-E",
            datasheet="https://cdn-shop.adafruit.com/product-files/4960/4960_SK6812MINI-E_REV02_EN.pdf",
        )
```

- `self.footprint(...)` defines the footprint associated with this block and its pinning and takes these arguments:
  - `refdes`
  - `footprint`: KiCad footprint name.
  - `pinning`: dictionary mapping footprint pin numbers to ports.
    - Pin numbers must be `str` or `Tuple[str, ...]` (for multi-pin pads).
    - Ports must be `Passive` or `HasPassive`.
  - Optional metadata `mfr`, `part`, `value`, `datasheet`.
  - Optional pick-and-place metadata `pnp_rot`, `pnp_offset` for KiCad footprint to JLC PCBA PnP data. 
- While not (yet) forbidden, `FootprintBlock`s should not have inner sub-`Block`s.

## Schematic-Defined Blocks

`KiCadSchematicBlock` is a `Block` that is defined by a KiCad schematic sheet.

```python
class MySchematicDefinedBlock(KiCadSchematicBlock):
    def __init__(self) -> None:
        super().__init__()
        self.gnd = self.Port(Ground())
        self.pwr = self.Port(VoltageSink(...))

    def contents(self) -> None:
        super().contents()
        self.import_kicad(
          self.file_path(f"{self.__class__.__name__}.kicad_sch"),
          conversions={'pwr': VoltageSink(...), 'gnd': Ground()},
          auto_adapt=True
        )
```

- The HDL stub is required to define the boundary ports and parameters.
- Graphical schematic components map as follows:
  - Labels, including symbols like GND and VCC, connect internally  
  - Hierarchical labels connect to the boundary ports
  - True global labels (that connect design-wide) are not supported)
  - Components map to `Block`s, with rhe refdes mapping to the `Block` name.
  - Wires map to `connect`s.
  - Pins must be connected at a wire end or bend.
- Components can be defined as:
  - Using a `KiCadInstantiableBlock` (which defines the symbol to port mapping), and the symbol has no footprint:
    - **Value parsing**: some blocks can parse the symbol value to parameters, see the table below.
    - **HDL instantiation**: the block is instantiated in HDL and the symbol refdes matches the HDL `Block` name and has no value.
    - **Inline HDL**: the symbol value starts with a `#` and contains Python code to instantiate the `Block`.
      Multi-line values supported using the `Value2`, `Value3`, ... fields.
  - **Blackboxing**, where the symbol has a footprint specified and is created as a `Block` with all `Passive` ports.
- Port connections are direct and types of connected pins must be compatible.
  - Use `conversions` to optionally specify a electrically typed `Port` model for a `Passive` `Port`.
  - Use `auto_adapt` to automatically insert ideal adapters from `Passive` `Port`s to the HDL-defined electrically typed boundary ports.

> <details>
> <summary>Common `KiCadInstantiableBlock`s</summary>
>
> With Passive-typed Ports, typically for constructing basic (sub)circuits:
> 
> | Symbol                             | HDL Block          | Value Parsing    |
> |------------------------------------|--------------------|------------------|
> | Device:C, Device:C_Polarized       | Capacitor          | e.g. `10uF 10V`* |
> | Device:R                           | Resistor           | e.g. `100`       |
> | Device:L                           | Inductor           |                  |
> | Device:Q_NPN_\*, Device:Q_PNP_\*   | Bjt.Npn, Bjt.Pnp   |                  |
> | Device:D                           | Diode              |                  |
> | Device:D_Zener                     | ZenerDiode         |                  |
> | Device:L_Ferrite                   | FerriteBead        |                  |
> | Device:Q_NMOS_\*, Device:Q_PMOS_\* | Fet.NFet, Fet.PFet |                  |
> | Switch:SW_SPST                     | Switch             |                  |
> * Capacitor voltage is required and is specified as the expected operating voltage, not a rating.
> 
> Where value parsing is empty, the Block can only be defined by HDL instantiation or inline HDL.
> 
> In many cases, the `_Small` (like `Device:C_Small`) symbol can also be used.
>
> With electrically-typed ports, typically used in higher-level subcircuits like analog signal-processing chains:
> 
> | Symbol                               | HDL Block             |
> |--------------------------------------|-----------------------|
> | Simulation_SPICE:OPAMP               | Opamp*                |
> | edg_importable:Amplifier             | Amplifier             |
> | edg_importable:DifferentialAmplifier | DifferentialAmplifier |
> | edg_importable:IntegratorInverting   | IntegratorInverting   |
> | edg_importable:OpampCurrentSensor    | OpampCurrentSensor    |
> * `Opamp`s include any datasheet-required supporting circuitry like decoupling capacitors.
> 
> Search for all subclasses of `KiCadImportableBlock` for a complete listing.
> 
> </details>

Guidance:
- Good uses include analog subcircuits where the graphical connectivity is complex and meaningful.
- This can be used to construct both library subcircuits as well a higher-level subcircuits like signal-processing chains using amplifier subcircuits.
- Most chip subcircuits are defined purely in HDL.

## Generators

`GeneratorBlock` is a `Block` that can retrieve the concrete value of its parameters and run arbitrary Python code to create its inner definition, including structural circuitry and parameters.

```python
class IndicatorLedArray(GeneratorBlock):
    def __init__(self, count: IntLike):
        super().__init__()
        self.count = self.ArgParameter(count)
        self.generator_param(self.count)
        
        self.gnd = self.Port(Ground.empty(), [Common])
        self.signals = self.Port(Vector(DigitalSink.empty()))
    
    def generate(self) -> None:
        super().generate()
        self.led = ElementDict[IndicatorLed]()
        for led_i in range(self.get(self.count)):
          led = self.led[str(led_i)] = self.Block(IndicatorLed())
          self.connect(...)
```

- `self.generator_param(...)` is required to declare parameters that the generator needs.
  - Only `ArgParameter`s, `port.is_connected()` and `port.elements()` are allowed.
- `self.get(...)` can be invoked in `generate()` to retrieve the concrete value of a parameter.

Guidance:
- Generators are necessary for parametric structural circuit construction.
- Prefer using non-generator expression operations for parameter calculations where possible.
  Generators should only be used where the expression operations are insufficient. 

## Abstract Blocks

`abstract_block`s are `Blocks` that define an interface that can be implemented by (concrete) subclasses.
They can be instantiated but will error during compilation if not refined.

```python
@abstract_block
class Led(Block):
    def __init__(self):
        self.a = self.Port(Passive.empty())
        self.k = self.Port(Passive.empty())
```

- Boundary ports and parameters are defined as usual.
- Ports are defined with `PortType.empty()` to allow subclasses flexibility in modeling.
  - Subclasses can specify modeling with `self.port.init_from(PortType(...))`.
    Replacing the port object is not allowed.
- A default refinement can be attached to the `abstract_block` with `@abstract_block_default(lambda: DefaultRefinementBlock)`. 
  - The `lambda` is required to break circular definitions.
  - Top-level designers can still override these refinements.

Guidance:
- Use `abstract_block`s to define a common interface for `Block`s that are drop-in interchangeable.
- You can always refactor to pull out a common `abstract_block` later.

### Mixins

`BlockInterfaceMixin`s define an interface that can be added to an `abstract_block`.

```python
# mixin interface definition
class RotaryEncoderSwitch(BlockInterfaceMixin[RotaryEncoder]):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.sw = self.Port(Passive.empty(), optional=True)

# concrete class implementing the mixin
class Ec11eWithSwitch(RotaryEncoderSwitch, RotaryEncoder):
    ...
```

- A `Block` definition can inherit multiple mixins (the `Block` implements multiple mixins).
- A `Block` instantiation can use multiple mixins (requiring the concrete `Block` refinement to implement those mixins).
- Mixin interface ports are typically `optional` to allow usage without the mixin.
  This may be a generator that provides a default connection in a basic usage configuration.

### Abstract Passives and Parts Tables

Many common passive and discrete parts (like `Resistor`, `Capacitor`, `Diode`) are `abstract_blocks` and support different (including user-defined) implementations, e.g. to support different vendors and distributors.

Many of these include a utility subclass for selecting a part from a table (like `TableResistor`, `TableCapacitor`, `TableDiode`).

These also provide a separate utility subclass that defines KiCad footprint to port mappings that implement the `HasStandardFootprint` interface (like `ResistorStandardFootprint`, `CapacitorStandardFootprint`, `DiodeStandardFootprint`).

These classes provide utility functions for parts table selectors:
- `PartsTablePart`: interface parameters (part requirement, excluded parts, and more) for part selected from a parts table.
- `PartsTableSelector`: utility code to select a part from a `PartsTable`, implementing `PartsTableSelector`.
- `SelectorFootprint`: interface parameters to allow filtering by footprint.
- `PartsTableFootprintFilter`: utility code to filter a parts table by footprint, implementing `SelectorFootprint`.
- `PartsTableSelectorFootprint`: utility code to construct the footprint, for a `HasStandardFootprint`. 

Look at some example implementations to for the `PartsTable` API and utilities.

## Design Patterns and Conventions

These are design patterns and conventions used in the included parts library.

### `_Device` Footprint and Subcircuit

The `x_Device` `Block` defines the footprint only, while the application circuit `Block` is the user-friendly name and instantiates `x_Device`.
`x_Device` is not exported in `__init__.py`.

### Passive and Typed Layers

Passive components are `Passive` port typed, and applications of them are separate `Block`s that instantiate the `Passive` typed `Block`s. 
This allows different implementation of the same `Passive` device, eg, `PullupResistor`, `PulldownResistor`.
Subcircuits follow this pattern too, with them instantiating the `Passive` typed `Block`, connecting the `Passive` ports internally and to the `Passive` `.net` of the electrically-typed boundary `Port`s.

### Target and Actual Parameters

Most parameters are defined as a target requirement.

The actual expected operating value may be calculated as a readout parameter and is prefixed `actual_`. 

### PassiveConnector

Devices that use a standard connector (like FPCs) should instantiate the appropriate `PassiveConnector` subclass to allow the system designer to make choices for the concrete connector.
`PassiveConnector` supports parameterized pin counts.

### Circular Dependencies

There is currently no structural prevention of circular parameter dependencies.

This may happen when a `Block` has a parameter that is calculated from a `Port`'s link, and the `Port`'s link is calculated from the `Block`'s parameter.
For example, the LED calculates current from the link's voltage, while a source block that calculates voltage from the link's current would be unsolvable.

We typically resolve this by using the user-specified range for one of the parameters and accepting that it will be a wider range than the actual operating range.


## Custom Ports and Links

Custom `Port`s and `Link`s can be defined.

`Port`s should define properties of that `Port` only, not properties influenced by any other connected `Port`.
The `Link` aggregates parameters on the connected `Ports` and optionally defines constraints as assertions.

`Port`s can contain other `Port`s, such as:
- bundles of `Port`s, like `SpiController`
- an inner `Passive` that provides the connectivity layer 

Look at examples in the standard interfaces library for details.

### Bridges

`PortBridge` are a quirk of the hierarchical model: how to expose a single boundary `Port` of a `Block` that is internally connecting multiple internal `Port`s.

`PortBridge` "aggregate" the `inner_link` (by connecting to a `Port` on that `Link`) and expose a single `outer_port`.

General design patterns:
- Parameters always propagate outward, never inward.
- Checks that require context at the outer level are handled by propagating the relevant parameters outward. 
- If needed, define additional internal parameters (`_`-prefixed) on the `Port` to propagate all the relevant data outward.

### Mixins

Mixins on `Port`s may be an interesting concept to support opt-in specialized parameter propagation without an excessive base (see [#333](https://github.com/BerkeleyHCI/PolymorphicBlocks/issues/333)) but do not have an implementation plan yet.
