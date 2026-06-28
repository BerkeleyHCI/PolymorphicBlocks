# Quick Reference

A short reference for writing HDL code.

New? Consider reading through the [getting started guide](getting-started.md).

Also see the [reference for building subcircuit / part library blocks](reference_library.md).


### DesignTop Block
`Block`s represent a subcircuit (including the top-level circuit) and contain inner blocks and connections between them.

```python
class MyBoard(SimpleBoardTop):
    def contents(self) -> None:
        # declare subblocks and connections here
        super().contents()  # required to call this superclass method        
        self.mcu = self.Block(IoController())
        self.led = self.Block(IndicatorLed())
        self.connect(self.mcu.gpio.request("led"), self.led.signal)
        self.connect(self.mcu.gnd, self.led.gnd)

    def refinements(self) -> Refinements:
        # refinements describe modifications across the design hierarchy
        return super().refinements() + Refinements(
            class_refinements=[
                (IoController, Esp32c3),  # replace all abstract IoController with Esp32c3
            ],
            instance_refinements=[
                (["mcu"], Esp32c3),  # replace mcu with Esp32c3, redundant with the above class refinement
            ],
            instance_values=[
                (["mcu", "pin_assigns"],  ["led=3"])  # assign LED to footprint pin 3
            ],
        )
```

- `SimpleBoardTop` maps abstract passive components to the JLC parts library and relaxes some strict constraints that do not matter for maker-type boards.
- Alternatively, use `DesignTop` (which has no default mappings) or `JlcBoardTop` (which has JLC part mappings).


### Block definition

```python
self.block_name = self.Block(BlockType(...))
```

- All blocks must have a unique name as a `self` variable (this preserves netlist stability for layout).
- Some blocks may take arguments, see their `__init__` for details.
- Builtin parts (like ICs) are in [the parts folder](edg/parts) and builtin circuits are in [the circuits folder](edg/circuits).
- See [the examples](examples/) for common blocks and how they're used.
- Abstract blocks can be instantiated, but require a refinement in the top-level design.
  - Some DesignTop subclasses like `SimpleBoardTop` provide default refinements.

#### Range Arguments

```python
self.reg = self.Block(LinearRegulator(3.3 * Volt(tol=0.05)))
```

- Blocks commonly take arguments as a range-like type, typically a specification for an allowable range accounting for tolerance stackup.

#### ElementDict

```python
self.block_name = ElementDict[IndicatorLed]()
for i in range(4):
    self.block_name[i] = self.Block(IndicatorLed())
```

- `ElementDict` provides an internal namespace for blocks, by index name.
- Use this to construct (and uniquely name) arrays of blocks.


### Connections

```python
self.connect(self.block1.port, self.block2.port, ...)
```

- `self.connect` connects ports on blocks, inferring the link type from the port types in the connection.
- `self.connect` returns a `Connection` object, which can be used in connections.
- Optionally assign a name to the `Connection` by assigning to a `self` variable.

#### Implicit Connection Blocks

```python
with self.implicit_connect(
    ImplicitConnect(self.pwr, [Power]),
    ImplicitConnect(self.gnd, [Common]),
) as imp:
    self.block_name = imp.Block(BlockType(...))
``` 

- `self.implicit_connect` creates a scope for implicit connections, which automatically connects ports on instantiated blocks by matching on tags like `Power` and `Common`.
- This is typically used to implicitly connect power (`Power` tag) and ground (`Common` tag) ports.

#### Chain Connections

```python
(self.led,), _ = self.chain(imp.Block(IndicatorSinkLed()), self.mcu.gpio.request("led"))
```

- `self.chain` connects ports in a chain, from left to right.
- Blocks in the chain are connected to:
  - their `Input` tagged port, for an incoming connection from the left,
  - their `Output` tagged port, for an outgoing connection to the right,
  - their `InOut` tagged port, for both incoming and outgoing connections (tapped connection).
- This returns a tuple of `(blocks...), chain`.
  Blocks must be named, the chain object can be optionally named to name the interior nets.

#### .connected(...)

```python
self.tp_gnd = self.Block(GroundTestPoint()).connected(self.gnd)
```

- Some (but far from all) blocks define a `.connected(...)` as a shorthand connection method, see each class's API for details.


### Refinements

```python
def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
        class_refinements=[
            (IoController, Esp32c3),
        ],
        instance_refinements=[
            (["mcu"], Esp32c3),
        ],
        instance_values=[
            (["mcu", "pin_assigns"],  ["led=3"])
        ],
        class_values=[
            (SelectorArea, ["footprint_area"], Range.from_lower(1.5)),
        ]
    )
```

- Refinements allow specifying, at the top level, modification across the design hierarchy.
- `class_refinements` replaces all instances of a block type with a subclass.
- `instance_refinements` replaces a specific instance of a block with a subclass.
  The instance is specified as a path, as a list of block names from the root.
- `instance_values` sets a parameter value on a specific instance of a block, specified as a path.
- `class_values` sets a parameter value on all instances of a block type.
  It is specified as a class, then a sub-path to the parameter.


### Parts Table Parts

- Some blocks, particularly discrete components like `Resistor`s and `Fet`s, are implemented as automatic selection from a parts table.
- These are some common top-level refinements:
  - Class refinement`(SelectorArea, ["footprint_area"], Range.from_lower(1.5))`: require a minimum footprint courtyard area in mm²
    - These are common minimum areas for passives: 01005=0.72, 0201=0.98, 0402=1.74, 0603=4.32, 0805=6.38, 1206=10.21.
  - Instance refinement `(["part_table_block", "excluded_parts"], ["1N2127"])`: exclude parts from selection, e.g., if they're out-of-stock.
  - Instance refinement `(["part_table_block", "part"], "1N2127")`: require a particular part.
  - Instance refinement `(["part_table_block", "footprint_spec"], "Diode_SMD:D_SMA")`: require a particular footprint.


### IoController

```python
self.mcu = imp.Block(IoController())
self.connect(self.mcu.gpio.request("led"), self.led.signal)
```

- `IoController` is an abstract class for any programmable IO controller, typically microcontrollers, but also including FPGAs.
- `IoController`s have a `gnd` and `pwr` input power ports, and `gpio`, `adc`, `spi`, `i2c`, `uart`, and `usb` Vector IO ports which elements can be requested from.
- Not all `IoController`s support all IO types, see each class's API for details.
- The `request(...)` name is used in the `pin_assigns` refinement, with each entry specified as either `led=3` (by footprint pin number) or `led=GPIO4` (by IO name, see each class's API for details).


### Mixins

```python
# require additional ports defined by a mixin
self.connect(self.can.controller, self.mcu.with_mixin(IoControllerCan()).can.request("can"))

# require a mixin as a refinement constraint only
self.mcu.with_mixin(IoControllerWifi())
```

- Mixins are a way to require additional functionality on an abstract block, they restrict refinements to concrete classes that implement the mixin.
- Mixins can optionally define ports and parameters.
- IoController has these mixins:
  - defining IO ports: `IoControllerDac`, `IoControllerI2cTarget`, `IoControllerSpiPeripheral`, `IoControllerTouchDriver`, `IoControllerCan`, `IoControllerUsbCc`, `IoControllerI2s`, `IoControllerDvp8`
  - connectivity requirements only: `IoControllerWifi`, `IoControllerBluetooth`, `IoControllerBle`
  - defining power ports, typically for microcontroller dev boards: `IoControllerPowerOut`, `IoControllerUsbOut`, `IoControllerVin`


### Connector Blocks

```python
class CustomUartConnector(Block):
    def __init__(self) -> None:
        super().__init__()
        self.gnd = self.Port(Ground(), [Common])
        self.pwr = self.Port(VoltageSink(), [Power])
        self.uart = self.Port(UartPort())

        self.conn = self.Block(PassiveConnector(length=4)).connected(
            {
                "1": self.gnd,
                "2": self.pwr,
                "3": self.uart.tx,
                "4": self.uart.rx,
            }
        )
```

- Custom connectors are implemented as a `Block` with ports representing its IOs.
- `self.port_name = self.Port(...)` defines a port on the block.
- Ports must be typed, the `Passive` port type is not automatically connectable to typed single-wire ports like `Ground` or `VoltageSink` without explicit adapters.
- Ports take electrical modeling parameters (like voltage and current limits) as parameters, empty parameter generally means an ideal port.
- `PassiveConnector` is an abstract class for connectors with a parameterizable number of passive-typed pins, including 2.54mm headers, FPCs, and more.
- `PassiveConnector.connected(...)` automatically adapts typed ports to the connector's Passive ports.

### Sub-boards and Connector Pairs

```python
class LedSubboard(SubboardBlock):
    def __init__(self) -> None:
        super().__init__()

        self.led = self.Block(IndicatorLed())
        self.gnd = self.Export(self.led.gnd, [Common])
        self.signal = self.Export(self.led.signal, [Input])

        self.conn = self.Block(Fpc050SocketTabPair(2), external=True)
        self.export_tap(self.gnd.net, self.conn.pins.request("1"))
        self.export_tap(self.io.net, self.conn.pins.request("2"))
```

- Subboards are `Block`s that define a subcircuit that is its own board (generates a separate netlist).
- These are defined `Block`s that have their subcircuits inside and exported ports crossing the physical board boundary.
- These use a `SubboardConnectorPair` block (like `Fpc050SocketTabPair`) to define the physical connector pair.
  - `SubboardConnectorPair` are similar to `PassiveConnector`, with `Passive` typed ports. 
    - Typed ports (like `Ground` or `VoltageSink`) internally contain a `Passive` `net` which can be attached to the connector's `Passive`ports.
  - `self.export_tap` behaves similar to `self.connect`, but attaches the inner port to the outer port without propagating parameter values (non-physical attachment).
    Conceptually, the connector taps onto (or hangs off) the parameter-propagating Export connection.


### Overriding Values / "Waiving" ERCs

- Some of the electrical modeling may have overly strict limits or overly broad operating parameters resulting in compiler errors from ERC failures, use refinements to override their values. 
- Values can be inspected via:
  - CLI compiler error messages for values failing constraints,
  - the IDE,
  - or, the .json generated during compilation which contains the entire compiled / solved design.

