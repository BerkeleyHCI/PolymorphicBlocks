# Generated KiCad schematics

PB Python defines the parts, physical pad mappings and connectivity. Generated
schematics are a one-way view of that compiled design. Every sheet says to edit
Python and regenerate; KiCad edits are overwritten. The existing PB netlist
remains the supported PCB update workflow.

## Compile and open

```python
from edg import compile_board_inplace, SchematicExportOptions

compile_board_inplace(
    MyBoard,
    schematic=SchematicExportOptions(
        design_name="MyBoard",
        symbol_library_dirs=("/usr/share/kicad/symbols",),
    ),
)
```

A runnable opt-in example is
[`examples/export_schematic.py`](../examples/export_schematic.py). Run
`python -m examples.export_schematic --output /tmp/pb-schematic-example --symbol-dir /usr/share/kicad/symbols`
from the PB checkout to generate the existing LED design in a dedicated
destination. The example uses Python presentation hints to keep the LED and
its current-limiting resistor in circuit order.

![Native KiCad 9 excerpt of the opt-in LED example](images/schematic-example.png)

Open the root schematic in `MyBoard/MyBoard.schematic/`. Each independent
physical board scope has its own root. The manifest lists generated files,
source provenance, a compiled-design fingerprint and diagnostics.

Library directories are searched in order, followed by `KICAD9_SYMBOL_DIR`
(or the major version selected in options). The output embeds the definitions,
so readers do not need the original symbol libraries installed. Generation does
not download files or require a running KiCad GUI.

## Actual symbols and pin mappings

Standard resistor, capacitor, inductor, LED, diode, switch and connector mappings
use verified KiCad pin numbers. An exact-model registry handles additional known
parts. It never guesses a symbol from the reference designator or substitutes an
unrelated IC with similar functions. A physical block can declare its own map:

```python
self.schematic_symbol("Device:LED", {"1": "1", "2": "2"})
```

Keys are library symbol pin numbers; values are physical footprint pad numbers.
Export mappings do not change schematic-import `symbol_pinning()`.

For ESP32-C6-WROOM-1, use the exact symbol in
[Espressif's official library](https://github.com/espressif/kicad-libraries/blob/main/symbols/Espressif.kicad_sym).
Download `Espressif.kicad_sym` into one of the configured directories, retaining
the vendor license. Definitions from newer libraries are normalized to the
supported embedded-symbol grammar. Explicit exact-part registry maps can omit
library pins absent from PB's modeled pad inventory; they do not invent NCs.

Missing symbols produce diagnosed functional views with the actual modeled pin
names and numbers, supply pins above, and ground below. Such views are not
claimed to be vendor symbols. Unknown packages and ambiguous diode polarity
remain unmapped. Unsupported multi-unit symbols also fall back explicitly.

## Wires, grouping and presentation

The exporter places functional groups and routes orthogonal local connections.
Wire branches are explicitly split, with junction dots; crossings between
unrelated nets have no junction. Internal routed nets need no redundant labels.
Cross-sheet signals use labels, and ground uses the standard power symbol.
Native netlist comparison is required to establish connectivity equivalence.

Readable electrical values are displayed near components; the original physical
Value and Footprint properties remain intact. Procurement descriptions do not
need to occupy the drawing. Failed local routes retain matching net labels and
produce diagnostics rather than changing connectivity.

Automatic grouping and placement are a baseline, not a guarantee of readable
circuit topology. Complex circuits can use Python-owned presentation hints:

```python
from edg import SchematicExportOptions, SchematicPlacement

options = SchematicExportOptions(
    "MyBoard",
    symbol_library_dirs=("/usr/share/kicad/symbols",),
    placements={
        "led.package": SchematicPlacement("Status LED", 70, 80, rotation=180),
        "led.res": SchematicPlacement("Status LED", 100, 80, rotation=90),
    },
)
```

A placement contains a functional region, millimetre coordinates, an orthogonal
rotation, optional horizontal reflection, and optional reference/value annotation
coordinates. Hints define presentation only: the compiled physical graph still
defines every wire. Missing component paths and incomplete hinted groups fail
explicitly. Hints arrange a circuit within a region; the shared sheet planner
then translates whole regions onto A3 landscape pages, preserving their scale,
relative positions and wiring. A functional region is not a separate sheet.

### Plan complete regions onto sheets

Without assignments, the planner packs measured regions in stable order,
favoring related regions. Measurements include headings, symbol graphics,
fields, pin labels, power symbols and wires. Fixed margins and gutters prevent
region overlap; oversized automatic groups continue on numbered regions.
Explicitly hinted circuits must fit as a whole or report an error. Mechanical
parts may occupy the overview inset instead of a dedicated circuit page.

Assign related regions to named pages when the automatic organization needs
refinement. Assignment keys are canonical region IDs or unambiguous titles:

```python
options = SchematicExportOptions(
    "MyBoard",
    symbol_library_dirs=("/usr/share/kicad/symbols",),
    sheet_assignments={
        "Charger": "1. Power input",
        "USB interface": "1. Power input",
        "MCU": "2. Controller",
    },
)
```

A requested page that cannot hold its complete regions gains a diagnosed
continuation rather than clipping content. Sheets containing multiple regions
retain local labels at region boundaries; short inter-region wires are added
only where an unobstructed aligned corridor exists. Power-rail affinity alone
does not justify merging every circuit into a single region.

The same planner is available before serialization:

```python
from dataclasses import replace
from edg import KiCadSchematicExporter, SchematicSheetPlanner, SchematicSheetPlan

plan = SchematicSheetPlanner().plan(compiled, options)
plan_data = plan.to_dict()  # JSON-compatible, stable region IDs and coordinates
# Refine region-to-sheet placement without changing the component inventory.
restored = SchematicSheetPlan.from_dict(plan_data)
options = replace(options, sheet_plan=restored)
bundle = KiCadSchematicExporter().export(compiled, options)
```

Plans bind to a deterministic fingerprint of the compiled design and resolved presentation.
Stale plans, missing/duplicate regions, cross-board moves, out-of-bounds positions
and overlapping regions are errors. The output includes `sheet-plan.json` and
planning diagnostics for sparse sheets, small regions and cross-sheet signal
counts. These measurements help review; they do not imply visual approval.

The Ballu Gen3 companion `ballu_gen3_schematic.py` demonstrates functional hints
for parallel LED branches, a soft-power gate, charger, MCU support, servo
interfaces, display and an addressable RGB chain. Named sheet assignments
consolidate its circuits into seven circuit pages plus an overview. Circuit
connectivity remains defined by the board's Python source.

### A useful first page

![Native Ballu Gen3 system overview with witnessed functional relationships](images/schematic-overview.png)

Multi-sheet boards open on a system overview. Functional cards show a readable
name, circuit summary, actual component count and detail-sheet number. Each card
is a real KiCad hierarchical sheet link. The source notice, board identity and
mechanical reference area remain visible. The root has page number 1.

By default, up to sixteen cards occupy a deterministic four-by-four grid. A
bounded selection of compiled cross-sheet relationships is drawn without arrows;
GND is excluded and no power or signal direction is guessed. The connection key
identifies each line. Large sheet inventories use a compact directory and the
existing contents hierarchy. Single-sheet designs retain their circuit root.

Use Python-owned overview annotations for a stronger system narrative:

```python
from edg import SchematicOverview, SchematicOverviewBlock, SchematicOverviewLink

options = replace(options, overview=SchematicOverview(
    blocks=(
        SchematicOverviewBlock("Power", "Power management", "Protection / regulation", 0, 1),
        SchematicOverviewBlock("Controller", "Controller", "MCU / programming support", 1, 1),
    ),
    links=(
        SchematicOverviewLink("Power", "Controller", "3.3 V supply", ("v3v3",), directed=True),
    ),
))
```

Here `Power` and `Controller` must be actual unique sheet titles or canonical
sheet IDs, and `v3v3` must really connect components on both sheets. Grid columns
and rows are integers 0–3. Unspecified cards fill unused cells. Duplicate cells,
unknown/ambiguous sheets, cross-board links, self-links and unwitnessed nets are
errors. Titles/labels are limited to 48 characters, summaries to 96, and there
are at most eight authored relationships. The schema is available through
`SchematicOverview.to_dict()` / `from_dict()` for data-only tooling.

An arrow states the author's intended functional flow. Its shared-net witnesses
establish physical association; they do not prove voltage direction, signal
causality or electrical safety. Diagram connectors are graphical polylines,
never schematic wires, pins or nets. They cannot alter electrical connectivity.

`KiCadSchematicExporter().overview(compiled, options)` previews the same model
written to `overview.json`. Each board record contains card identities/bounds,
part counts, selected relationships with complete net witnesses, routing status,
and `shared_connections` for all non-GND sheet pairs. This lets agents refine
presentation using compiled evidence instead of guessing net names. The
`overview_present` flag distinguishes a circuit-only root from a system index.
Overview annotations are included in the plan fingerprint.

The key and coverage counters disclose that the diagram is selective. A blocked
graphical route retains its relationship in the key with an explicit diagnostic;
it does not invent a wire or silently disappear. Direction/coverage, native
connectivity validation and visual approval are separate results. Inspect the
native page at readable scale, including arrowheads, line tags, descriptions,
mechanical notes, clipping and working sheet navigation.

### Optional agent-assisted refinement

The companion agentic-pcb integration provides `plan_pb_schematic`,
`generate_pb_schematic_candidate` and `review_pb_schematic_candidate`, backed by
the same framework planner and exporter. Candidates live in isolated directories;
source, plan, library and artifact hashes reject stale evidence. The tools accept
schema-validated presentation data rather than arbitrary Python callbacks.
Native review returns SVGs and connectivity results with visual approval pending.

The `pb-schematic-generation` companion skill guides whole-board inspection and
presentation refinement. Keep durable choices beside the board source and
regenerate. Review every sheet for usable circuit communication, including local
support wiring and pin/field legibility; native netlist equality is a separate
acceptance gate.

## Integrations and verification

`KiCadSchematicExporter.export(compiled, options)` returns an in-memory
`SchematicExport` bundle and diagnostics. Compile successfully and assign
reference designators before calling it. `bundle.write()` stages files before
replacement and removes only stale manifest-owned files. `generate=False`
writes nothing.

For every root, use KiCad's schematic netlist export in `kicadxml` format, then
compare with `SchematicVerification.verify_schematic_netlist()` against that
`NetlistTransform` scope. This checks component identities, footprints, physical
pin inventories and connected pin sets, independently of net names. Inspect
native SVGs for circuit readability, annotations and visual crossing ambiguity;
netlist equality alone is not a readable-schematic acceptance test.

The implementation is tested against native KiCad 9.0.9 and 10.0.8 using the
official containers under Apptainer. Focused regressions cover mappings,
inheritance, missing libraries, stable output, local wiring, preserved values,
Python placement/reflection, whole-region packing, stale/invalid plans, measured
bounds, exact component coverage, named continuations and index pagination. Interactive GUI navigation has
not been tested. Generic passive pin types do not reproduce PB electrical checks
or establish electrical design/manufacturing acceptance.
