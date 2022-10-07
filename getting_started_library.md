# Getting Started, Part 2: Building Library Blocks
_In this section, we build and add a digital magnetic field sensor ([LF21215TMR](https://www.littelfuse.com/~/media/electronics/datasheets/magnetic_sensors_and_reed_switches/littelfuse_tmr_switch_lf21215tmr_datasheet.pdf.pdf)) to our design._
_We do this in two stages, first defining a `FootprintBlock` for the chip itself, then building the wrapper application circuit `Block` around it._

> While `Block`s are arbitrary hierarchy blocks that only have ports, inner blocks, and connections, `FootprintBlock` also allows up to one PCB footprint, and a mapping from the block ports to footprint pins.
> In schematic terms, think of `FootprintBlock` as analogous to a schematic symbol, while `Block` is closer to a hierarchy sheet.


## Creating a part
A new block can be defined from the library browser.
Since we will be making a `FootprintBlock`, search for that in the library browser.
Then, select a point for insertion (top-level: outside any class or function) in the file being edited, right-click on FootprintBlock, select "Define New Subclass", and name it `Lf21215tmr_Device`.
It should insert this code:

```python
class Lf21215tmr_Device(FootprintBlock):
  def __init__(self) -> None:
    super().__init__()
    # block boundary (ports, parameters) definition here 

  def contents(self) -> None:
    super().contents()
    # block implementation (subblocks, internal connections, footprint) here
```

> `__init__` is meant to define the interface of a block (all Ports and Parameters), while `contents` is meant to define the contents of a block (largely Blocks, connections, and constraints).
> This split is not enforced (and there are cases where it is desirable to mix them into just `__init__`), but the main benefits of this are performance (avoid building the full design tree unnecessarily) and separation for readability.

To work with this part in the visual editor, you can instantiate this block in your top-level design.
Once you recompile, it should show up in the library browser.
Then, double-click into the newly created `Lf21215tmr_Device` block to set it for editing.

The chip itself has three pins:
- Vcc: voltage input, type **VoltageSink**
- GND: voltage input, type **VoltageSink**
- Vout: digital output, type **DigitalSource**

We can create ports through the library browser, by searching for the port name, then double-clicking to insert.
Ports show up at the end of the library browser, and can only be inserted with the caret in `__init__` (because it defines the block's interface).

Similar to inserting the barrel jack and buck converter blocks, these ports are also parameterized.
We will need to modify these with the appropriate parameters from the datasheet:
- operating supply voltage of 1.8-5.5v
- supply current of 1.5uA (nominal)
- output thresholds of 0.2v (low) and (Vcc-0.3) (high)

For Vcc, replace the `voltage_limits` and `current_draw`:
```python
self.vcc = self.Port(
  VoltageSink(voltage_limits=(1.8, 5.5)*Volt, current_draw=(0, 1.5)*uAmp))
```

For `gnd`, we have a special `Ground()` convenience constructor for voltage inputs used as ground:
```python
self.gnd = self.Port(Ground())
```

For `DigitalSource`, while we could write the parameters explicitly:
```python
# Don't do this, see better style below!

self.vout = self.Port(DigitalSource(
  voltage_out=(self.gnd.link().voltage.lower(),
               self.vcc.link().voltage.upper()),
  current_limits=1.5 * uAmp(tol=0),
  output_thresholds=(self.gnd.link().voltage.upper() + 0.2 * Volt,
                     self.vcc.link().voltage.lower() - 0.3 * Volt)
))
```

there's also a wrapper `DigitalSource.from_supply` that wraps the common way of specifying a digital output as offsets from voltage rails:
```python
self.vout = self.Port(DigitalSource.from_supply(
  self.gnd, self.vcc,
  output_threshold_offset=(0.2, -0.3)
))
```

> With a relatively simple example like this, you may be wondering why this needs an HDL instead of a diagram with properties sheet interface that supports mathematical expressions.
> That interface would have a few shortcomings:
> - First, it would be less straightforward to support wrappers like `DigitalSource.from_supply`.
    >   While possible, these wrappers may need to be baked into the tool (and limited to what the tool designers support), instead of being user-defineable.
> - Second, interfaces that don't allow multi-line code (think spreadsheets) generally have issues with duplication for re-use.
    >   While this example only had one port, consider if we had several outputs with the same electrical characteristics.
    >   In code, we could define one port model and instantiate it multiple times, while the GUI may require repeating the definition several times.

> <details>
>   <summary>At this point, your code and diagram might look like...</summary>
>
>   ```python
>   class Lf21215tmr_Device(FootprintBlock):
>     def __init__(self) -> None:
>       super().__init__()
>       self.vcc = self.Port(
>         VoltageSink(voltage_limits=(1.8, 5.5)*Volt, current_draw=(0, 1.5)*uAmp))
>       self.gnd = self.Port(Ground())
>   
>       self.vout = self.Port(DigitalSource.from_supply(
>         self.gnd, self.vcc,
>         output_threshold_offset=(0.2, -0.3)
>       ))
> 
>     def contents(self) -> None:
>       super().contents()
>   ```
>
>   ![Block diagram view](vis_magsense_device.png)
> </details>


## Defining the footprint
`FootprintBlock` defines its footprint and pin mapping (from port to footprint pin) via a `self.footprint(...)` call.
This can also be inserted from the GUI.

Select (but without necessarily focusing into) the newly created block in the block diagram view.
Then, position the caret at where you want to insert the code - we recommend in the `contents` method.
In the KiCad panel, search for a **SOT-23** footprint, and double-click to insert code.
This code should appear:

```python
self.footprint(
  'U', 'Package_TO_SOT_SMD:SOT-23',
  { },
  mfr='', part='',
  datasheet=''
)
```

> If your caret is already inside a `self.footprint` call, it will instead modify the existing call to use the selected footprint.

To assign pins, double-click on the pad on the footprint while the caret is within the `self.footprint` call to be edited.
Then, select from the list of connectable pins.

Assign these pins:
- Pin 1: `vcc`
- Pin 2: `vout`
- Pin 3: `gnd`

You can also fill in the other fields in the code (which would be propagated to BoMs and layout):
- Manufacturer: `Littelfuse`
- Part: `LF21215TMR`
- Datasheet: `https://www.littelfuse.com/~/media/electronics/datasheets/magnetic_sensors_and_reed_switches/littelfuse_tmr_switch_lf21215tmr_datasheet.pdf.pdf`

> <details>
>   <summary>At this point, your code and footprint might look like...</summary>
>
>   ```python
>   class Lf21215tmr_Device(FootprintBlock):
>     def __init__(self) -> None:
>       super().__init__()
>       self.vcc = self.Port(
>         VoltageSink(voltage_limits=(1.8, 5.5)*Volt, current_draw=(0, 1.5)*uAmp))
>       self.gnd = self.Port(Ground())
>   
>       self.vout = self.Port(DigitalSource.from_supply(
>         self.gnd, self.vcc,
>         output_threshold_offset=(0.2, -0.3)
>       ))
> 
>     def contents(self) -> None:
>       super().contents()
>       self.footprint(
>         'U', 'Package_TO_SOT_SMD:SOT-23',
>         {
>           '1': self.vcc,
>           '2': self.vout,
>           '3': self.gnd,
>         },
>         mfr='Littelfuse', part='LF21215TMR',
>         datasheet='https://www.littelfuse.com/~/media/electronics/datasheets/magnetic_sensors_and_reed_switches/littelfuse_tmr_switch_lf21215tmr_datasheet.pdf.pdf'
>       )
>   ```
>
>   ![Footprint view](footprint_magsense.png)
> </details>


## Creating the application circuit
In most cases, individual components are not used alone but are instead part of an application circuit,
As in the typical application circuit of the LF21215TMR datasheet, it requires a 0.1uF decoupling capacitor.
We will build the application circuit as a block around the device defined above, then use this in the top-level design.

Start by creating a new block, `Lf21215tmr`.
Since this won't be a footprint, it should extend `Block` directly, and you can insert such code by right clicking on All Blocks in the library browser.

> In contrast to definition we just wrote, this drops the `_Device` postfix we used to indicate a footprint block.

Again, if you want to work with this in the graphical editor, you can recompile once you've added the block code, then instantiate it from the library browser.
If you had the `Lf21215tmr_Device` block in your top-level design, you can delete that.
Then, double-click into the newly created `Lf21215tmr` block to select it for editing.

<!-- TODO GUI Export support -->

<!-- TODO Create Wrapper Block? -->

As indicated by the application circuit, this block would have the same ports as the device (two **VoltageSink** and one **DigitalSource**). It would have two parts, the `Lf21215tmr_Device` we just defined, and a `DecouplingCapacitor`.
Instantiate them both, and connect them together.

For the ports, because these are intermediate ports, they do not need parameters (they are derived from the connected devices), so you can delete all of them.
You can also add the implicit connection `Power` and `Common` tags
```python
self.pwr = self.Port(VoltageSink(), [Power])
self.gnd = self.Port(VoltageSink(), [Common])
self.out = self.Port(DigitalSource())
```

For the DecouplingCapacitor, you'll need to specify it as 0.1uF.
By default, we use a loose 20% tolerance for capacitors:
```python
self.cap = self.Block(DecouplingCapacitor(capacitance=0.1*uFarad(tol=0.2)))
```

> <details>
>   <summary>At this point, your code and diagram might look like...</summary>
>
>   ```python
>   class Lf21215tmr(Block):
>     def __init__(self) -> None:
>       super().__init__()
>       self.ic = self.Block(Lf21215tmr_Device())
>       
>       self.pwr = self.Port(VoltageSink(), [Power])
>       self.gnd = self.Port(VoltageSink(), [Common])
>       self.out = self.Port(DigitalSource())
> 
>       self.cap = self.Block(DecouplingCapacitor(capacitance=0.1*uFarad(tol=0.2)))
> 
>       self.connect(self.ic.vcc, self.cap.pwr, self.pwr)
>       self.connect(self.ic.gnd, self.cap.gnd, self.gnd)
>       self.connect(self.ic.vout, self.out)
>   
>     def contents(self) -> None:
>       super().contents()
>   ```
>
>   ![Block diagram view](vis_magsense_app.png)
> </details>


## Export
Instead of creating ports, we can also use the `self.Export(...)` function to export an inner port directly.
The main benefit is you don't need to specify repeated type information for the port, which will be inferred from the inner port.

With this style, `__init__` can be rewritten as follows:
```python
self.ic = self.Block(Lf21215tmr_Device())
self.pwr = self.Export(self.ic.vcc, [Power])
self.gnd = self.Export(self.ic.gnd, [Common])
self.out = self.Export(self.ic.vout)

self.cap = self.Block(DecouplingCapacitor(capacitance=0.1*uFarad(tol=0.2)))
self.connect(self.cap.pwr, self.pwr)
self.connect(self.cap.gnd, self.gnd)
```

> <details>
>   <summary>At this point, your code might look like...</summary>
>
>   ```python
>   class Lf21215tmr(Block):
>     def __init__(self) -> None:
>       super().__init__()
>       self.ic = self.Block(Lf21215tmr_Device())
>       self.pwr = self.Export(self.ic.vcc, [Power])
>       self.gnd = self.Export(self.ic.gnd, [Common])
>       self.out = self.Export(self.ic.vout)
>   
>       self.cap = self.Block(DecouplingCapacitor(capacitance=0.1*uFarad(tol=0.2)))
>       self.connect(self.cap.pwr, self.pwr)
>       self.connect(self.cap.gnd, self.gnd)
>   
>     def contents(self) -> None:
>       super().contents()
>   ```
>
> The block diagram should not have changed - this is a non-functional, stylistic change.
> </details>


## Finishing Touches
Connect the magnetic sensor at the top level (if you haven't done so already).
You can put it in the implicit block to avoid the explicit power and ground `connect` statements.
The sensor output can be connected to any digital line of the microcontroller, such as `digital[4]`.

> <details>
>   <summary>At this point, your code and diagram might look like...</summary>
>
>   ```python
>   class BlinkyExample(SimpleBoardTop):
>     def contents(self) -> None:
>       super().contents()
>   
>       self.jack = self.Block(Pj_102a(voltage_out=6*Volt(tol=0.10)))
>   
>       self.buck = self.Block(BuckConverter(output_voltage=3.3*Volt(tol=0.05)))
>       self.connect(self.jack.pwr, self.buck.pwr_in)
>       self.connect(self.jack.gnd, self.buck.gnd)
>   
>       with self.implicit_connect(
>               ImplicitConnect(self.buck.pwr_out, [Power]),
>               ImplicitConnect(self.jack.gnd, [Common]),
>       ) as imp:
>         self.mcu = imp.Block(Lpc1549_48())
>         self.swd = imp.Block(SwdCortexTargetHeader())
>         self.connect(self.swd.swd, self.mcu.swd)
>   
>         self.led = ElementDict()
>         for i in range(4):
>           self.led[i] = imp.Block(IndicatorLed())
>           self.connect(self.mcu.digital[i], self.led[i].signal)
>   
>         self.mag = imp.Block(Lf21215tmr())
>         self.connect(self.mcu.digital[4], self.mag.out)
>   
>     def refinements(self) -> Refinements:
>       return super().refinements() + Refinements(
>         instance_refinements=[
>           (['buck'], Tps561201),
>         ])
>   ```
>
>   ![Block diagram view](vis_blinky_magsense.png)
> </details>
