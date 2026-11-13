# Capacitor coverage and compact LED-driver layouts

This change fixes ordinary capacitor symbol fallbacks and gives verified
TPS92200 buck LED drivers a bounded functional layout in the native exporter.
Python remains authoritative. No electrical redesign, PCB edits, manufacturing
output adoption, commits or pushes are part of this evaluation.

## Implementation and limits

Fresh Datalogger compilation identified its ordinary capacitor leaves as
`edg.vendor_parts.generic.GenericCapacitor.GenericMlcc`, with physical
1=pos and 2=neg. The registry now resolves the exact model's six supported
ceramic packages to `Device:C`. Model identity, footprint and pin roles must
all match. Polarized/custom capacitors do not acquire guessed mappings.
Explicit mappings retain precedence and invalid explicit mappings remain errors.

The manifest's additive `symbol_coverage` inventory records every component's
compiled class, mapping origin, selected symbol or categorized fallback reason.
Library absence is distinct from missing mappings. Resolved symbols also enter
the existing ownership and passive-orientation logic.

The verified TPS92200 model supplies the BOOT/SW and FB/sense roles. A unique
compiled bootstrap capacitor, current-sense resistor and output inductor are
required. Virtual loads remain virtual; no pads or connectors are invented.
Four measured placement proposals compare against the cached legacy result,
using its selected routing strategy. The bootstrap sits beside BOOT/SW; the
sense resistor has its own feedback corridor; rail banks pack by measured field
edges rather than capacitor centers.

Primary-path visibility, crossings and unrelated-circuit intrusion precede
wire length plus 2.54 mm per bend. Ties preserve the incumbent. Failed endpoints,
new pin escape conflicts, collisions, page overflow and degraded wire clearance
reject proposals. A final serialized-scene check includes pin text, labels,
fields and ground glyphs. New or worse findings or more sheets restore the
cached region. Fitting proposals retain the incumbent packing-cell dimensions
as explicit whitespace to avoid disturbing unrelated circuits; both content
and reserved bounds are recorded. This reservation also avoids claiming that
shorter local wiring necessarily makes the whole board smaller.

The pass is automatic, skips authored placements, and precedes optional passive
quarter turns. The quarter-turn default is unchanged. Authored field coordinates
are preserved. Search evidence is under `routing.json`'s `regions[].led_buck`;
top-level `after` metrics describe the actually selected route.

MCP exposes this same native evidence and compares manifest/routing artifacts
with its one fresh export per action. It adds no layout algorithm or public
option. Whole-bundle bytes intentionally change because of the additive manifest
inventory; deterministic repeated exports remain required.

## Reproducibility

The final frozen non-test PB implementation digest is
`8a3c23d8e0fdaeb8d62dc3793d157eda1ded1f37dd439f1f0a3e5a2e02d941bc`.
The baseline is the prior frozen implementation
`8f93b26079b6790fd2de88ab445148d4140cdb4a498a3ee7899f25a3df95af20`.
Matched comparisons use the default `half_turn` mode; the previous quarter-turn
corpus is not substituted for a default-mode baseline.

Host evidence is isolated under
`.local-execution/schematic-gaps-2026-11-11-final/`; exploratory runs and rejected
larger layouts remain under `.local-execution/schematic-gaps-2026-11-11/`.
Sources, implementation files, artifacts and native render inventories are
hash-bound. KiCad 9.0.9 and 10.0.8 use the installed container wrappers.

The public examples can also be reproduced without MCP or the host harness.
With PB's normal compiler dependencies and `KICAD9_SYMBOL_DIR` configured:

```python
from pathlib import Path
from edg import ScalaCompiler, KiCadSchematicExporter, SchematicExportOptions
from edg.electronics_model.RefdesRefinementPass import RefdesRefinementPass
from examples.test_iot_led_driver import IotLedDriver

compiled = ScalaCompiler.compile(IotLedDriver)
compiled.append_values(RefdesRefinementPass().run(compiled))
bundle = KiCadSchematicExporter().export(compiled, SchematicExportOptions(
    "IotLedDriver", source="examples.test_iot_led_driver.IotLedDriver"))
bundle.write(Path("output/IotLedDriver.schematic"))
```

Use `Datalogger` from `examples.test_datalogger` for the capacitor case. The
focused regressions are `edg.electronics_model.test_kicad_symbol_registry` and
`edg.electronics_model.test_schematic_led_buck`. The manifest identifies each
root for native KiCad netlist/SVG export and physical-pin comparison as described
in [schematic export verification](schematic-export.md#integrations-and-verification).

## Validation results

- 261 schematic tests passed, with zero skips, including configured native
  KiCad 9/10 fixtures, symbol mappings, ambiguous topologies, parallel pads,
  authored annotations/placements, ties, failed endpoints, scene rollback,
  sheet-count rollback and final metric/strategy evidence.
- 27 configured MCP tests passed with zero skips; a real candidate also passed
  KiCad 9.0.9/10.0.8 connectivity comparisons and native SVG export. Twelve
  package resource/dependency contracts passed. Review preserves one fresh
  native export per action and rejects changed evidence artifacts.
- Both focused designs passed native component identity, footprint, modeled
  pin-inventory and connected-pin-partition comparisons on KiCad 9 and 10.
  Repeated exports were byte-identical and captured sources stayed unchanged.

| Default automatic export | Symbols falling back | Sheets | Failed endpoints | Crossings | Bends | Local wire mm | Weighted mm | Scene findings |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Datalogger before | 67 | 10 | 9 | 24 | 142 | 8036.560 | 8397.240 | 233 |
| Datalogger after | 25 | 8 | 3 | 25 | 142 | 8195.945 | 8556.625 | 195 |
| IotLedDriver before | 9 | 5 | 1 | 47 | 104 | 5341.620 | 5605.780 | 65 |
| IotLedDriver after | 9 | 5 | 1 | 39 | 88 | 4351.020 | 4574.540 | 61 |

These whole-design measurements cover selected local router wires, excluding
fixed pin stubs, final label tails and inter-region links. Weighted cost is
wire length plus 2.54 mm per bend. Remaining scene findings are reported, not
waived. Failed local-wire endpoints retain labeled electrical connections; they
are not missing physical pins or native netlist mismatches. Datalogger resolves
42 ordinary capacitor boxes and recovers six local
endpoints, but has one more crossing and 159.385 mm more local wire. Symbol
correction is not a claim that every whole-design route metric improves.

All four IotLedDriver channels adopt compact layouts. Each uses four proposal
route calls, reduces local crossings 2→0, bends 10→6, wire 397.51→149.86 mm and
weighted cost 422.91→165.10 mm, with zero failed endpoints. This is a 62.3%
wire-length and 61.0% weighted-cost reduction per channel. The entire design
retains five sheets and reduces weighted local cost by 18.4%. All four final
serialized-scene gates record no new or worse findings.

The [complete 54-target default corpus](schematic-symbol-converter-corpus.md)
has 51 nonempty native/repeat passes, one separately reported empty-design pass
and two expected compile rejections. `TestBlinkyIncomplete` lacks required
refinements/model parameters; `TestBlinkyInvalid` violates voltage assertions.
Neither rejection reaches the exporter. No unexpected exporter, electrical,
determinism or provenance failure occurred.

| Curated design / mode | Parts / sheets | KiCad 9 / 10 | Byte-identical repeat | Unchanged prior schematic files |
|---|---:|---|---|---:|
| Ballu / half turn | 105 / 8 | pass / pass | yes | 8 / 8 |
| Ballu / quarter turn | 105 / 8 | pass / pass | yes | 8 / 8 |
| PDU / half turn | 166 / 17 | pass / pass | yes | 17 / 17 |
| PDU / quarter turn | 166 / 17 | pass / pass | yes | 17 / 17 |
| USB-C / half turn | 261 / 20 | pass / pass | yes | 20 / 20 |
| USB-C / quarter turn | 261 / 20 | pass / pass | yes | 20 / 20 |

All 90 curated schematic files match their prior matching-mode outputs.
Presentation options and every loaded design-source hash also match: 48 source
files for Ballu, 54 for PDU and 63 for USB-C. The additive manifest evidence is
intentionally excluded from that schematic-byte comparison. Existing drawing
review limitations are retained; these checks do not create new visual approval.

The additional LED-driver quarter-turn compatibility case also passed both
native versions, deterministic repeat and all source guards: 78 components,
five sheets, 58 eligible passives, 174 angle evaluations and 174 routing calls
(`3P`, with complete coverage). Serialized-scene safety rolled seven regions
back to their cached incumbents. All four compact LED channels remain selected,
and all five final schematic documents are byte-identical to the new default
mode. No additional quarter-turn improvement is claimed for this circuit.

## Controlled runtime

Timing runs only after every functional coordinator has exited. Each
design/implementation pair uses one compiled object, one warm-up and three
sequential measured exports, with a 900-second ceiling per export. Compilation,
native CLI checks, rendering and input/library hashing are outside the measured
interval. All measured processes use logical CPU 10 on an Intel Core i9-14900K.
Its sibling CPU 11 is not reserved; host load and frequency are not controlled.

Normalized physical-input hashes include component paths, references,
footprints, values, part identifiers, compiled pinning and connected physical-pin
partitions, including singletons. Before/after input and library hashes must
stay unchanged, and old/new physical-input hashes must match per design.
All measured output bundle hashes must repeat exactly within each implementation.
These guards are separate from the earlier native electrical comparisons.
Manifest fingerprints also bind symbol and placement geometry, so old/new
manifest fingerprints deliberately differ; the normalized physical-input hash
establishes equal electrical input for timing.

| Design | Baseline median s (range) | New median s (range) | Observed change | Guards |
|---|---:|---:|---:|---|
| Datalogger | 77.32 (75.94–77.51) | 72.72 (72.05–73.02) | −5.9% | pass |
| IotLedDriver | 55.25 (55.05–56.03) | 63.81 (63.05–63.88) | +15.5% | pass |

Measured sample order was baseline Datalogger, new Datalogger, baseline
IotLedDriver, new IotLedDriver, each with its own warm-up followed by three
samples. Baseline-first ordering, uncontrolled host activity/frequency and only
three observations limit inference: these results do not establish statistical
significance, a general latency bound or cold MCP action performance. Peak
memory is not measured.

All input, library, source, implementation and output-repeat guards passed.
The compact LED-driver pass costs about 8.56 seconds in this measured case while
reducing each channel's weighted local route cost by 61.0%. Datalogger's median
falls by about 4.60 seconds. These are case-specific observed costs, not a claim
of universal exporter speedup. The automatic gated rollout is retained; passive
quarter turns remain opt-in.

Raw samples, physical/library hashes and per-export bundle hashes are in the
host evidence's `timing/` records and `timing-summary.json`. `FINAL-VERIFICATION.json`
confirms that the production-source digest still matches the frozen snapshot,
all functional work is complete and no functional worker remains active.

## Visual limitations

Native component/net equality is independent of visual acceptance. The drawing
review of Datalogger's MCU closes the ordinary-capacitor-box finding for the
inspected components, but retains long supply/oscillator detours, a generic
crystal, split support and mixed functional page grouping as limitations.
Its custom supercapacitor remains a deliberate unresolved symbol mapping.

A separate fresh drawing-only review inspected native full sheets and readable
details for all four LED-driver channels. It closes the bootstrap long-loop and
crossover finding throughout. The external LED load/terminal meaning is still
missing from the rendered channel, and inductor fields remain farther away than
ideal. Page-three whitespace and mixed automatic grouping also remain. These
are recorded limitations; whole-board visual approval is pending. No
corpus-wide aesthetic approval is inferred from the native checks.

The final Datalogger PNGs match the precursor drawing review byte-for-byte; the
hash-bound reuse record retains that review's sampled scope and limitations.
Native SVG export timestamps differ, so only drawing bytes are reused as visual
evidence. Final native connectivity checks are fresh.

Full-sheet inventories and hashes remain in the isolated host evidence.
