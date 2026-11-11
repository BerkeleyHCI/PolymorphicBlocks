# Default schematic corpus

Implementation: `8a3c23d8e0fdaeb8d62dc3793d157eda1ded1f37dd439f1f0a3e5a2e02d941bc`. Completed 54/54.

| Target | Status | Parts / sheets | KiCad 9 / 10 | Repeat | Fallback endpoints | Symbol fallbacks | Crossings | Bends | Local wire mm | Weighted mm | Export s |
|---|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|
| `examples.test_battery_protector:BatteryProtectorCircuit` | pass | 9 / 3 | pass / pass | True | 1 | 3 | 5 | 20 | 1140.46 | 1191.26 | 9.89 |
| `examples.test_bldc_controller:BldcController` | pass | 74 / 5 | pass / pass | True | 5 | 7 | 20 | 108 | 4258.31 | 4532.63 | 49.75 |
| `examples.test_ble_joystick:BleJoystick` | pass | 97 / 10 | pass / pass | True | 2 | 24 | 26 | 88 | 5373.37 | 5596.89 | 39.98 |
| `examples.test_blinky:TestLed` | pass | 2 / 1 | pass / pass | True | 0 | 0 | 0 | 0 | 2.54 | 2.54 | 0.87 |
| `examples.test_blinky:TestBlinkyEmpty` | empty design | 0 / 1 | pass / pass | True | 0 | 0 | 0 | 0 | 0.00 | 0.00 | 0.05 |
| `examples.test_blinky:TestBlinkyBasic` | pass | 3 / 1 | pass / pass | True | 0 | 1 | 0 | 1 | 109.86 | 112.40 | 1.37 |
| `examples.test_blinky:TestBlinkySwitchMatrix` | pass | 15 / 3 | pass / pass | True | 2 | 1 | 8 | 24 | 1360.17 | 1421.13 | 21.87 |
| `examples.test_blinky:TestBlinkySwitchMatrixRefined` | pass | 15 / 3 | pass / pass | True | 2 | 1 | 8 | 24 | 1360.17 | 1421.13 | 22.42 |
| `examples.test_blinky:TestBlinkyRegulated` | pass | 33 / 4 | pass / pass | True | 2 | 5 | 28 | 65 | 3225.16 | 3390.26 | 41.81 |
| `examples.test_blinky:TestBlinkyRgb` | pass | 47 / 4 | pass / pass | True | 2 | 12 | 24 | 74 | 4032.25 | 4220.21 | 42.84 |
| `examples.test_blinky:TestBlinkyImplicit` | pass | 47 / 4 | pass / pass | True | 2 | 12 | 24 | 74 | 4032.25 | 4220.21 | 42.11 |
| `examples.test_blinky:TestBlinkyPinned` | pass | 47 / 4 | pass / pass | True | 2 | 12 | 24 | 74 | 4032.25 | 4220.21 | 43.20 |
| `examples.test_blinky:TestBlinkyWithLibrary` | pass | 29 / 3 | pass / pass | True | 0 | 3 | 10 | 43 | 1911.99 | 2021.21 | 16.83 |
| `examples.test_blinky:TestBlinkyWithLibraryExport` | pass | 29 / 3 | pass / pass | True | 0 | 3 | 10 | 43 | 1911.99 | 2021.21 | 16.43 |
| `examples.test_blinky:TestBlinkyArray` | pass | 27 / 3 | pass / pass | True | 0 | 2 | 7 | 44 | 1880.87 | 1992.63 | 16.80 |
| `examples.test_blinky:TestBlinkyPacked` | pass | 24 / 3 | pass / pass | True | 0 | 2 | 7 | 44 | 1870.71 | 1982.47 | 16.25 |
| `examples.test_blinky:TestBlinkyWithSchematicImport` | pass | 29 / 4 | pass / pass | True | 3 | 2 | 21 | 60 | 3176.27 | 3328.67 | 39.10 |
| `examples.test_blinky:TestBlinkyWithModeledSchematicImport` | pass | 29 / 4 | pass / pass | True | 3 | 2 | 21 | 60 | 3176.27 | 3328.67 | 41.36 |
| `examples.test_blinky:TestBlinkyIncomplete` | expected compile rejection | — | — | — | — | — | — | — | — | — | — |
| `examples.test_blinky:TestBlinkyInvalid` | expected compile rejection | — | — | — | — | — | — | — | — | — | — |
| `examples.test_can_adapter:CanAdapter` | pass | 31 / 3 | pass / pass | True | 0 | 4 | 3 | 28 | 1598.29 | 1669.41 | 11.80 |
| `examples.test_datalogger:Datalogger` | pass | 108 / 8 | pass / pass | True | 3 | 25 | 25 | 142 | 8195.94 | 8556.62 | 84.03 |
| `examples.test_deskcontroller:DeskController` | pass | 74 / 6 | pass / pass | True | 6 | 12 | 24 | 96 | 6003.29 | 6247.13 | 77.48 |
| `examples.test_esp_programmer:EspProgrammer` | pass | 24 / 3 | pass / pass | True | 0 | 5 | 5 | 35 | 1337.95 | 1426.85 | 10.60 |
| `examples.test_fcml:Fcml` | pass | 177 / 12 | pass / pass | True | 11 | 29 | 110 | 271 | 12218.03 | 12906.37 | 152.99 |
| `examples.test_high_switch:HighSwitch` | pass | 89 / 10 | pass / pass | True | 2 | 30 | 28 | 145 | 7497.44 | 7865.74 | 65.16 |
| `examples.test_iot_blinds:IotRollerBlinds` | pass | 39 / 3 | pass / pass | True | 0 | 4 | 20 | 54 | 2348.86 | 2486.02 | 16.15 |
| `examples.test_iot_blinds:IotCurtainCrawler` | pass | 50 / 3 | pass / pass | True | 0 | 7 | 20 | 69 | 3275.96 | 3451.22 | 24.88 |
| `examples.test_iot_display:IotDisplay` | pass | 75 / 5 | pass / pass | True | 2 | 8 | 12 | 60 | 3339.47 | 3491.87 | 36.60 |
| `examples.test_iot_fan:IotFan` | pass | 94 / 8 | pass / pass | True | 3 | 20 | 28 | 91 | 5035.55 | 5266.69 | 44.95 |
| `examples.test_iot_iron:IotIron` | pass | 94 / 6 | pass / pass | True | 9 | 14 | 23 | 128 | 6127.11 | 6452.23 | 74.68 |
| `examples.test_iot_led_driver:IotLedDriver` | pass | 78 / 5 | pass / pass | True | 1 | 9 | 39 | 88 | 4351.02 | 4574.54 | 75.58 |
| `examples.test_iot_thermal_camera:IotThermalCamera` | pass | 119 / 8 | pass / pass | True | 3 | 20 | 36 | 174 | 8555.35 | 8997.31 | 71.89 |
| `examples.test_jd_keyswitch:JacdacKeyswitch` | pass | 37 / 3 | pass / pass | True | 0 | 16 | 8 | 45 | 2266.31 | 2380.61 | 29.98 |
| `examples.test_keyboard:Keyboard` | pass | 80 / 7 | pass / pass | True | 10 | 19 | 24 | 95 | 6205.86 | 6447.16 | 88.04 |
| `examples.test_ledmatrix:LedMatrix` | pass | 56 / 5 | pass / pass | True | 0 | 5 | 14 | 54 | 3690.62 | 3827.78 | 102.09 |
| `examples.test_lora:EspLora` | pass | 105 / 7 | pass / pass | True | 14 | 13 | 13 | 128 | 6196.33 | 6521.45 | 132.68 |
| `examples.test_multimeter:Multimeter` | pass | 107 / 7 | pass / pass | True | 7 | 28 | 18 | 121 | 6920.86 | 7228.20 | 71.54 |
| `examples.test_pcbbot:PcbBot` | pass | 108 / 8 | pass / pass | True | 7 | 29 | 19 | 128 | 7134.86 | 7459.98 | 61.66 |
| `examples.test_protected_charger:ProtectedCharger` | pass | 21 / 2 | pass / pass | True | 0 | 1 | 2 | 18 | 532.13 | 577.85 | 6.40 |
| `examples.test_robotcrawler:RobotCrawler` | pass | 122 / 8 | pass / pass | True | 14 | 21 | 63 | 133 | 7814.94 | 8152.76 | 117.38 |
| `examples.test_robotdriver:RobotDriver` | pass | 83 / 7 | pass / pass | True | 1 | 20 | 31 | 126 | 6395.08 | 6715.12 | 44.28 |
| `examples.test_seven_segment:SevenSegment` | pass | 174 / 13 | pass / pass | True | 9 | 66 | 59 | 116 | 12713.33 | 13007.97 | 144.27 |
| `examples.test_simon:Simon` | pass | 41 / 5 | pass / pass | True | 0 | 12 | 8 | 73 | 3185.80 | 3371.22 | 19.74 |
| `examples.test_swd_debugger:SwdDebugger` | pass | 41 / 4 | pass / pass | True | 2 | 7 | 12 | 56 | 2453.01 | 2595.24 | 29.72 |
| `examples.test_swd_debugger:PicoProbe` | pass | 42 / 3 | pass / pass | True | 14 | 6 | 36 | 63 | 3226.43 | 3386.45 | 82.91 |
| `examples.test_tofarray:TofArray` | pass | 72 / 5 | pass / pass | True | 3 | 23 | 15 | 93 | 4364.99 | 4601.21 | 42.76 |
| `examples.test_usb_fpga_programmer:UsbFpgaProgrammer` | pass | 37 / 3 | pass / pass | True | 5 | 5 | 17 | 60 | 2328.54 | 2480.94 | 43.86 |
| `examples.test_usb_key:UsbKey` | pass | 17 / 2 | pass / pass | True | 0 | 4 | 3 | 14 | 720.72 | 756.28 | 6.74 |
| `examples.test_usb_source_measure:UsbSourceMeasure` | pass | 320 / 18 | pass / pass | True | 8 | 62 | 61 | 363 | 19078.58 | 20000.60 | 212.00 |
| `examples.test_usb_uart:UsbUart` | pass | 18 / 2 | pass / pass | True | 0 | 3 | 3 | 22 | 789.31 | 845.19 | 8.18 |
| `boards.ballu.ballu_gen3.ballu_gen3:BalluGen3` | pass | 105 / 8 | pass / pass | True | 6 | 9 | 25 | 124 | 6763.39 | 7078.35 | 75.92 |
| `boards.pdu.pdu_main:PduMain` | pass | 166 / 14 | pass / pass | True | 10 | 44 | 127 | 279 | 11986.89 | 12695.55 | 177.80 |
| `boards.usbc_pd_bidir.usbc_pd_bidir:UsbcPdBidir` | pass | 261 / 17 | pass / pass | True | 25 | 28 | 144 | 366 | 18053.69 | 18983.33 | 390.46 |

Local selected-route metrics exclude fixed pin stubs, final tails and inter-region wiring. Weighted cost = wire length + 2.54 mm per bend. Export times came from parallel functional workers and are not controlled performance measurements. Native pass and deterministic output do not establish visual approval.

Expected compile rejections remain separate from exporter failures:

- `TestBlinkyIncomplete`: missing refinements/model parameters and resulting unevaluated assertions.
- `TestBlinkyInvalid`: failed voltage-limit assertions.

The empty design is also separate from the 51 nonempty designs. All 52 successful exports, including the empty design, passed both native versions and deterministic repeats. No unexpected failures occurred.

Export times above were collected under parallel functional load; use the [controlled comparison report](schematic-symbol-converter-gaps.md) for runtime conclusions. Native equality does not imply visual acceptance.
