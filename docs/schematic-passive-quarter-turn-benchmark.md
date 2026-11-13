# Passive quarter-turn evaluation

The opt-in `orientation_mode="passive_quarter_turn"` adds one fixed-center
passive sweep after the established placement, half-turn, converter-template and
routing pipeline. The default remains `half_turn`. PB Python remains authoritative
for component identities, values, footprints, physical pins and connectivity.
Generated schematics remain reference artifacts.

Evaluation uses KiCad 9.0.9 and 10.0.8. The frozen implementation digest is
`8f93b26079b6790fd2de88ab445148d4140cdb4a498a3ee7899f25a3df95af20`.
The evaluation harness, source ledgers, native logs, full generated bundles and
controlled timing protocol are retained in the host's ignored
`.local-execution/passive-quarter-turn-2026-11-10/` directory. An earlier,
incomplete cohort was superseded before acceptance when independent review
identified a conflict-count safety gap. A second cohort was superseded to enforce
strict weighted-cost tie retention; secondary bend counts cannot replace an
equal-cost incumbent.

## Selection and safety

Only verified `Device:R`, `Device:R_US`, `Device:C`, `Device:C_Polarized` and
`Device:L` mappings with two distinct terminal attachment positions qualify.
Parallel physical pads remain separate identities. Explicit rotation locks and
authored field coordinates are preserved. Automatic fields are recomputed from
their original policy. No component movement, mirroring or pin swapping occurs
in the new pass; later sheet packing can translate a complete region.

Every eligible passive receives all three alternative-angle evaluations against
the same incumbent, in stable PB-path order. Geometry can reject an angle before
routing. Thus `P` eligible passives add at most `3P` router calls, separately from
the earlier pipeline and one additional bounded route-order search per changed
region. The incumbent's selected routing strategy is reused.

Primary-path fallbacks, crossings and unrelated-circuit intrusion precede
`wire length + 2.54 mm per bend`. New failed endpoints, escape-conflict identities,
wire-clearance contact identities, collisions and page overflow reject a trial.
The identity checks also guard the final route-order result; equal conflict
counts cannot conceal a replacement conflict. Collinear wire splitting does
not change contact identity.

The fully serialized candidate is compared with the cached baseline, including
fields, labels, pin text and ground symbols. New or worsened blocking contacts
roll back all adopted passive changes in that independent board scope. Existing
bad labels cannot whitelist contact with a different obstacle or a larger
overlap. Rollback restores cached poses and routes without another optimization
loop. Final geometry determines bounds and fingerprints before an adopted sheet
plan is validated. Per-region `routing.json` records trials and rollback evidence.

## Verified-library fixture

This small compiled fixture uses KiCad's actual `Device:C_Polarized` definition
and a generic physical anchor. A 270-degree turn makes the positive-terminal
connection shorter while preserving polarity and the relative component centers.
Both modes pass native KiCad 9/10 physical-netlist comparisons. The only
readability diagnostics in either mode are the two intentionally generic anchors.

| Optimizer metric, local wires plus fixed pin stubs | Half-turn | Quarter-turn |
| --- | ---: | ---: |
| Wire length (mm) | 66.50 | 48.87 |
| Bends | 4 | 4 |
| Weighted cost (mm) | 76.66 | 59.03 |
| Crossings / failed endpoints / visual-clearance conflicts | 0 / 0 / 0 | 0 / 0 / 0 |

The optimizer's segment-based bend measure can differ from a viewer's count of
visible corners. The shorter retained path reduces this fixture's measured wire
length by 26.5% and weighted cost by 23.0%; it does not establish whole-board gains.

## Focused verification

| Check | Result |
| --- | --- |
| Complete schematic suite | 228 tests pass, no skips; native KiCad 9/10 enabled |
| MCP suite | 25 tests pass, no skips; complete Python/MCP bundle parity |
| Legacy golden bundle | All nine files byte-identical to the preceding exporter with default options |
| Curated default compatibility | All 69 bundle files byte-identical to the preceding exporter: Ballu 16, PDU 25, USB-C 28; source ledgers match |
| Real-routing coverage | 90/270-degree resistor, capacitor, polarized capacitor and inductor fixtures; parallel pads retained |
| Search safety | Complete three-angle coverage, stable ordering, 3P bound, locks, fixed fields, ties, collisions and clearance replacement regressions |
| Integration safety | Post-template ordering, cached-baseline rollback, final-route-order guard, final plan fingerprint, serialized label/body and wire-contact severity |

The C66 driver-supply label-corridor regression remains in the complete suite.
`optimize_orientations=False` bypasses both orientation passes and preserves
legacy output. Tests and native equivalence do not imply whole-sheet visual
acceptance or electrical-design approval.


## Full corpus

| Outcome | Targets | Native KiCad 9/10 and repeat checks |
| --- | ---: | --- |
| Valid compiled designs | 51 | All pass |
| Expected compile rejections | 2 | `TestBlinkyIncomplete`, `TestBlinkyInvalid`; no schematic generated |
| Empty design | 1 | Zero physical components; recorded separately and native-checked |
| Curated mode comparisons | 6 | Ballu, PDU and USB-C in both modes; all pass |

All source ledgers and frozen implementation hashes remain unchanged during
these runs. Every eligible passive receives complete three-angle coverage.
Across the automatic corpus, 1,941 eligible instances produce 5,765 router calls
within the 5,823-call bound. Ten valid targets retain 28 changes: 13 turns of 90
degrees, 12 of 270 degrees, and three of 180 degrees. The latter arise from the
balanced objective rather than an additional angular capability.

The [complete per-target table](schematic-passive-quarter-corpus.md) includes
fallbacks, crossings, bends, wire length, weighted cost, scene findings and
first-export time. Its route-plus-stub metrics differ from serialized wire totals.
These are machine acceptance results; whole-corpus visual approval is not claimed.

The opt-in example was executed successfully with
`python -m examples.export_schematic --output <scratch-directory> --symbol-dir <symbols> --orientation-mode passive_quarter_turn`.

## Curated boards

Both modes pass byte-identical repeated exports and KiCad 9/10 physical identity,
footprint, modeled-pin inventory and connected-pin-set comparisons in every
scope. Ballu contains 105 components on eight sheets. PDU contains 166 components
across its main, driver-daughter and e-stop-panel scopes on 17 sheets. USB-C
contains 261 components across main and control scopes on 20 sheets.

These totals cover local routed wires across each complete design. Fixed pin
stubs, final label-repair tails and inter-region links are excluded here. The
optimizer uses the wider wire-plus-stub measure shown in the fixture table.
Fallback endpoints remain electrically connected through labels. The scene
column counts all readability findings, including symbol-fallback diagnostics;
it is not a count of newly introduced blocking collisions.

| Board / mode | Fallback endpoints | Crossings | Bends | Local wire (mm) | Weighted cost (mm) | Readability findings |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Ballu / half-turn | 11 | 57 | 173 | 7804.2 | 8243.6 | 117 |
| Ballu / quarter-turn | 11 | 57 | 173 | 7804.2 | 8243.6 | 117 |
| PDU / half-turn | 16 | 218 | 398 | 16873.2 | 17884.1 | 175 |
| PDU / quarter-turn | 16 | 218 | 399 | 16863.1 | 17876.5 | 175 |
| USB-C / half-turn | 33 | 245 | 508 | 19749.1 | 21039.5 | 361 |
| USB-C / quarter-turn | 33 | 245 | 508 | 19749.1 | 21039.5 | 361 |

| Board | Eligible passives | Angle evaluations | Additional router calls / 3P limit | Locally proposed turns | Finally adopted turns | Regions rolled back |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Ballu | 54 | 162 | 156 / 162 | 15 | 0 | 9 |
| PDU | 99 | 297 | 287 / 297 | 30 | 1 | 9 |
| USB-C | 183 | 549 | 506 / 549 | 43 | 0 | 9 |

All three boards receive complete trial coverage. Geometry rejects some angles
before routing. New blocking serialized-scene findings cause the reported
scope-wide rollbacks. All eight Ballu schematic documents and all twenty USB-C
documents are byte-identical between modes after rollback. Their routing
evidence still records the attempted opportunities. The retained PDU change is
`estop_panel.estop.indicator.res`, R40, from 0 to 90 degrees; it saves 10.16 mm of
wire with one additional measured bend, reducing weighted cost by 7.62 mm.

| First export under parallel functional load (not controlled timing) | Half-turn (s) | Quarter-turn (s) |
| --- | ---: | ---: |
| Ballu | 135.4 | 239.6 |
| PDU | 333.2 | 638.5 |
| USB-C | 578.4 | 1047.1 |

These are single first-export observations. Compilation, repeat verification,
native CLI and raster rendering are excluded. Parallel test load and host
conditions prevent treating these observations as controlled performance ratios.
The final functional cohort used eight isolated workers, with long historical
cases scheduled first. The controlled timing run is separate.

## Drawing-only review

A fresh reviewer inspected the PDU e-stop detail from drawings alone. The
horizontal R40 makes its D9 LED branch read more directly left to right, with no
visible regression or label/body/wire overlap. The sheet still has generic
connector pin names, long crossing wire runs, small whole-sheet text and a short
stepped LED-to-resistor connection. The reviewed PNGs match the final validated
native render hashes. The other 16 PDU documents differ only in the design
fingerprint in title-block comment 2; their parsed S-expressions otherwise match.

A different fresh reviewer inspected the actual USB-C converter sheet 4/10.
Both modes produce identical pixels, SHA256
`732941d7d122b18d837b5e8e6680176fd6b7aa78226ed47237d34c6524e3a685`.
No definite controller/C66 body-field collision or clipping was seen. The dense
central wire corridor, crowded controller-side ground markings, long C66
driver-supply detour and remote C67/C68/L4 fields remain. The earlier C66 overlap
stays resolved, while fixed-center optimization provides no retained improvement
on this sheet. The initially supplied overview-only render was rejected by the
reviewer and replaced with the title-verified converter render before acceptance.

Ballu has no changed schematic pages to review; its complete eight-document
identity was checked and the regenerated contact sheet inspected. These reviews
cover the named drawings only, with electrical fidelity checked separately.

## Remaining readability flags

The pass is a nonregression optimizer and preserves existing baseline findings.
The following unchanged flags require visual triage; the drawing-only reviews
above do not establish that all sheets are clear of existing contacts.

| Final curated design, either mode | Text-collision flags | Wire-through-text flags | Label-placement conflicts | Unresolved anchors |
| --- | ---: | ---: | ---: | ---: |
| Ballu | 29 | 68 | 1 | 0 |
| PDU | 27 | 88 | 2 | 0 |
| USB-C | 68 | 232 | 13 | 0 |

These detector findings are not electrical mismatches. They also are not all
symbol-fallback warnings: substantial baseline presentation work remains. The
new pass rejects new or worsened blocking contacts and does not repair the
baseline scene. A scope-level rollback can discard otherwise useful local
rotations elsewhere in that scope. Keep the feature opt-in.

## Controlled USB-C timing

Controlled USB-C timing used one compiled design instance, one warm-up per mode, then three sequential exports per mode in AB / BA / AB order. Both option files differ only in `orientation_mode`. The process was pinned to logical CPU 10 on the Intel Core i9-14900K; sibling CPU 11, CPU frequency, thermal state and other host activity were not reserved or fixed. Functional workers had finished before measurement. Each export had a 900-second limit.

| Mode | Three measured exports (s) | Median (s) | Min–max (s) |
|---|---|---:|---|
| `half_turn` | 372.68, 417.34, 415.94 | 415.94 | 372.68–417.34 |
| `passive_quarter_turn` | 700.80, 779.72, 794.96 | 779.72 | 700.80–794.96 |

The median quarter-turn export took 1.875× the half-turn median (87.5% longer). For this USB-C input, both modes produced byte-identical schematic files and equal final local-route metrics: 245 crossings, 508 bends, 19,749.135 mm wire length and 21,039.455 mm weighted cost. The serialized wire length was25,257.76 mm across 1,769 segments; 13 label-placement conflicts remained, with zero unresolved anchors. Those metric scopes differ: local-route totals omit fixed pin stubs, final label tails and inter-region links. No quarter-turn change survived the serialized-scene safety gate on this board.

Timing includes only `KiCadSchematicExporter.export()`. Compilation, reference assignment, presentation-plan refresh, KiCad CLI/netlist verification, rendering, bundle hashing/metrics and garbage collection between exports are excluded. Warm-up files are audit artifacts, not additional measured observations. Three observations per mode support descriptive median/min/max reporting only; no statistical significance, controlled-frequency performance or peak-memory claim is made.

Independent post-run audit passed all six sample statuses, planned order, summary statistics, warm-up/sample bundle hashes, saved warm bundles, same-input fingerprint, source hashes (69 files), symbol-library hashes (448 files), runner hash, frozen implementation hash and protocol hash. Framework: `8f93b26079b6790fd2de88ab445148d4140cdb4a498a3ee7899f25a3df95af20`. Compiled input: `baacea3f413ce899b340b821691118d9778a3dad4473ebd6a93c3b6f60face07`. Runtime assertions also checked the compiled payload and source hashes before each sample and after the last sample; the summary is written only after all final guards pass.

Evidence: `benchmark/protocol.json`, `benchmark/samples.json`, `benchmark/summary.json`, `benchmark/compiled-input.json`, and `controlled-timing-audit.json`.


## Final geometry and rollout

The post-timing artifact audit checks all 532 curated physical symbol instances:
Ballu 105, PDU 166 and USB-C 261. Reference/value/footprint/PB-path properties,
instance UUIDs and physical-pin UUID inventories remain unchanged between modes.
All region translations are zero in these exports, so absolute and relative
component centers remain fixed. Only the PDU indicator resistor changes angle,
from 0 to 90 degrees. Rotation locks remain respected.

Keep `passive_quarter_turn` opt-in. It finds genuine quarter-turn improvements in
some automatic targets and the PDU branch, but the curated USB-C export takes
about 1.87 times the default median runtime while retaining identical drawings.
A reviewed explicit Python rotation hint can preserve a known presentation choice
without repeatedly searching unrelated passives. This change does not write hints
back into Python or edit generated schematics by hand.

The MCP default timeout is 300 seconds and its maximum is 900 seconds. The
controlled quarter-turn observations fit inside 900 seconds, while the separate
1,047.1-second parallel cold observation exceeds that limit. These observations
provide no general deadline guarantee; use native Python for longer batch
experiments. Generation itself needs no KiCad process or GUI; native KiCad was
used for the acceptance checks and rendered views.

Code, tests, example, API documentation, MCP guide, companion skill and rendered
comparisons are supplied in the existing development worktrees. Experimental ELK
work and project PCB/manufacturing outputs are preserved. No commits or pushes
are part of this delivery.
