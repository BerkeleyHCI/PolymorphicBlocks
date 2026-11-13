# Orientation and converter layout evaluation

PB Python remains authoritative for components, physical pins and connectivity.
These generated schematics are reference artifacts. Evaluation completed on
2026-11-08–09 using native KiCad 9.0.9 and 10.0.8.

## USB-C converter comparison

All three profiles use the same compiled 261-component design and source-owned
presentation intent. The controlled baseline preserves the new position-search
stage and suppresses orientation/bridge selection in the evaluation harness.
The rotation-only profile suppresses bridge proposals. Route-order optimization
stays enabled in all profiles. Native component identities, footprints, values,
modeled pin inventories and connected physical-pin sets match across profiles. These two harness profiles are diagnostic controls;
the public API exposes `optimize_orientations`, and explicit placements constrain
position-changing proposals.

| Power-stage sheet | Local fallback endpoints | Crossings | Bends | Local wire (mm) | First export (s) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Controlled baseline | 7 | 45 | 53 | 1939.3 | 182.8 |
| Fixed-center rotations | 6 | 34 | 59 | 1934.2 | 476.2 |
| Rotations + bridge | 0 | 26 | 60 | 1602.1 | 399.8 |

The final bridge removes local route fallbacks, reduces crossings by 42%, and
reduces local wire length by 17% against the controlled baseline. Bends increase
from 53 to 60. Metrics cover local routed wires; fixed pin stubs, final label
repair tails and inter-region connections are excluded. Counts are physical
fallback endpoints, not disconnected electrical nets: labels preserve electrical
connectivity in every profile.

The first-export timings are one observation per profile. Compilation, repeat
verification, native CLI and raster rendering are excluded. Parallel validation
load, OS cache and unrelated host activity were not controlled. No statistical
speedup claim is made, and peak memory was not measured. Orientation increases
export cost; large boards may require the MCP's explicit 900-second timeout
instead of its 300-second default.

## Verification

| Check | Result |
| --- | --- |
| Schematic unit/native suite | 203 tests pass, no skips |
| MCP suite, including complete direct Python/MCP bundle parity | 23 tests pass, no skips |
| Full automatic corpus | 54 targets: 51 valid pass, 2 expected compile rejections, 1 empty |
| Native fidelity | Every valid corpus scope passes KiCad 9 and 10 physical identity, footprint, modeled pin inventory and connected-pin-set comparisons |
| Determinism | Byte-identical repeated exports for every valid corpus design and final curated USB-C export |
| Fixed centers | All 261 physical component centers retain relative positions within their functional regions in the controlled rotation-only comparison; sheet packing may translate regions |
| Opt-out compatibility | Complete USB-C bundle: all 28 files byte-identical to the preceding exporter when `optimize_orientations=False` |
| MCP preparation cost | Exactly one native export per plan, generate or review action; stale plans still rejected before artifact writing |

Across the 51 valid automatic exports, local routing counts compare with the
preceding native implementation as follows. These are machine measures, not
whole-corpus visual acceptance; grouping changes can affect their scope.

| Metric | Decreased | Same | Increased |
| --- | ---: | ---: | ---: |
| Local fallback endpoints | 37 | 14 | 0 |
| Crossings | 34 | 2 | 15 |
| Bends | 33 | 3 | 15 |
| Local wire length | 26 | 2 | 23 |

## Drawing-only findings

Fresh reviewers inspected all eight Ballu sheets and all seventeen PDU sheets,
with dense-region crops. Both are qualified usable references. Ballu retains
convoluted white-LED branches and regulator wiring; PDU retains dense converter
feedback and long connector/MCU harnesses.

The blind USB-C comparison selected the conventional bridge as clearest: two
vertical halfbridges, the inductor link, rail banks and series shunts are directly
recognizable. Review caught a real C66/driver-label overlap. The final bypass
placement uses the controller's measured external-label corridor, and the final
full-board power sheet was rechecked. That overlap is resolved. Gate/bootstrap
and I2C routing around L4 remains dense. Independent final USB-C review covers
the converter sheet, not all twenty pages; the complete page inventory was
contact-sheet scanned separately. Native equality does not approve aesthetics
or electrical design safety.

## Search and evidence scope

The fixed-center stage performs at most two stable PB-path sweeps, with one
baseline-router call per geometrically viable 180-degree trial and cached
incumbent routes. Four measured bridge alternatives add at most four calls.
Existing automatic placement and final route-order searches add separate costs.
This is a finite local search, not a global optimum. Explicit placements retain
rotation locks unless `lock_rotation=False`.

Verified converter core endpoints (controller, FETs, inductor, series shunts and
bootstrap branches) determine primary-path fallbacks. Bulk/bypass-bank fallbacks
are recorded separately. Authored primary nets elsewhere keep their original
meaning. `orientation.after` and `selected_rotations` describe that stage; a
later bridge can change poses. Final symbol coordinates are in the schematic,
and region-level `routing.after` records the selected final local route.

The broad corpus snapshot is `17e639c5da676449bdf5c4ba41cdd779c42285343875421a7442853835757447`.
The final snapshot is `be45bd1a3136463855b796e383bb3729af1f5dfb6b44c7d4ebdb2a0621790292`.
Only `KiCadSchematicPower.power_template_candidates` changed between them, to
move bypasses outside controller label corridors. Automatic corpus circuits use
`template="auto"`, and Ballu/PDU do not request a four-switch bridge, so that
changed function is outside those export paths. The final fix received the full
USB-C export/repeat/native 9+10 checks plus complete unit/MCP suites. The broad
corpus was not redundantly rerun after this isolated visual placement fix.

Reproduction inputs, scripts, source ledgers, per-target results, native XML/SVG,
full PNGs, hash-bound reviews, change-impact analysis and aggregate `RESULTS.json`
are retained in the host PCB repository under
`.local-execution/orientation-readability-2026-11-08/`. Expected rejections and
superseded/rejected visual candidates are retained separately. No PCB edits,
normal board regeneration, commits or pushes were performed.
