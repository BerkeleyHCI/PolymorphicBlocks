# Getting Started Tutorial

## Core concepts
The core abstraction is the hierarchical block diagram, which we will explain using an example design of a microcontroller driving an LED.

In conventional schematic tools, such a design could be a flat schematic, consisting of the microcontroller module, LED, and resistor:  
![Blinky Hierarchy Block Diagram](docs/blinky_model_flat.png)

Many modern tools have the concept of hierarchy blocks, where a block could be a subcircuit:  
![Blinky Hierarchy Block Diagram](docs/blinky_model_hierarchy1.png)

In the example above, the LED-resistor subcircuit is contained within a block, which can be manipulated as a unit, and exposes ports (circles on the diagram) while encapsulating internal pins.
(note: in mainstream schematic tools with this feature, the subcircuit is usually presented in its own sheet, instead of having its contents displayed in the block)

Generalizing this model, components are blocks too, and component pins are also block ports:  
![Blinky Hierarchy Block Diagram](docs/blinky_model_hierarchy2.png)

The main concepts our model extends on top of the simple hierarchy blocks above are **parameters**, **links**, and **generators**.

**Parameters** are variables that can be attached to blocks and ports.
For example, a digital IO, like `digital[0]` in the example above, would have parameters like input voltage tolerance, output voltage range, and logic thresholds.
This allows for a more powerful design correctness check (think ERC++), and provides a foundation for generators.

**Generators** allow a block's internal contents to be constructed by code, possibly based on parameters on it and its ports.
For example, the `IndicatorLed` block automatically sizes the resistor based on the input voltage on the `sig` pin, and the DC-DC converter block automatically sizes inductors and capacitors based on the target output voltage and current.

Finally, in the internal model (mainly relevant for compiler writers and library builders), the connections between ports expand into **links** which defines how parameters propagate between those ports and any constraints on them.
Continuing the digital IO example, the link would check the output thresholds against the input thresholds, and provide the worst-case voltage levels given all connected drivers.
These could be viewed as a block-like object (diamonds on the diagram) instead of direct wire connections:  
![Blinky Hierarchy Block Diagram](docs/blinky_model_full.png)

> In the user-facing HDL design model, links are inferred based on the types of connected ports and not explicit.
> Being aware of links can be useful for debugging, but this is mainly relevant for compiler writers and library builders.

We'll put these concepts into practice in the rest of this tutorial by building a variation of the blinky example above, then defining a custom part.


### Setup
Instructions for setting up the IDE and compiler are in the [setup document](setup.md).


### Reference Document
While this getting started guide is meant to be self-contained, you may also find the [reference document](reference.md) helpful, especially as you build designs outside this tutorial.
The reference document includes a short overview of all the core primitives and common library elements.


### Hardware Description Language (HDL)
To support user-defined computation of parameters and generator blocks, the design system is implemented as a _hardware description language_ (HDL).
That is, blocks are "placed" or instantiated, and their ports are connected, through lines in code instead of GUI actions in a graphical schematic.

There are a couple of basic operations, which you'll get to try in the tutorial:
- **Block Definition**: blocks are defined as Python classes which extend (subclass, including indirectly) `Block`.
- **Block Instantiation**: creates a sub-block in the current block
  - For example, `self.led = self.Block(IndicatorLed())` instantiates an `IndicatorLed` block and names it `led` in the current block
- **Port Instantiation**: creates an exterior port in the current block, used for building library blocks.
  - For example, `self.vdd = self.Port(VoltageSink(voltage_limits=(2.3, 5.5)*Volt, current_draw=(0, 15)*uAmp))` instantiates a port of type `VoltageSink` (voltage input) with defined voltage limits and current draw ranges, and names it `vdd`.
  - Ports are not allowed on top-level blocks.
- **Connect**: connects two (or more) ports.
  - For example, `self.connect(self.mcu.gnd, self.led.gnd)` connects the `gnd` ports on `mcu` and `led`


### Graphical Editor and Integrated Development Environment (IDE)
While an HDL is needed to support parameter computation and programmatic construction, some operations (like building a top-level design with an LED connected to a microcontroller) may not require the full power provided by an HDL and may be more intuitive or familiar within a graphical environment.
However, because this design makes use of generator blocks (the LED), and because blocks may also take parameters (such as the target output voltage of a DC-DC converter), the HDL is still the primary design input.

To help with these more basic operations and to support those more familiar with a graphical schematic capture flow, an IDE helps bridge the graphical schematic-like and HDL code representations. Specifically, it:
- provides a block diagram visualization of the design
- allows inspection of solved / computed parameters in the design
- generates and inserts HDL code from schematic editor-like actions

![Annotated IDE screen](docs/ide/overview.png)

The IDE has these major components:
- **Block Diagram Visualization**: shows the compiled design visualized as a block diagram here.
  - **Design Tree**: shows the compiled design as a tree structure of the block hierarchy.
- **Library Browser**: shows all the library blocks, ports, and links.
  The text box at the top allows filtering by keyword.
  - The preview box on the right shows more information on the selected library block, including docstring (if available), instantiation parameters, and block diagram preview.
- **Compiler / Run Console**: shows the compilation log, including any errors and prints from Python as HDL runs.

The rest of this tutorial will focus on the HDL, but will also describe how the equivalent code could be generated by GUI actions.
**As you go through the tutorial, you can write the code shown in the code blocks or follow the graphical actions described immediately afterward.**
However, you can't do both (since they would duplicate the same results), but you can try the graphical actions if you remove the code.


## A top-level design: Blinky
_In this example, we will create a circuit consisting of a LED and switch connected to a microcontroller._

Start by creating a `blinky.py`, and filling it with this skeleton code:

```python
from edg import *


class BlinkyExample(SimpleBoardTop):
  def contents(self) -> None:
    super().contents()
    # your implementation here


if __name__ == "__main__":
  compile_board_inplace(BlinkyExample)
```

> If using the IDE, `blinky.py` must be within the project directory.
> Make sure you've set up the project according to the [setup document](setup.md).
> 
> If using the command line, `blinky.py` can be created anywhere.

- `from edg import *` brings in the base classes for circuit construction, like `SimpleBoardTop`.
- `class BlinkyExample` contains the (top-level) circuit you're going to build, and it extends the top-level hierarchical block base class `SimpleBoardTop`.
  It's empty for now, but we'll fill it in the next section.
  - `SimpleBoardTop` has definitions which make this tutorial easier but which may not be desirable in a production environment, in which case you should use `BoardTop`.
    Currently, this is just ignoring the frequency specification for inductor, since that data isn't available in the parts table.
- `compile_board_inplace(...)` invokes the circuit generator given the top-level design (`BlinkyExample`).
  This is the starting point that allows the file to run as a Python script, and you can treat it as magic.

Try building the example now.

**If using the IDE**: look for the run icon ![run icon](docs/ide/ide_run_button.png) in the gutter (with the line numbers) next to `class BlinkyExample`:
![run in IDE](docs/ide/ide_gutter_run.png)  
1. Click it.
   _Make sure that you're using the run icon associated with `class BlinkyExample`, not the file, and not `if __name__ == "__main__"`._
2. Then from the menu, click the Run option.  
   ![run menu](docs/ide/ide_run_blinky_menu.png)
   > **Tip**: Next time, you can rebuild the design by re-running the last selected run configuration with hotkey **Shift+F10** (Windows) or **Ctrl+R** (MacOS).

   > **Note on re-compiling behavior**: The IDE only re-compiles block classes when its source (or the source of superclasses) has changed, but this does not catch all functional changes.
   > If changes aren't recompiling, try making a change to the class code.
   > Alternatively, you can clear all compiled blocks through main menu > Tools > Empty Block Cache.
   > 
   > In particular, these changes may not trigger a recompile:
   > - Any changes outside the class, even if the code is called by the class.
   > - Changes to supporting files (such as part tables and imported schematics), even if they are referenced in the class.
   > - Changes to `__init__` do not re-compile instantiating classes, even if default values have been updated.
3. The design should build, and you should get a run log that looks something like:
   ```
   Starting compilation of blinky.BlinkyExample
   Using interpreter from configured SDK [...]
   [... lots of compilation output here ...]
   Completed: generate netlist: wrote [...]
   ```
4. Some options (like where the netlist is generated into) can be modified via the run options at the top right:  
   ![run menu](docs/ide/ide_run_config.png)
<details> <summary>If not using the IDE</summary>
  
Run `python blinky.py` from the command line.
If all worked, this should create a folder `BlinkyExample` with a netlist `BlinkyExample.net` inside.
</details>

<details> <summary>Resolving common errors</summary>
  
- If you get an error along the lines of `ModuleNotFoundError: No module named 'deprecated'` or `ModuleNotFoundError: No module named 'google'`, this is because the Python dependencies haven't been installed.
See the [setup document](setup.md) for instructions on installing dependencies.
</details>


### Creating the microcontroller and LED
For this simple example, we connect an LED to a STM32F103 microcontroller, and have everything powered by a USB type-C receptacle.

Let's start by instantiating the USB type-C receptacle through graphical operations in the IDE.
1. In the Library Browser, search for the block (here, `UsbCReceptable`) using the Filter textbox:  
   ![Library filtering by USB](docs/ide/ide_library_usbc.png)
2. Double-click the library entry.
   This will insert the code to instantiate the block as a _live template_, code with template fields you can fill in:  
   ![Live template example](docs/ide/ide_livetemplate_usbc.png)  
   **Editing outside the currently active template field (boxed in blue) will break off and cancel the template.**
   **Moving the cursor outside the currently active template field, either using the mouse or keyboard arrows, is discouraged.**
3. Name the block `usb`, by typing it into the first template field.  
   ![Live template example](docs/ide/ide_livetemplate_usbc_named.png)
4. Then press [Tab] through the end of the template (leaving the other fields empty, they're optional).
5. Once you commit the live template, the block will appear in the block diagram visualizer.
    - The hatched pattern (diagonal lines) in the block diagram visualizer indicates that the block may be out-of-sync with the code until the next re-compile.

> While the template is active, you can:
> - Press [Enter] or [Tab] to move to the next template field.
>   Validation may prevent moving to the next field, for example if the name field is invalid.
> - Tabbing past the last field will commit the template.
> - Press [Shift+Tab] to move back to the previous template field.
> - Use [Alt+Click] to move the template to another place in the code.
>   If the selected place isn't valid, the template will snap to a valid location.
> - Press [Esc] to cancel the template, ending the editing but leaving the code in place.
>   Canceling a blank template deletes the inserted code.

> `self.Block(...)` creates a sub-block in `self` (the current hierarchy block being defined).
> It must be assigned to an instance variable (in this case, `mcu`), which is used as the name sub-block.

> The library icons have these meanings:
> - ![Folder](docs/intellij_icons/AllIcons.Nodes.Folder.svg) (category): this "block" is actually a category organizer and should not be instantiated.
> - ![Abstract Type](docs/intellij_icons/AllIcons.Hierarchy.Subtypes.dark.svg) (abstract type): this block is an abstract type.
>   Abstract blocks will be discussed more later.
> - Most will not have an icon, which means that they're none of the above. These blocks can be instantiated.

**Repeat for the microcontroller** (`Stm32f103_48`, named `mcu`) **and LED** (`IndicatorLed`, named `led`).

If all was done correctly, your changes to the skeleton code might look like:
```diff
  super().contents()
- # your implementation here
+ self.usb = self.Block(UsbCReceptacle())
+ self.mcu = self.Block(Stm32f103_48())
+ self.led = self.Block(IndicatorLed())
```

If you're using the IDE, once you recompile the block diagram should look like:  
![Blink diagram with blocks only](docs/ide/ide_blinky_blocks.png)  
With something on your screen now, you can zoom in and out of the visualization using the mousewheel, or pan by clicking and dragging.

As the design is incomplete, **it is expected that there will be errors**.
The red ports indicate ports that need to be connected, but aren't.
We'll fix that next.

### Connecting blocks
Blocks alone aren't very interesting, and they must be connected to be useful.
First, we need to connect the power and ground between the devices, which we can also do with graphical operations in the IDE:
1. Double click any of the ground ports (say, `usb.gnd`).
   This starts a connection operation, which dims out the ports that cannot be connected:  
   ![Connection beginning](docs/ide/ide_connect_usbc_start.png)
2. Select (single click) on all the other ground ports to be connected (here, `mcu.gnd` and `led.gnd`):  
   ![Connection with ports](docs/ide/ide_connect_usbc_all.png)
    - The order in which you select additional ports determines the order of the ports in the generated code.
3. Double-click anywhere (within a block) to insert the connections as a live template.
   ![Connection live template](docs/ide/ide_livetemplate_gnd_connect.png)
   > - You can double-click on a port to simultaneously select that port and insert the connection.
   > - You can cancel a connect operation by pressing [Esc] while the block diagram visualizer is selected.
4. The name template field is optional, leave it blank and [Tab] past it.
    - Like the block instantiation, you can move the live template with [Alt+Click].
5. Once you commit the live template, the connection will appear in the block diagram visualizer.

> `self.connect(...)` connects all the argument ports together.
> Connections are strongly typed based on the port types: the system will try to infer a _link_ based on the argument port types and count.

**Repeat for the power line** (connect `usb.pwr` to `mcu.pwr`).

If all was done correctly, your changes to the skeleton code might look like:
```diff
  self.usb = self.Block(UsbCReceptacle())
  self.mcu = self.Block(Stm32f103_48())
  self.led = self.Block(IndicatorLed())
+ self.connect(self.usb.pwr, self.mcu.pwr)
+ self.connect(self.usb.gnd, self.mcu.gnd, self.led.gnd)
```

> `self.connect(...)` connects all the argument ports together. 
> Connections are strongly typed based on the port types: the system will try to infer a _link_ based on the argument port types and count.

If you're using the IDE, once you recompile the block diagram should look like:  
![Block diagrams with power connections](docs/ide/ide_blinky_connectpower.png)

Then, we need to connect the LED to a GPIO on the microcontroller, so **repeat the connect process** (connect `mcu.gpio` to `led.signal`).

If all was done correctly, your changes to the skeleton code might look like:
```diff
  self.connect(self.usb.pwr, self.mcu.pwr)
  self.connect(self.usb.gnd, self.mcu.gnd, self.led.gnd)
+ self.connect(self.mcu.gpio.request(), self.led.signal)
```

Give the GPIO pin an (optional) name `led` by modifying the generated code:
```diff
- self.connect(self.mcu.gpio.request(), self.led.signal)
+ self.connect(self.mcu.gpio.request('led'), self.led.signal)
```

> Microcontroller GPIOs (and other IOs like SPI and UART) are ![port array symbol](docs/ide/ide_portarray.png) _port arrays_, which are dynamically sized.
> Here, we ![port array symbol](docs/ide/ide_portarray_slice_min.png) `request(...)` a new GPIO from the GPIO port array, then connect it to the LED.
> `request(...)` takes an optional name parameter, the meaning of which depends on the block.
>
> By default, these connections are arbitrarily assigned to microcontroller pins.
> However pin assignments can also be manually specified (using this name parameter) to simplify board layout - this will be covered at the end of this tutorial.
> 
> Port arrays can be connected as a unit, which also propagates the length, though this isn't yet supported with graphical operations.
> 
> Port arrays behave differently when viewed externally (as we're doing here) and internally (for library builders).
> Internal usage of port arrays will be covered later in the library building section.

Recompiling in the IDE yields this block diagram:  
![Fully connected block diagram](docs/ide/ide_blinky_connect.png)

> <details>
>   <summary>At this point, your HDL might look like...</summary>
>
>   ```python
>   class BlinkyExample(SimpleBoardTop):
>     def contents(self) -> None:
>       super().contents()
>       self.usb = self.Block(UsbCReceptacle())
>       self.mcu = self.Block(Stm32f103_48())
>       self.led = self.Block(IndicatorLed())
>       self.connect(self.usb.gnd, self.mcu.gnd, self.led.gnd)
>       self.connect(self.usb.pwr, self.mcu.pwr)
>       self.connect(self.mcu.gpio.request('led'), self.led.signal)
>   ```
> </details>


## Fixing Blinky
_In this section, we will explore and fix the remaining compiler errors to get to a clean design._

While the design is now structurally complete, we still have errors in the form of failed assertions.
Assertions are checks on the electronics model, in this case it's detecting a voltage incompatibility between the USB's 5v out and the STM32's 3.3v tolerant power inputs.

If you're in the IDE, errors will show up in the compilation log and in the errors tab:  
![Errors tab with errors](docs/ide/ide_blinky_errors.png)  
You can also inspect the details of the power connection by mousing over it:  
![Inspection of the power lines with voltages and limits](docs/ide/ide_blinky_inspect.png)

### Adding a Voltage Regulator
To run the STM32 within its rated voltage limits, we'll need a voltage regulator to lower the 5v from USB to the common 3.3v power expected by modern devices.

**Repeat the add block flow** with a `VoltageRegulator` block and name it `reg`.
Unlike the prior blocks, we actually need to specify a target output voltage here: use `3.3*Volt(tol=0.05)` for 3.3V ± 5%.
If using live templates, you can write it into the `output_voltage` template field.
**Place this between the USB connector and the microcontroller** (you can use Alt+click to move the template position, while it's active).  
![Regulator live template](docs/ide/ide_livetemplate_reg.png)

> The `VoltageRegulator` block is parameterized - configured by additional data specified as constructor arguments.
>
> Many blocks in the library are parameterized, allowing them to be used in a wide range of situations.
> See each block's definition or documentation for what those parameters mean.

**Repeat the connect flow** to connect `reg.gnd` to the existing ground net.
If using graphical operations, you can start by double-clicking on any port you want to connect.
**Try merging the new connect into the prior ground connect statement by re-positioning (Alt+click) the template into the prior ground connect**.  
![Connection live template](docs/ide/ide_livetemplate_gnd_append.png)

You'll also need to splice the regulator into the power connection between the USB and the microcontroller.
Since graphical operations don't support connection delete, you'll have to **delete the power connection in the code, then recompile**:
```diff
  self.usb = self.Block(UsbCReceptacle())
  self.reg = self.Block(VoltageRegulator(3.3*Volt(tol=0.05)))
  self.mcu = self.Block(Stm32f103_48())
  self.led = self.Block(IndicatorLed())
  self.connect(self.usb.gnd, self.mcu.gnd, self.led.gnd)
- self.connect(self.usb.pwr, self.mcu.pwr)
  self.connect(self.mcu.gpio.request('led'), self.led.signal)
```

From here, you can **repeat the connect flow** to connect the regulator input and output.

When all is done, your changes to the skeleton code might look like:
```diff
  self.usb = self.Block(UsbCReceptacle())
+ self.reg = self.Block(VoltageRegulator(3.3*Volt(tol=0.05)))
  self.mcu = self.Block(Stm32f103_48())
  self.led = self.Block(IndicatorLed())
- self.connect(self.usb.gnd, self.mcu.gnd, self.led.gnd)
- self.connect(self.usb.pwr, self.mcu.pwr)
+ self.connect(self.usb.gnd, self.mcu.gnd, self.led.gnd, self.reg.gnd)
+ self.connect(self.usb.pwr, self.reg.pwr_in)
+ self.connect(self.reg.pwr_out, self.mcu.pwr)
  self.connect(self.mcu.gpio.request('led'), self.led.signal)
```

If you try recompiling it, it will give you an error because `VoltageRegulator` is an _abstract block_ (it does not have an implementation) and was automatically substituted with an ideal model (which does not have a circuit implementation, but allows compilation to continue).
Abstract blocks are useful for two reasons:
1. It allows your design to be more general and allows you to defer implementation choices until later.
   This is more relevant for library builders, where you may want to give the system designer the choice of, for example, whether to use a surface-mount or through-hole resistor.
2. It can help preserve design intent more precisely and keep HDL readable.
   For example, saying that we want a voltage regulator can be more intuitive than directly instantiating a TPS561201 block.

Unlike in software, we can instantiate abstract blocks here, but they won't actually place down a useful circuit.
We can _refine_ those abstract blocks to give them a _concrete_ subclass by **adding a refinements block in the top-level design class**.
```diff
  class BlinkyExample(SimpleBoardTop):
    def contents(self) -> None:
      ...

+   def refinements(self) -> Refinements:
+     return super().refinements() + Refinements(
+     instance_refinements=[
+       (['reg'], Tps561201),
+     ])
```

> `BoardTop` defines default refinements for some common types, such has choosing surface-mount components for `Resistor` and `Capacitor`.
> You can override these with a refinement in your HDL, for example choosing `AxialResistor`.

> If using the IDE, refinements can be done through the library browser.
> 1. Select (single click) on the block you want to refine.
> 2. In the Library Browser, search for the class you want to refine into.
>    If you don't know, you can filter by the abstract type and see what options are under it.
> 3. Right-click the subclass in the Library Browser, and click "Refine instance...".
>    - Refine instance only affects the single selected block.
>    - Refine class affects all classes of the selected block.
>      This may be useful, for example, if you wanted to do a design-wide replacement of all generic resistors with a specific type.
> 4. The corresponding refinement block should be inserted, or if it already exists, a new refinement entry will be added.

Recompiling in the IDE yields this block diagram and no errors:  
![Blinky with buck converter block diagram](docs/ide/ide_blinky_buck.png)

> <details>
>   <summary>At this point, your HDL might look like...</summary>
>
>   ```python
>   class BlinkyExample(SimpleBoardTop):
>     def contents(self) -> None:
>       super().contents()
>       self.usb = self.Block(UsbCReceptacle())
>       self.reg = self.Block(VoltageRegulator(3.3*Volt(tol=0.05)))
>       self.mcu = self.Block(Stm32f103_48())
>       self.led = self.Block(IndicatorLed())
>       self.connect(self.usb.gnd, self.reg.gnd, self.mcu.gnd, self.led.gnd)
>       self.connect(self.usb.pwr, self.reg.pwr_in)
>       self.connect(self.reg.pwr_out, self.mcu.pwr)
>       self.connect(self.mcu.gpio.request('led'), self.led.signal)
>
>     def refinements(self) -> Refinements:
>       return super().refinements() + Refinements(
>       instance_refinements=[
>         (['reg'], Tps561201),
>       ])
>   ```
> </details>

### Deeper Inspection
Here, we were able to place down a buck converter - a non-trivial subcircuit - with just one line of code.
A major benefit of this HDL-based design flow is the design automation that is encapsulated in the libraries.
The library writer has done the hard work of figuring out how to size the capacitors and inductors, and wrapped it into this neat `VoltageRegulator` block.

You may want to inspect the results.
In the IDE, you can hover over the output line and see that it is at 3.3v ±4.47%.
Why?
You can dig into the converter subcircuit by double-clicking on it:  
![TPS561201 subcircuit](docs/ide/ide_buck_internal.png)

The implementation uses a feedback voltage divider, and if you mouseover this it will show the generated ratio of 0.23.
The converter's output voltage reflects the actual expected output voltage, accounting for resistor tolerance and the chip's feedback reference tolerance.  
![Buck converter input capacitor](docs/ide/ide_buck_fb.png)

Similarly, mousing over the other components like the resistors and capacitors shows their details.

To zoom out, double-click on the topmost block.

## KiCad Import
If you have KiCad installed, you can import this full design into the layout editor. _KiCad 6.0+ is required, the netlist format is not compatible with 5.x or lower!_

In the KiCad PCB Editor (layout tool), go to File > Import > Netlist..., and open the netlist file generated.
KiCad will produce an initial placement that roughly clusters components according to their hierarchical grouping:
![Blinky layout with default placement](docs/blinky_kicad.png)

The block hierarchy will appear to KiCad as a sheet hierarchy.
You can, for example, right click one of the footprints > Select > Items in Same Hierarchical Sheet, and it will select all footprints in that sub-block.
<!-- TODO: now broken because of required schematic check =(: Some external hierarchical plugins like [Replicate Layout](https://github.com/MitjaNemec/ReplicateLayout) also work. -->

As you continue to write HDL, tstamps (an unique per-footprint ID used by KiCad to match netlist components to layout footprints) are stable and allows you to update a partial layout with a new netlist.
**tstamps are generated from Block names, so if HDL names change those footprints will not update.**

When you're ready for production, you can toggle traditional refdes generation (R1, R2, instead of current hierarchical path).
While refdes generation is deterministic (the same design will produce the same refdes assignments), small changes to the design can significantly change refdes assignments.


## Expanding Blinky
**_This section goes over some additional quality-of-life features that can make the HDL more elegant and powerful, but does not introduce any significantly new constructs._**

_In this section, we will add a tactile switch and three more LEDs._

### Adding a Switch
A tactile switch with a digital output can be instantiated as `DigitalSwitch()` which has an `out` port.
Using what you've learned above, instantiate a switch and connect it to the microcontroller.

### Arraying LEDs
While you certainly can copy-paste the above LED instantiation 4 times, that's no fun given that we're in a programming language with `for` loops.

**Replace your single LED instantiation and connections with**:
```diff
  ...
- self.led = self.Block(IndicatorLed())
- self.connect(self.usb.gnd, self.reg.gnd, self.mcu.gnd, self.led.gnd)
+ self.connect(self.usb.gnd, self.reg.gnd, self.mcu.gnd)
  ...
- self.connect(self.mcu.gpio.request('led'), self.led.signal)
  ...
+ self.led = ElementDict[IndicatorLed]()
+ for i in range(4):
+   self.led[i] = self.Block(IndicatorLed())
+   self.connect(self.mcu.gpio.request(f'led{i}'), self.led[i].signal)
+   self.connect(self.usb.gnd, self.led[i].gnd)
```

> ElementDict creates a naming space that is an extension of the parent and is needed to give a unique, arrayed name for the LED being created.
> The square brackets provide the type parameter for the value type, which is necessary when using static analysis tools like mypy.

> The IDE cannot produce code that programmatically generates hardware.
> In general, code offers you a lot more power than can be achieved through the GUI.
> 
> However, the visualizer will run fine.

Recompiling in the IDE yields this block diagram:  
![Blinky with switch and LED array block diagram](docs/ide/ide_ledarray.png)

> <details>
>   <summary>At this point, your HDL might look like...</summary>
>
>   ```python
>   class BlinkyExample(SimpleBoardTop):
>     def contents(self) -> None:
>       super().contents()
>       self.usb = self.Block(UsbCReceptacle())
>       self.reg = self.Block(VoltageRegulator(3.3*Volt(tol=0.05)))
>       self.mcu = self.Block(Stm32f103_48())
>       self.connect(self.usb.gnd, self.reg.gnd, self.mcu.gnd)
>       self.connect(self.usb.pwr, self.reg.pwr_in)
>       self.connect(self.reg.pwr_out, self.mcu.pwr)
> 
>       self.sw = self.Block(DigitalSwitch())
>       self.connect(self.mcu.gpio.request('sw'), self.sw.out)
>       self.connect(self.usb.gnd, self.sw.gnd)
>
>       self.led = ElementDict[IndicatorLed]()
>       for i in range(4):
>         self.led[i] = self.Block(IndicatorLed())
>         self.connect(self.mcu.gpio.request(f'led{i}'), self.led[i].signal)
>         self.connect(self.usb.gnd, self.led[i].gnd)
>
>     def refinements(self) -> Refinements:
>       return super().refinements() + Refinements(
>       instance_refinements=[
>         (['reg'], Tps561201),
>       ])
>   ```
> </details>


## Syntactic sugar
_Syntactic sugar refers to syntax within programming languages that makes things more usable._
_In this section, we clean up the prior example by consolidating some repetitive connections through implicit scopes._

> Similar to arraying LEDs, the IDE does not have any special support for generating these operations.
> However, the visualizer will continue to run fine.

### Implicit Connections
Because some connections (like power and ground) are very common, the HDL provides the idea of an implicit connection scope to automatically make them when a block is instantiated.
The implicit scope defines the connections to make and the conditions for which ports to connect (through tags):

```python
with self.implicit_connect(
    ImplicitConnect(self.reg.pwr_out, [Power]),
    ImplicitConnect(self.reg.gnd, [Common]),
) as imp:
  # any blocks here instantiated with imp.Block(...) instead of self.Block(...)
  # will have Power-tagged ports connected to self.reg.pwr_out
  # and Common-tagged ports connected to self.reg.gnd
```

> When blocks define ports, they can associate tags with them to specify implicit connectivity.
> To prevent errors, all ports with tags are required to be connected, either implicitly (as in this section) or explicitly (through `connect` statements).
>
> The most common tags are `Power` (for a general positive voltage rail) and `Common` (for ground).

In our example, we can get rid of the explicit power and ground connections.
Start by **adding an implicit scope** to tie Power-tagged ports to `self.reg.pwr_out` and Common- (ground) tagged ports to `self.reg.gnd`, and **move the microcontroller, switch, and LED into the implicit scope**

```diff
  ...
  self.reg = self.Block(VoltageRegulator(3.3*Volt(tol=0.05)))
  
+ with self.implicit_connect(
+     ImplicitConnect(self.reg.pwr_out, [Power]),
+     ImplicitConnect(self.reg.gnd, [Common]),
+ ) as imp:
    self.mcu = self.Block(IoController())
    self.connect(self.usb.gnd, self.reg.gnd, self.mcu.gnd)
    self.connect(self.usb.pwr, self.reg.pwr_in)
    self.connect(self.reg.pwr_out, self.mcu.pwr)
    
    self.sw = self.Block(DigitalSwitch())
    self.connect(self.mcu.gpio.request('sw'), self.sw.out)
    self.connect(self.usb.gnd, self.sw.gnd)
    
    self.led = ElementDict[IndicatorLed]()
    for i in range(4):
      self.led[i] = self.Block(IndicatorLed())
      self.connect(self.mcu.gpio.request(f'led{i}'), self.led[i].signal)
      self.connect(self.usb.gnd, self.led[i].gnd)
```

Inside an implicit connection block, only blocks instantiated with `imp.Block(...)` have implicit connections made.
**Replace the microcontroller, switch, and LED `self.Block(...)` instantiations with `imp.Block(...)` instantiations**, then **delete the redundant power and ground connections** (remember that the USB to regulator ground would need to be separated out):

```diff
  ...
  self.reg = self.Block(VoltageRegulator(3.3*Volt(tol=0.05)))
+ self.connect(self.usb.gnd, self.reg.gnd)
+ self.connect(self.usb.pwr, self.reg.pwr_in)
  with self.implicit_connect(
      ImplicitConnect(self.reg.pwr_out, [Power]),
      ImplicitConnect(self.reg.gnd, [Common]),
  ) as imp:
-   self.mcu = self.Block(IoController())
+   self.mcu = imp.Block(IoController())
-   self.connect(self.usb.gnd, self.reg.gnd, self.mcu.gnd)
-   self.connect(self.usb.pwr, self.reg.pwr_in)
-   self.connect(self.reg.pwr_out, self.mcu.pwr)
    
-   self.sw = self.Block(DigitalSwitch())
+   self.sw = imp.Block(DigitalSwitch())
    self.connect(self.mcu.gpio.request('sw'), self.sw.out)
-   self.connect(self.usb.gnd, self.sw.gnd)
    
    self.led = ElementDict[IndicatorLed]()
    for i in range(4):
-     self.led[i] = self.Block(IndicatorLed())
+     self.led[i] = imp.Block(IndicatorLed())
      self.connect(self.mcu.gpio.request(f'led{i}'), self.led[i].signal)
-     self.connect(self.usb.gnd, self.led[i].gnd)
```

> <details>
>   <summary>At this point, your HDL might look like...</summary>
>
>   ```python
>   class BlinkyExample(SimpleBoardTop):
>     def contents(self) -> None:
>       super().contents()
>       self.usb = self.Block(UsbCReceptacle())
>       self.reg = self.Block(VoltageRegulator(3.3*Volt(tol=0.05)))
>       self.connect(self.usb.gnd, self.reg.gnd)
>       self.connect(self.usb.pwr, self.reg.pwr_in)
>
>       with self.implicit_connect(
>           ImplicitConnect(self.reg.pwr_out, [Power]),
>           ImplicitConnect(self.reg.gnd, [Common]),
>       ) as imp:
>         self.mcu = imp.Block(Stm32f103_48())
>
>         self.sw = imp.Block(DigitalSwitch())
>         self.connect(self.mcu.gpio.request('sw'), self.sw.out)
>
>         self.led = ElementDict[IndicatorLed]()
>         for i in range(4):
>           self.led[i] = imp.Block(IndicatorLed())
>           self.connect(self.mcu.gpio.request(f'led{i}'), self.led[i].signal)
>
>     def refinements(self) -> Refinements:
>       return super().refinements() + Refinements(
>       instance_refinements=[
>         (['reg'], Tps561201),
>       ])
>   ```
> </details>

### Chain Connects
Another shorthand is for chained connections of blocks with inline declarations of blocks.
We could, **inside the implicit scope, replace the LED and switch instantiations and connections, with**:  
```diff
  ...
- self.sw = imp.Block(DigitalSwitch())
- self.connect(self.mcu.gpio.request('sw'), self.sw.out)
+ (self.sw, ), _ = self.chain(imp.Block(DigitalSwitch()), self.mcu.gpio.request('sw'))
  ...
  for i in range(4):
-   self.led[i] = imp.Block(IndicatorLed())
-   self.connect(self.mcu.gpio.request(f'led{i}'), self.led[i].signal)
+   (self.led[i], ), _ = self.chain(self.mcu.gpio.request(f'led{i}'), imp.Block(IndicatorLed()))
```

`chain` takes blocks and ports as arguments, from left to right as inputs to outputs, and does `connects` to chain them together.
The first argument is treated as the initial input, and the last element is treated as the final output.
Blocks in the middle (if any) have the previous link connected to their `Input`-tagged ports and present their `Output`-tagged ports for the next element, or attach their `InOut`-tagged port to the previous link which is also presented to the next element.
Only one pin per block may be tagged with `Input`, `Output`, and `InOut`.

`chain` returns a chain object, which can be unpacked into a tuple of blocks that are part of the chain and the chain object itself.
The tuple of blocks can be used to name inline blocks declared in the chain (which is done in the blinky example to name the LED and switch), and the chain object can be used to name the links.

> As a more complicated example, running `self.chain(Port1, Block1, Block2, Block3, Block4)` (with the block definitions written as are shown below) would produce this block diagram:  
> ![Chain Connects Example](docs/chain.png)  
> The chain starts at Port1.
> Block1 and Block2 have both an Input and Output port, so the chain goes "through" those blocks.
> Block3 has an InOut port, so it is attached to the previous connection, but the chain goes not go "through" it.
> Because Block4 is the last in the chain, it only needs an Input port.

> <details>
>   <summary>At this point, your HDL might look like...</summary>
>
>   ```python
>   class BlinkyExample(SimpleBoardTop):
>     def contents(self) -> None:
>       super().contents()
>       self.usb = self.Block(UsbCReceptacle())
>       self.reg = self.Block(VoltageRegulator(3.3*Volt(tol=0.05)))
>       self.connect(self.usb.gnd, self.reg.gnd)
>       self.connect(self.usb.pwr, self.reg.pwr_in)
>
>       with self.implicit_connect(
>           ImplicitConnect(self.reg.pwr_out, [Power]),
>           ImplicitConnect(self.reg.gnd, [Common]),
>       ) as imp:
>         self.mcu = imp.Block(Stm32f103_48())
>
>         (self.sw, ), _ = self.chain(imp.Block(DigitalSwitch()), self.mcu.gpio.request('sw'))
>
>         self.led = ElementDict[IndicatorLed]()
>         for i in range(4):
>           (self.led[i], ), _ = self.chain(self.mcu.gpio.request(f'led{i}'), imp.Block(IndicatorLed()))
>
>     def refinements(self) -> Refinements:
>       return super().refinements() + Refinements(
>       instance_refinements=[
>         (['reg'], Tps561201),
>       ])
>   ```
> </details>


## Changing the Microcontroller
_Finally, let's put the finishing touches on this design by changing the microcontroller and specifying a pin assignment._

### Using the IoController Abstract Class
Like the `VoltageRegulator`, there is actually an abstract class for microcontrollers, `IoController`.
`Stm32f103_48` extends this class and adheres to its interface, so we can **change the type of `mcu` to `IoController`**, then **add a refinement to `Stm32f103_48`**.

```diff
  class BlinkyExample(SimpleBoardTop):
    def contents(self) -> None:
      ...
      with self.implicit_connect(
          ...
      ) as imp:
-       self.mcu = imp.Block(Stm32f103_48())
+       self.mcu = imp.Block(IoController())
       
    def refinements(self) -> Refinements:
      return super().refinements() + Refinements(
      instance_refinements=[
        ...
+       (['mcu'], Stm32f103_48),
      ])
```

> `IoController` defines an interface of a power and ground pin, then an array of common IOs including GPIO, ADC, SPI, I2C, and UART.
> Not all devices that implement it have all those capabilities (or the number of IOs requested), in which case they will fail with a compilation error.
> This interface generalizes beyond microcontrollers to anything that can control IOs, such as FPGAs.

With the abstract block in place, we can now easily change it to something else.
Perhaps we want a microcontroller with built-in wifi, so
**change the refinement to an `Esp32_Wroom_32`**.

> If using the IDE, refinements can be changed the same way they are defined.
> The IDE will update the existing refinement instead of inserting a new entry.

### Explicit Pin Assignments
While `IoController` can assign peripherals like SPI pins according to the capabilities of each chip, it does not have access to layout data to do physically-based pin assignment.
However, it does define a `pin_assigns` parameter (as an array-of-strings) which allows specifying a pin number (on the footprint) or pin name (eg, `PC_13` - format specific to each microcontroller) for each requested pin.

We can also force parameter values through the refinements system, using `instance_values`.
Let's arbitrarily choose pins 26-29 for the LEDs.
**Add a pin assignment for the ESP32 in the refinements section**:
```diff
  class BlinkyExample(SimpleBoardTop):
    def refinements(self) -> Refinements:
      return super().refinements() + Refinements(
      instance_refinements=[
        ...
+     ],
+     instance_values=[
+       (['mcu', 'pin_assigns'], [
+         'led0=26',
+         'led1=27',
+         'led2=28',
+         'led3=29',
+       ])
      ])

```

> <details>
>   <summary>At this point, your HDL might look like...</summary>
>
>   ```python
>   class BlinkyExample(SimpleBoardTop):
>     def contents(self) -> None:
>       super().contents()
>       self.usb = self.Block(UsbCReceptacle())
>       self.reg = self.Block(VoltageRegulator(3.3*Volt(tol=0.05)))
>       self.connect(self.usb.gnd, self.reg.gnd)
>       self.connect(self.usb.pwr, self.reg.pwr_in)
>
>       with self.implicit_connect(
>           ImplicitConnect(self.reg.pwr_out, [Power]),
>           ImplicitConnect(self.reg.gnd, [Common]),
>       ) as imp:
>         self.mcu = imp.Block(IoController())
>
>         (self.sw, ), _ = self.chain(imp.Block(DigitalSwitch()), self.mcu.gpio.request('sw'))
>
>         self.led = ElementDict[IndicatorLed]()
>         for i in range(4):
>           (self.led[i], ), _ = self.chain(self.mcu.gpio.request(f'led{i}'), imp.Block(IndicatorLed()))
>
>     def refinements(self) -> Refinements:
>       return super().refinements() + Refinements(
>       instance_refinements=[
>         (['reg'], Tps561201),
>         (['mcu'], Esp32_Wroom_32),
>       ],
>       instance_values=[
>         (['mcu', 'pin_assigns'], [
>           'led0=26',
>           'led1=27',
>           'led2=28',
>           'led3=29',
>          ])
>       ])
>   ```
> </details>

And that's it for system-level (top-level, as opposed to library construction) PCB design!
You can import the netlist into KiCad if you'd like.
Good luck with building PCBs!


## Defining Library Parts
Continue to [the next part of the tutorial](getting_started_schimport.md) on defining a library Block with a KiCad schematic.

### Additional Resources
If you want to some more complex examples of boards designed in this HDL, check out:
- [LED Matrix](examples/test_ledmatrix.py): a charlieplexed LED matrix.
  Ignore the implementation of the charlieplexing LED matrix library block for now, just look at the top-leve design.
- [Simon Game](examples/test_simon.py): an implementation of the Simon electronic game, that uses 12v dome buttons and includes the needed power conversion circuitry.
- [CANdapter](examples/test_can_adapter.py): an USB to isolated CAN adapter, with a bunch of onboard LEDs and an LCD display.
