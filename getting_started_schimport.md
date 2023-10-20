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



## HDL Stub


## Top-Level Board


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
