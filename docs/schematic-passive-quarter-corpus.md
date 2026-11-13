# Passive quarter-turn corpus results

Frozen implementation: `8f93b26079b6790fd2de88ab445148d4140cdb4a498a3ee7899f25a3df95af20`.

All 54 targets completed: 51 valid designs passed, two intentionally invalid designs were rejected during compilation, and one design was empty. Each valid design and the empty design passed KiCad 9.0.9 and 10.0.8 physical-netlist comparisons and byte-identical repeat checks. Source and framework hashes remained stable.

Deltas compare the cached incumbent after the legacy placement/half-turn/template/routing pipeline with the final selected passive result, including rollback. Wire, bend and cost deltas use local routed wires plus fixed pin stubs, excluding final label tails and inter-region links. Cost is wire millimeters + 2.54 per measured bend. The scene column counts all final readability findings, including fallback-symbol diagnostics. Export seconds are a single first successful export under eight-worker functional load; they are not controlled performance samples.

Adopted turns are relative angle changes (90/180/270). The three 180-degree changes arise from the balanced objective; the 25 quarter turns exercise the new angular capability. The 28 changes occur across 10 targets. All 1,941 eligible passives receive three angle evaluations; 5,765 additional router calls stay within the 5,823-call limit. Geometry rejects the other trials before routing.

| Target | Status | Eligible P | Calls / 3P | Adopted 90/180/270 | Δ fallback | Δ crossings | Δ bends | Δ wire mm | Δ cost mm | Scene | Export s |
| --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `BalluGen3` | pass | 54 | 162 / 162 | 0/0/0 | +0 | +0 | +0 | 0.00 | 0.00 | 130 | 160.7 |
| `PduMain` | pass | 99 | 291 / 297 | 1/0/1 | +0 | +0 | -4 | -17.78 | -27.94 | 195 | 454.4 |
| `UsbcPdBidir` | pass | 183 | 540 / 549 | 0/0/0 | +0 | +0 | +0 | 0.00 | 0.00 | 414 | 959.3 |
| `BatteryProtectorCircuit` | pass | 3 | 9 / 9 | 1/0/1 | +0 | +0 | -1 | -33.02 | -35.56 | 5 | 24.6 |
| `BldcController` | pass | 38 | 114 / 114 | 0/0/0 | +0 | +0 | +0 | 0.00 | 0.00 | 97 | 114.8 |
| `BleJoystick` | pass | 36 | 108 / 108 | 0/0/0 | +0 | +0 | +0 | 0.00 | 0.00 | 146 | 92.4 |
| `TestBlinkyArray` | pass | 17 | 49 / 51 | 0/0/0 | +0 | +0 | +0 | 0.00 | 0.00 | 21 | 33.5 |
| `TestBlinkyBasic` | pass | 1 | 3 / 3 | 0/0/0 | +0 | +0 | +0 | 0.00 | 0.00 | 2 | 2.4 |
| `TestBlinkyEmpty` | empty (0 physical components) | — | — | — | — | — | — | — | — | — | — |
| `TestBlinkyImplicit` | pass | 21 | 61 / 63 | 0/0/0 | +0 | +0 | +0 | 0.00 | 0.00 | 61 | 92.3 |
| `TestBlinkyIncomplete` | expected compile rejection | — | — | — | — | — | — | — | — | — | — |
| `TestBlinkyInvalid` | expected compile rejection | — | — | — | — | — | — | — | — | — | — |
| `TestBlinkyPacked` | pass | 13 | 37 / 39 | 0/0/0 | +0 | +0 | +0 | 0.00 | 0.00 | 21 | 31.6 |
| `TestBlinkyPinned` | pass | 21 | 61 / 63 | 0/0/0 | +0 | +0 | +0 | 0.00 | 0.00 | 61 | 97.4 |
| `TestBlinkyRegulated` | pass | 14 | 40 / 42 | 1/1/1 | +0 | -2 | +2 | +15.88 | +20.95 | 47 | 64.3 |
| `TestBlinkyRgb` | pass | 21 | 61 / 63 | 0/0/0 | +0 | +0 | +0 | 0.00 | 0.00 | 62 | 100.0 |
| `TestBlinkySwitchMatrix` | pass | 1 | 3 / 3 | 0/0/0 | +0 | +0 | +0 | 0.00 | 0.00 | 22 | 27.1 |
| `TestBlinkySwitchMatrixRefined` | pass | 1 | 3 / 3 | 0/0/0 | +0 | +0 | +0 | 0.00 | 0.00 | 22 | 29.3 |
| `TestBlinkyWithLibrary` | pass | 18 | 52 / 54 | 3/0/1 | +0 | -2 | -6 | -52.70 | -67.95 | 27 | 38.4 |
| `TestBlinkyWithLibraryExport` | pass | 18 | 52 / 54 | 3/0/1 | +0 | -2 | -6 | -52.70 | -67.95 | 27 | 35.8 |
| `TestBlinkyWithModeledSchematicImport` | pass | 21 | 61 / 63 | 0/0/0 | +0 | +0 | +0 | 0.00 | 0.00 | 26 | 86.8 |
| `TestBlinkyWithSchematicImport` | pass | 21 | 61 / 63 | 0/0/0 | +0 | +0 | +0 | 0.00 | 0.00 | 26 | 86.9 |
| `TestLed` | pass | 1 | 3 / 3 | 0/0/0 | +0 | +0 | +0 | 0.00 | 0.00 | 1 | 1.2 |
| `CanAdapter` | pass | 18 | 54 / 54 | 0/0/0 | +0 | +0 | +0 | 0.00 | 0.00 | 29 | 29.4 |
| `Datalogger` | pass | 33 | 99 / 99 | 0/0/0 | +0 | +0 | +0 | 0.00 | 0.00 | 233 | 160.0 |
| `DeskController` | pass | 34 | 102 / 102 | 0/0/0 | +0 | +0 | +0 | 0.00 | 0.00 | 72 | 168.7 |
| `EspProgrammer` | pass | 11 | 33 / 33 | 1/1/1 | +0 | -3 | -5 | -54.61 | -67.31 | 28 | 20.4 |
| `Fcml` | pass | 107 | 317 / 321 | 0/0/0 | +0 | +0 | +0 | 0.00 | 0.00 | 288 | 364.1 |
| `HighSwitch` | pass | 25 | 75 / 75 | 0/0/0 | +0 | +0 | +0 | 0.00 | 0.00 | 147 | 128.1 |
| `IotCurtainCrawler` | pass | 26 | 78 / 78 | 0/0/0 | +0 | +0 | +0 | 0.00 | 0.00 | 41 | 64.0 |
| `IotRollerBlinds` | pass | 21 | 63 / 63 | 0/0/0 | +0 | +0 | +0 | 0.00 | 0.00 | 27 | 33.8 |
| `IotDisplay` | pass | 33 | 99 / 99 | 0/0/0 | +0 | +0 | +0 | 0.00 | 0.00 | 125 | 76.7 |
| `IotFan` | pass | 52 | 156 / 156 | 0/0/0 | +0 | +0 | +0 | 0.00 | 0.00 | 113 | 114.8 |
| `IotIron` | pass | 60 | 180 / 180 | 0/0/0 | +0 | +0 | +0 | 0.00 | 0.00 | 124 | 173.1 |
| `IotLedDriver` | pass | 58 | 166 / 174 | 0/0/0 | +0 | +0 | +0 | 0.00 | 0.00 | 65 | 155.6 |
| `IotThermalCamera` | pass | 82 | 242 / 246 | 0/0/0 | +0 | +0 | +0 | 0.00 | 0.00 | 185 | 207.1 |
| `JacdacKeyswitch` | pass | 11 | 33 / 33 | 0/0/0 | +0 | +0 | +0 | 0.00 | 0.00 | 35 | 53.6 |
| `Keyboard` | pass | 33 | 99 / 99 | 0/0/0 | +0 | +0 | +0 | 0.00 | 0.00 | 120 | 174.5 |
| `LedMatrix` | pass | 13 | 39 / 39 | 0/0/0 | +0 | +0 | +0 | 0.00 | 0.00 | 105 | 134.3 |
| `EspLora` | pass | 68 | 204 / 204 | 0/0/0 | +0 | +0 | +0 | 0.00 | 0.00 | 152 | 306.7 |
| `Multimeter` | pass | 61 | 182 / 183 | 0/0/0 | +0 | +0 | +0 | 0.00 | 0.00 | 178 | 168.4 |
| `PcbBot` | pass | 45 | 135 / 135 | 0/0/0 | +0 | +0 | +0 | 0.00 | 0.00 | 191 | 116.5 |
| `ProtectedCharger` | pass | 8 | 24 / 24 | 2/0/0 | +0 | -1 | -1 | +6.35 | +3.81 | 16 | 13.1 |
| `RobotCrawler` | pass | 64 | 190 / 192 | 0/0/0 | +0 | +0 | +0 | 0.00 | 0.00 | 208 | 276.5 |
| `RobotDriver` | pass | 40 | 120 / 120 | 0/0/0 | +0 | +0 | +0 | 0.00 | 0.00 | 123 | 98.6 |
| `SevenSegment` | pass | 87 | 261 / 261 | 0/0/0 | +0 | +0 | +0 | 0.00 | 0.00 | 179 | 427.1 |
| `Simon` | pass | 17 | 51 / 51 | 1/0/3 | +0 | +0 | -3 | -66.04 | -73.66 | 59 | 38.4 |
| `PicoProbe` | pass | 26 | 78 / 78 | 0/0/0 | +0 | +0 | +0 | 0.00 | 0.00 | 75 | 208.2 |
| `SwdDebugger` | pass | 25 | 73 / 75 | 0/0/0 | +0 | +0 | +0 | 0.00 | 0.00 | 69 | 72.6 |
| `TofArray` | pass | 34 | 102 / 102 | 0/0/0 | +0 | +0 | +0 | 0.00 | 0.00 | 119 | 103.7 |
| `UsbFpgaProgrammer` | pass | 21 | 63 / 63 | 0/0/0 | +0 | +0 | +0 | 0.00 | 0.00 | 56 | 109.8 |
| `UsbKey` | pass | 9 | 27 / 27 | 0/0/2 | +0 | +0 | +2 | -40.64 | -35.56 | 4 | 16.5 |
| `UsbSourceMeasure` | pass | 209 | 625 / 627 | 0/0/0 | +0 | +0 | +0 | 0.00 | 0.00 | 488 | 469.9 |
| `UsbUart` | pass | 8 | 24 / 24 | 0/1/1 | +0 | -1 | -3 | -36.83 | -44.45 | 17 | 17.0 |

These are machine acceptance results. Drawing-only review covered the named curated sheets in the [main report](schematic-passive-quarter-turn-benchmark.md); this table does not assert whole-corpus visual approval.
