# Hierarchical Layout Tutorial

Hierarchical layout tips and tricks, using the macropad circuit from the [introductory tutorial](getting-started.md) as an example.


## Requirements

The example uses the Keyswitch Kicad Library, available on the KiCad Plugin and Content Manager.

![Keyswitch](docs/kicad/pcm_keyswitch_library.png)

For hierarchical loading and replication, you have two options:

- Use KiCad 10+ and the native design blocks feature.
  - This tutorial covers hierarchical replication, but hierarchical loading is not covered.
  - The design blocks flow is heavyweight (requires local library creation) and (at least for netlist driven flows, like this one) requires you to group footprints within a block manually.
- Use the Sublayout plugin (KiCad 8+), also available on the KiCad Plugin and Content Manager.
  ![Sublayout](docs/kicad/pcm_sublayout.png)
  - This was designed to work with netlist-based flows and automatically detects grouping based on hierarchy data in the netlist.  
  - This works with KiCad 10+, but zone replication is broken.
- Replicate Layout, Save/Restore Layout, and HierarchicalPCB will **NOT work**. These require and validate against schematic files, which are not generated in this HDL flow.


## Netlist Import

1. Start the PCB Editor (standalone)

   ![PCB Editor](docs/kicad/app_pcb_editor.png)
2. Open Import Netlist from the toolbar: 
   
   ![pcb_netlist.png](docs/kicad/pcb_netlist.png)
   > If you launched the PCB Editor from a KiCad project, this will not be on the toolbar (you will have "Update PCB from Schematic" instead).
   > You can still access it from the menu: File > Import > Netlist...

3. Select the generated netlist file, likely `BlinkyExample/BlinkyExample.net` in whereever you ran your HDL script.


> In KiCad 10, uncheck "Group footprints based on symbol group".
> This ignores hierarchical data in the netlist and removes footprint grouping.

