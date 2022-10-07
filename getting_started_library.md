## Adding Parts
_In this section, we will add a custom subcircuit block, an [MCP9700](http://ww1.microchip.com/downloads/en/DeviceDoc/20001942G.pdf) temperature sensor in SOT-23-3, by defining the component / footprint `Block`, then the encapsulating application circuit as another `Block`._

### Defining the component
We start off by defining the MCP9700 component using a `CirciutBlock` that provides footprint and pinning facilities.
**Add this as a new class in your `blinky_skeleton.py`**:
```python
class Mcp9700_Device(CircuitBlock):
  def __init__(self) -> None:
    super().__init__()
    # block boundary (ports, parameters) definition here 

  def contents(self) -> None:
    super().contents()
    # block implementation (subblocks, internal connections, footprint) here
```
> `CircuitBlock` is a subtype of `Block` that effectively is one footprint, and provides the `self.footprint(...)` method described in more detail below.
> If you think of a `Block` as analogous to a hierarchical sub-sheet, a `CircuitBlock` would be analogous to a schematic symbol.

> `__init__` is meant to define the interface of a block (all Ports and Parameters), while `contents` is meant to define the contents of a block (largely Blocks, connections, and constraints).
> This split is not enforced (and there are cases where it is desirable to mix them into just `__init__`), but the main benefits of this are performance (avoid elaborating the full design tree unnecessarily) and separation for readability.

According to the datasheet, the MCP9700 has three pins: Vdd (power), Vout (analog output), and GND (power), which we will model using the `EletricalSink`, `AnalogSource`, and `Ground` Port types, respectively.
Each takes arguments that can be sourced from the part's electrical characteristics table.
**In `__init__`, add this implementation**:
```python
self.vdd = self.Port(VoltageSink(
  voltage_limits=(2.3, 5.5)*Volt, current_draw=(0, 15)*uAmp
), [Power])
self.vout = self.Port(AnalogSource(
  voltage_out=(0.1, 2), current_limits=(0, 100)*uAmp,
  impedance=(20, 20)*Ohm
), [Output])
self.gnd = self.Port(Ground(), [Common])
```
> Limits are typically modeled with recommended operating conditions (as opposed to absolute maximum ratings) where available - for example, the 2.3v - 5.5v Vdd input limit.
> Other parameters are modeled for worst case / full range - for example, the 15uA maximum current draw, the impedance being exactly 20 Ohm (since no tolerance is given), or the full output range derived from the rated temperature range and temperature coefficient.
> The Ports are also specified with `Tag`s (like `Power` and `Common`) to enable implicit connection domains.

> Currently, we only model electrical characteristics - so while data like temperature range and accuracy would be useful, those are not currently modeled.

**In `contents`, add the footprint and pinmap (mapping footprint pins to `Block` ports)**:
```
self.footprint(
  'U', 'Package_TO_SOT_SMD:SOT-23',
  {
    '1': self.vdd,
    '2': self.vout,
    '3': self.gnd,
  },
  mfr='Microchip Technology', part='MCP9700T-E/TT',
  datasheet='http://ww1.microchip.com/downloads/en/DeviceDoc/20001942G.pdf'
)
```
> `self.footprint(refdes_prefix, footprint, pinning, [mfr=...], [part=...], [datasheet=...]` defines the footprint of a `CircuitBlock`.
> The pinning is specified as a mapping (`dict`) of footprint pin numbers to the `CircuitBlock`'s ports.
> The current data model uses KiCad footprint names and pinnings, and DigiKey-style manufacturer names and part numbers.
> There can only be one `self.footprint` per `CircuitBlock`.
>
### Defining the application circuit
However, the chip we just defined isn't supposed to be used bare: its application circuit recommends a decoupling capacitor (between 0.1 and 1uF - we arbitrarily choose 0.1uF).
Here, we define a subcircuit block to encapsulate application circuit.
**Add this as another new class in your `blinky_skeleton.py`**:
```python
class Mcp9700(Block):
  def __init__(self) -> None:
    super().__init__()
    self.ic = self.Block(Mcp9700_Device())
    self.pwr = self.Export(self.ic.vdd)
    self.gnd = self.Export(self.ic.gnd)
    self.out = self.Export(self.ic.vout)

  def contents(self) -> None:
    super().contents()
    with self.implicit_connect(
        ImplicitConnect(self.pwr, [Power]),
        ImplicitConnect(self.gnd, [Common])
    ) as imp:
      self.vdd_cap = imp.Block(DecouplingCapacitor(capacitance=0.1*uFarad(tol=0.2)))
```

> This is a typical pattern for many devices: define the chip as a `CircuitBlock`, then define a subcircuit `Block` containing its application circuit.

> self.Export creates a port on the current block that is directly connected to a port on an internal block, automatically propagating type and tag information.

> For decoupling capacitors, because tolerances are rarely explicitly specified, we use a loose 20% tolerance.

### Instantiating the temperature sensor
We can now instantiate the temperature sensor with a chain in the 3.3v implicit connection domain by **adding this line in our `BlinkyExample` circuit**:
```python
(self.temp, ), _ = self.chain(imp.Block(Mcp9700()), self.mcu.new_io(AnalogSink))
```

The final generated block diagram looks like:
![Full Blinky Hierarchy Block Diagram](docs/blinky_full_blocks.png)

> For reference, the complete block definition looks like:
> ```python
> self.usb = self.Block(UsbDeviceCReceptacle())
>
> with self.implicit_connect(
>     ImplicitConnect(self.usb.pwr, [Power]),
>     ImplicitConnect(self.usb.gnd, [Common]),
> ) as imp:
>   self.usb_reg = imp.Block(BuckConverter(output_voltage=3.3*Volt(tol=0.05)))
>
> with self.implicit_connect(
>     ImplicitConnect(self.usb_reg.pwr_out, [Power]),
>     ImplicitConnect(self.usb.gnd, [Common]),
> ) as imp:
>   self.mcu = imp.Block(Lpc1549_48())
>   (self.swd, ), _ = self.chain(imp.Block(SwdCortexTargetHeader()), self.mcu.swd)
>      
>   self.led = ElementDict[IndicatorLed]()
>   for i in range(8):
>     (self.led[i], ), _ = self.chain(self.mcu.new_io(DigitalBidir), imp.Block(IndicatorLed()))
>
>   (self.sw, ), _ = self.chain(imp.Block(DigitalSwitch()), self.mcu.new_io(DigitalBidir))
>   (self.temp, ), _ = self.chain(imp.Block(Mcp9700()), self.mcu.new_io(AnalogSink))
> ```
