# Quick Reference

A short reference for writing HDL for (top-level) board designs.

New? Consider reading through the [getting started guide](getting-started.md).

Also see the [reference for building subcircuit / part library blocks](reference_library.md).


### DesignTop Block
`Block`s represent a subcircuit (including the top-level circuit) and contain inner blocks and connections between them.

```python
class MyBoard(SimpleBoardTop):
    def contents(self) -> None:
        # declare subblocks and connections here
        super().contents()  # required to call this superclass method first        
        self.mcu = self.Block(IoController())
        self.led = self.Block(IndicatorLed())
        self.connect(self.mcu.gpio.request("led"), self.led.signal)
        self.connect(self.mcu.gnd, self.led.gnd)
        self.sw = self.Block(DigitalSwitch())
        self.connect(self.mcu.gpio.request("sw"), self.sw.out)
        self.connect(self.mcu.gnd, self.sw.gnd)
        
    def refinements(self) -> Refinements:
        # refinements describe modifications across the design hierarchy
        return super().refinements() + Refinements(
            class_refinements=[
                (IoController, Esp32c3),  # replace all abstract IoController with Esp32c3
            ],
            instance_values=[
                (["mcu", "pin_assigns"],  ["led=3", "sw=6"])  # assign to footprint pins 3 and 6
            ],
        )
```

- `SimpleBoardTop` maps abstract passive components to the JLC parts library and relaxes some strict constraints that do not matter for maker-type boards.
- Alternatively, use `DesignTop` (which has no default mappings) or `JlcBoardTop` (which has JLC part mappings).


### Block definition

Internal blocks are created using `self.Block(...)` and must be assigned a unique name (in `self`) for netlist stability.

```python
self.block_name = self.Block(BlockType(...))
```

- Some blocks may take arguments, see their `__init__` for details.
- Builtin parts (like ICs) are in [the parts folder](edg/parts) and builtin circuits are in [the circuits folder](edg/circuits).
- See [the examples](examples/) for common blocks and how they're used.
- Abstract blocks can be instantiated, but require a refinement in the top-level design.
  - Some DesignTop subclasses like `SimpleBoardTop` provide default refinements.

#### Range Arguments

Blocks commonly take arguments as a range-like type, typically a specification for an allowable range accounting for tolerance stackup.

```python
self.reg = self.Block(LinearRegulator(3.3 * Volt(tol=0.05)))
```

#### ElementDict

`ElementDict` creates an internal namespace, providing an unique name for elements in an array of blocks by attaching their index to the name.

```python
self.block_name = ElementDict[IndicatorLed]()
for i in range(4):
    self.block_name[i] = self.Block(IndicatorLed())
```


### Connections

`self.connect` connects ports on blocks, inferring the link type from the port types in the connection.

```python
self.connect(self.block1.port, self.block2.port, ...)
```

- `self.connect` returns a `Connection` object, which can be used in connections.
- Optionally assign a name to the `Connection` by assigning to a `self` variable.
- Connections must be between ports of compatible type.
  Typed ports (like `Ground` or `VoltageSink`) are distinct from `Passive` ports and not connectable without adapters.
- Only the block's ports and inner blocks' ports can be connected.
  Connections cannot be made arbitrarily deep in the block hierarchy.

#### Implicit Connection Blocks

`self.implicit_connect` creates a scope for implicit connections, typically for power and ground.

```python
with self.implicit_connect(
    ImplicitConnect(self.pwr, [Power]),
    ImplicitConnect(self.gnd, [Common]),
) as imp:
    self.block_name = imp.Block(BlockType(...))
``` 

- Port matching is done against the block's ports' tags using tag objects `Power` and `Common`.

#### Chain Connections

`self.chain` connects ports (and ports on blocks) in a chain, from left to right.

```python
(self.led,), _ = self.chain(imp.Block(IndicatorSinkLed()), self.mcu.gpio.request("led"))
```

- `self.chain` returns a nested tuple of `((blocks...), chain)`.
  Blocks must be named, the chain object can be optionally named to name the interior nets.
- In the example above:
  - The trailing comma in `(self.led, )` unpacks the single-element blocks tuple to name it.
  - The `_` discards (does not name) the chain object.
- Blocks in the chain are connected to:
  - their `Input` tagged port, for an incoming connection from the left,
  - their `Output` tagged port, for an outgoing connection to the right,
  - their `InOut` tagged port, for both incoming and outgoing connections (tapped connection).

#### .connected(...)

Some (but far from all) blocks define a `.connected(...)` as a shorthand connection method, see each class's API for details.
These return the block itself, allowing it to be assigned to a name.

```python
self.tp_gnd = self.Block(GroundTestPoint()).connected(self.gnd)
```


### Refinements

Refinements allow specifying, at the top level, modifications across the design hierarchy.

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

- `class_refinements` replaces all instances of a block type with a subclass.
- `instance_refinements` replaces a specific instance of a block with a subclass.
  The instance is specified as a path, as a list of block names from the root.
- `instance_values` sets a parameter value on a specific instance of a block, specified as a path.
- `class_values` sets a parameter value on all instances of a block type.
  It is specified as a class, then a sub-path to the parameter.


### Parts Table Parts

- Some blocks, particularly discrete components like `Resistor`s and `Fet`s, are implemented as automatic selection from a parts table.
- These are some common top-level refinements:
  - Class refinement `(SelectorArea, ["footprint_area"], Range.from_lower(1.5))`: require a minimum footprint courtyard area, in mm²
    - Common minimum areas for passives, in mm²: 01005=0.72, 0201=0.98, 0402=1.74, 0603=4.32, 0805=6.38, 1206=10.21.
  - Instance refinement `(["part_table_block", "excluded_parts"], ["1N2127"])`: exclude parts from selection, e.g., if they're out-of-stock.
  - Instance refinement `(["part_table_block", "part"], "1N2127")`: require a particular part.
  - Instance refinement `(["part_table_block", "footprint_spec"], "Diode_SMD:D_SMA")`: require a particular footprint.


### IoController

`IoController` is an abstract class for any programmable IO controller, typically microcontrollers, but also including FPGAs.

```python
self.mcu = imp.Block(IoController())
self.connect(self.mcu.gpio.request("led"), self.led.signal)
```

- `IoController`s have `gnd` and `pwr` input power ports, and `gpio`, `adc`, `spi`, `i2c`, `uart`, and `usb` Vector IO ports which elements can be requested from.
- Not all `IoController`s support all IO types, see each class's API for details.
- The `request(...)` name is used in the `pin_assigns` refinement, with each entry specified as either `led=3` (by footprint pin number) or `led=GPIO4` (by IO name, see each class's API for details).
- These request types are available, and their pin assignment entries are:

  | Request Type            | Request Syntax                           | Pin Assignment Entries                                 |
  |-------------------------|------------------------------------------|--------------------------------------------------------|
  | Single Element          | `self.mcu.gpio.request("my_io")`         | `"my_io=3"`                                            |
  | Vector                  | `self.mcu.gpio.request_vector("my_ios")` | `"my_ios_0=3", "my_ios_1=4", ...` (underscore-indexed) |
  | Bundle (e.g., SPI, I2C) | `self.mcu.spi.request("my_spi")`         | `"my_spi.sck=3", "my_spi.mosi=4", ...` (dot-indexed)   |
  | Unnamed                 | `self.mcu.gpio.request()`                | Arbitrarily named, don't rely on this                  |


### Mixins

Mixins are a way to require additional functionality (or ports) on an abstract block, they restrict refinements to concrete classes that implement the mixin.

```python
# require additional ports defined by a mixin
self.connect(self.can.controller, self.mcu.with_mixin(IoControllerCan()).can.request("can"))

# require a mixin as a refinement constraint only
self.mcu.with_mixin(IoControllerWifi())
```

- IoController has these mixins:
  - defining IO ports: `IoControllerDac`, `IoControllerI2cTarget`, `IoControllerSpiPeripheral`, `IoControllerTouchDriver`, `IoControllerCan`, `IoControllerUsbCc`, `IoControllerI2s`, `IoControllerDvp8`
  - connectivity requirements only: `IoControllerWifi`, `IoControllerBluetooth`, `IoControllerBle`
  - defining power ports, typically for microcontroller dev boards: `IoControllerPowerOut`, `IoControllerUsbOut`, `IoControllerVin`


### Connector Blocks

Custom connectors are implemented as a `Block` with ports representing its IOs.

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

- `self.port_name = self.Port(...)` defines a port on the block.
- Ports must be typed, the `Passive` port type is not automatically connectable to typed single-wire ports like `Ground` or `VoltageSink` without adapters.
- Ports take electrical modeling parameters (like voltage and current limits) as parameters, empty parameter generally means an ideal port.
- `PassiveConnector` is an abstract class for connectors with a parameterizable number of passive-typed pins, including 2.54mm headers, FPCs, and more.
- `PassiveConnector.connected(...)` automatically adapts typed ports to the connector's Passive ports.

### Multipacking

Multipacking allows multiple components, potentially spread across the design hierarchy, to be combined into one component.
This is an optimization that may save board area and cost.
Example: quad-pack resistor networks, dual-pack opamps, RGB LEDs.

```python
class MyBoard(SimpleBoardTop):
    def contents(self) -> None:
        ...
    
    def multipack(self) -> None:
        self.res_pack = self.PackedBlock(ResistorArray())
        self.pack(self.res_pack.elements.request('0'), ['led[0]', 'res'])
        self.pack(self.res_pack.elements.request('1'), ['led[1]', 'res'])
        self.pack(self.res_pack.elements.request('2'), ['led[2]', 'res'])
        self.pack(self.res_pack.elements.request('3'), ['led[3]', 'res'])
```

- `multipack()` is a blend of `contents()` (in that `PackedBlocks` are declared within) and `refinements()` (in that it uses `List[str]` to reference blocks in the design hierarchy).
- `self.PackedBlock(...)` is similar to `self.Block(...)`.
- `self.pack(...)` takes two arguments:
  - `multipack_part`: the multipack element that is part of the packed block, either a block or an element of a dynamically-sized packed block array.
  - `path`: the path to the block which this replaces, as a list of strings.
- This remains correct ERC model-wise, elements of the packed block are modeled as being 'inside' the replaced block.  
- Each multipack element has its own ports, including for shared pins like the common power pins of a dualpack opamp.
  A compiler assertion checks that these are all connected to the same netlist net.
- Multipacking can only be defined at the BoardTop level.

### Sub-boards and Connector Pairs

Subboards are `Block`s that define a subcircuit that is its own board (generates a separate netlist).

```python
class LedSubboard(SubboardBlock):
    def __init__(self) -> None:
        super().__init__()

        self.led = self.Block(IndicatorLed())
        self.gnd = self.Export(self.led.gnd, [Common])
        self.signal = self.Export(self.led.signal, [Input])

        self.conn = self.Block(Fpc050SocketTabPair(2), external=True)
        self.export_tap(self.gnd.net, self.conn.pins.request("1"))
        self.export_tap(self.signal.net, self.conn.pins.request("2"))
```

- These are defined `Block`s that have their subcircuits inside and exported ports crossing the physical board boundary.
- These use a `SubboardConnectorPair` block (like `Fpc050SocketTabPair`) to define the physical connector pair.
  - `SubboardConnectorPair` are similar to `PassiveConnector`, with `Passive` typed ports. 
    - Typed ports (like `Ground` or `VoltageSink`) internally contain a `Passive` `net` which can be attached to the connector's `Passive` ports.
  - `self.Export(...)` creates a Port on the Block that is connected to (and takes on the type) of the inner port.
  - `self.export_tap` behaves similar to `self.connect`, but attaches the inner port to the outer port without propagating parameter values (non-physical attachment).
    Conceptually, the connector taps onto (or hangs off) the parameter-propagating Export connection.


### Overriding Values / "Waiving" ERCs

Some of the electrical modeling may have overly strict limits or overly broad operating parameters resulting in compiler errors from ERC failures, use refinements to override their values.

```python
class_refinements=[
    (Neopixel, ["pwr", "voltage_limits"], Range(3.0, 5.5)),  # kinda works-ish at 3.3v
]
```

- Values can be inspected via:
  - CLI compiler error messages for values failing constraints,
  - the IDE,
  - or, the .json generated during compilation which contains the entire compiled / solved design.
