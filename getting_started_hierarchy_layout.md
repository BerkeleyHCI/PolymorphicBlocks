# Hierarchical Layout Tutorial

Hierarchical layout tips and tricks, using the macropad circuit from the [introductory tutorial](getting-started.md) as an example.

This assumes familiarity with KiCad PCB layout.
If you're new to KiCad, there are plenty of excellent tutorials online, go through one of those, then come back.


## Requirements

The example uses the Keyswitch Kicad Library, available on the KiCad Plugin and Content Manager.

![Keyswitch](docs/kicad/pcm_keyswitch_library.png)

For hierarchical loading and replication, you have a few options:

- Use the Sublayout plugin (KiCad 8+), also available on the KiCad Plugin and Content Manager.
  ![Sublayout](docs/kicad/pcm_sublayout.png)
  - This was designed to work with netlist-based flows and automatically detects grouping based on hierarchy data in the netlist.  
  - This works with KiCad 10+, but zone replication is broken.
- Use KiCad's native design blocks feature (KiCad 10+).
  - This tutorial covers hierarchical replication, but hierarchical loading is not covered.
  - The design blocks flow is heavyweight (requires local library creation) and (at least for netlist driven flows, like this one) requires you to group footprints within a block manually.
- Use KiCad's Multi-Channel and Placement Rule Area feature.
  - This tutorial does not cover this.
  - This seems brittle to other traces overlapping the placement rule area and does not seem grouping-aware. 

> Replicate Layout, Save/Restore Layout, and HierarchicalPCB will **NOT work**. 
> These require and validate against schematic files, which are not generated in this HDL flow.


## Netlist Import

1. Start the PCB Editor (standalone)

   ![PCB Editor](docs/kicad/app_pcb_editor.png)
2. Open Import Netlist from the toolbar: 
   
   ![pcb_netlist.png](docs/kicad/pcb_netlist.png)
   > If you launched the PCB Editor from a KiCad project, this will not be on the toolbar (you will have "Update PCB from Schematic" instead).
   > You can still access it from the menu: File > Import > Netlist...
3. Select the generated netlist file, likely `BlinkyExample/BlinkyExample.net` in whereever you ran your HDL script, then click Load and Test Netlist.
   It should load with no errors, but there may be some warnings about missing pins.
   ![pcb_netlist_dialog.png](docs/kicad/pcb_netlist_dialog.png)

   > In KiCad 10, uncheck "Group footprints based on symbol group".
   > This ignores hierarchical data in the netlist and removes footprint grouping.

4. Click "Update PCB" to place the components on the board.
   Drop them anywhere for now.
   ![pcb_initial.png](docs/kicad/pcb_initial.png)
   - This may give you error(s) about missing pins, which you can ignore.


## Switch Matrix Placement and Replication

The switch, diode, LED, and LED capacitor are all part of a SwitchCell hierarchical sheet in the netlist, which allows the layout to be replicated for each switch.

Start by arranging all the switch footprints in a grid.

This can be done by selecting all the switch footprints, then right-clicking and selecting Create From Selection > Create Array...
Set the grid array size (here, 3x2 as consistent with the HDL parameters) and spacing (19.05mm typical for mechanical keyboard switch spacing).
Set Item Source to Arrange selection (move the footprints, instead of creating new ones), and the Grid Position to Source items remain in place.

![kicad_array.png](docs/kicad/kicad_array.png)

![pcb_switcharray.png](docs/kicad/pcb_switcharray.png)

You may need to swap components to get the right ordering.

![pcb_switcharray_ordered.png](docs/kicad/pcb_switcharray_ordered.png)

Then, lay out a single switch cell, including the switch, diode, LED, LED capacitor, and traces.
Here is an example layout:

![pcb_switchcell.png](docs/kicad/pcb_switchcell.png)

In this layout, I've allocated the top layer to run horizontal traces (rows and LEDs) and the bottom layer to run vertical traces (columns).

> Tip: use the footprint pathname on the F.Fab layer to find the footprints that are part of the same block.
> For example, find all the footprints starting with `sw.sw[0,0]`.

> Right-click > Select > Items in Same Hierarchical Sheet only selects items _strictly_ in the same sheet, not recursively.
> For example, selecting the hierarchical sheet for the switch includes the diode, but not the LED or LED capacitor, which are in a sub-sheet.

Group the switch cell footprints: select them, right click, Grouping > Group Items.

![pcb_switchcell.png](docs/kicad/pcb_switchcell_group.png)

### Option 1: Sublayout Plugin

1. Enter into the switch cell footprint group you just created and select the switch.
   ![pcb_switchcell_anchor.png](docs/kicad/pcb_switchcell_anchor.png)
   The group defines the objects to replicate, while the selected footprint defines the _anchor footprint_, the matching component in the other sheets that other footprints are placed around.

2. Run the Sublayout plugin and select all the instances (bottom list box).
   ![sublayout_selected.png](docs/kicad/sublayout_selected.png)
3. Press Replicate, and the plugin will replicate the layout, including footprint positions, traces, and groupings.
   ![pcb_switchmatrix_replicated.png](docs/kicad/pcb_switchmatrix_replicated.png)


### Option 2: KiCad Design Blocks

_KiCad 10+ required._

1. Open the Design Blocks panel: main menu > View > Panels > Design Blocks.
   ![kicad_designblocks_empty.png](docs/kicad/kicad_designblocks_empty.png)

### Snaking

The LEDs are connected in a snaking pattern, which means every other row reverses the LED connection order.
You may want to have a different switch cell for the odd rows, which flips the LED rotation.


## Loading a Microcontroller Layout

_The tutorial only covers using the Sublayout plugin._
_It may be possible to create a design block library using KiCad 10+, but that is a more heavyweight flow and is not covered._ 

