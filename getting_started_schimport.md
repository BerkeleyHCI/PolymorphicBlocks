# Getting Started, Part 2: Schematic-Defined Library Blocks
_In this section, we build a graphical-schematic-defined HX711-based load cell amplifier subcircuit block and add it to our board._

> This section describes how to define a block in KiCad's graphical schematic editor and import it into an HDL flow.
> Blocks can also be defined in HDL using the same constructs used to define a board, which is covered in the [next section](getting_started_library.md).
>
> While defining blocks in HDL provides the most programming power, schematics can be a better option for blocks with complex connectivity or where the graphical arrangement is meaningful, in particular analog subcircuits.
> Graphical schematics may also be a more familiar interface and may be a good choice where programmatic generation is not necessary.
> 
> Schematic-defined blocks can make use of HDL library blocks (as schematic components), including all the automation (like automatic parts selection from a parts table) those libraries provide. 


## Schematic Definition
**Start by drawing the application schematic for the HX711**, as described in Figure 4 of its [datasheet](https://cdn.sparkfun.com/datasheets/Sensors/ForceFlex/hx711_english.pdf).

For common parts like capacitors, resistors, and transistors, we use the generic built-in KiCad symbols, which ultimately map down to HDL library blocks with parts selection automation.
A full list is available in the [reference section](#reference).
Parts where there isn't a corresponding library block can instead be defined with a footprint and pinning (like the HX711 chip here).

Hierarchical labels are used to define the block's boundary ports (electrical interface).

Our finished schematic looks like this and is available in [examples/resources/Hx711.sch](examples/resources/Hx711.sch):  
![HX711 schematic](docs/greybox_hx711.svg)

A few notes here:
- Labels like GND and VCC work as expected within this block.
- True global labels (which would directly connect to the rest of the design, not through the block's boundary ports) are not supported.
- Components mapping down to parameterized library blocks (like resistors and capacitors) must be defined with a value.
 See the [reference section](#reference) for details on formatting.


## HDL Stub
While the schematic defines the implementation, an HDL Block wrapper class is still required to interoperate with the rest of the system.
Start by **creating a empty `KiCadSchematicBlock` Block class:**

```diff
+ class Hx711(KiCadSchematicBlock):
+   def __init__(self) -> None:
+     super().__init__()
+     # block boundary (ports, parameters) definition here
+ 
+   def contents(self) -> None:
+     super().contents()
+     # block implementation (subblocks, internal connections, footprint) here
```

> `KiCadSchematicBlock` is a `Block` that is defined by a KiCad schematic.

Then, **define the ports in `__init__(...)`**, which must have the same name as the hierarchical labels:

```diff
  class Hx711(KiCadSchematicBlock):
    def __init__(self) -> None:
      super().__init__()
+ 
+     self.pwr = self.Port(VoltageSink.empty(), [Power])
+     self.gnd = self.Port(Ground.empty(), [Common])
+ 
+     self.dout = self.Port(DigitalSource.empty())
+     self.sck = self.Port(DigitalSink.empty())
+ 
+     self.ep = self.Port(Passive.empty())
+     self.en = self.Port(Passive.empty())
+     self.sp = self.Port(Passive.empty())
+     self.sn = self.Port(Passive.empty())

    def contents(self) -> None:
      super().contents()
      # block implementation (subblocks, internal connections, footprint) here
```

> Like the top-level board, the contents of a Block can be defined in `def contents(...)`.
> However, interfaces (like boundary ports and constructor parameters) must be defined in `def __init__(...)`.

> In the HDL model, ports must have a type.
> `Ground`, `VoltageSink`, `DigitalSource`, and `DigitalSink` are typed ports that have electronics modeling (e.g. voltage limits for `VoltageSink` and IO thresholds for `DigitalSink`).
> `Passive` represents a port with no electronics modeling and can be connected to any other `Passive` port.
> Unlike schematic ERC, `Passive` cannot be directly connected to a typed port and requires an adaptor (described later).
> 
> As these are intermediate ports (they connect to internal ports, here in the schematic), they must be `.empty()` to not define parameters like voltage limits which will be inferred from internal connections.

Then, **import the schematic**:

```diff
  class Hx711(KiCadSchematicBlock):
    def __init__(self) -> None:
      super().__init__()
      ...

    def contents(self) -> None:
      super().contents()
+ 
+     self.import_kicad("path/to/your/hx711.sch", auto_adapt=True)
```



```diff
  class Hx711(KiCadSchematicBlock):
    def __init__(self) -> None:
      super().__init__()
      ...

    def contents(self) -> None:
      super().contents()
  
+     self.Q1 = self.Block(Bjt.Npn((0, 5)*Volt, 0*Amp(tol=0)))
      self.import_kicad("path/to/your/hx711.sch", auto_adapt=True)
```


### Additional Modeling


## Top-Level Board


```diff
  class BlinkyExample(SimpleBoardTop):
    def contents(self) -> None:
      super().contents()
      ...

      with self.implicit_connect(
              ImplicitConnect(self.reg.pwr_out, [Power]),
              ImplicitConnect(self.reg.gnd, [Common]),
      ) as imp:
        self.mcu = imp.Block(IoController())

+       self.conn = self.Block(PassiveConnector(4))
+       self.sense = imp.Block(Hx711())
+       self.connect(self.mcu.gpio.request('hx711_dout'), self.sense.dout)
+       self.connect(self.mcu.gpio.request('hx711_sck'), self.sense.sck)
+       self.connect(self.conn.pins.request('1'), self.sense.ep)
+       self.connect(self.conn.pins.request('2'), self.sense.en)
+       self.connect(self.conn.pins.request('3'), self.sense.sp)
+       self.connect(self.conn.pins.request('4'), self.sense.sn)
```

## Reference

These symbols can be used in schematic-defined blocks and map to the following passive-typed HDL blocks:

| Symbol | HDL Block | Value Parsing | Notes |
|---|---|---|---|
| ducjs | cc | cc |
| ducjs | cc | cc |

These symbols may to non-passive-typed HDL blocks:


TODO:
SChematic: must delete value from BJT
Schematic: cap voltage must be cap V
