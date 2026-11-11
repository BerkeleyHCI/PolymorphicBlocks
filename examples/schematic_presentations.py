"""Optional source-owned explanatory annotations for generated example schematics.

These describe intent already present in the example/model sources. They do not
supply layout coordinates, change parts, or add electrical connections. The
ordinary automatic export remains available without this companion data.
"""

from edg.electronics_model.KiCadSchematicPresentation import SchematicPresentation

# Evidence: test_battery_protector.py contents connects the holder to protector
# input and the LED/resistor to protector output; there is no external load jack.
PRESENTATIONS = {
    "BatteryProtectorCircuit": {
        "schema": 1,
        "components": {
            "li_ion_bat": {"description": "18650 battery source, 2.5-4.2 V", "pin_names": {"1": "BAT+", "2": "BAT-"}},
            "led.package": {"description": "Protected-output indicator; this LED branch is the modeled load"},
            "battery_protector.do_fet": {"description": "Discharge protection in battery return"},
            "battery_protector.co_fet": {"description": "Charge protection in battery return"},
        },
    },
    # test_bldc_controller.py explicitly uses IoControllerPowerOut/UsbOut;
    # Feather_Nrf52840.generate exports device pins 2 (3V3) and 26 (USB).
    "BldcController": {
        "schema": 1,
        "components": {
            "mcu.device": {
                "description": "Feather module supplies USB-derived vusb and regulated 3.3 V",
                "pin_names": {"2": "3V3 OUT", "26": "USB OUT", "4": "GND"},
            },
        },
    },
    # EspProgrammerTc2030Inline.contents explicitly assigns all six contacts;
    # UART TX/RX names are from the TARGET perspective, as its comment states.
    "EspProgrammer": {
        "schema": 1,
        "components": {
            "out.conn": {
                "description": "ESP target programming; UART names are target-side",
                "pin_names": {
                    "1": "3V3",
                    "2": "BOOT",
                    "3": "TARGET TX",
                    "4": "TARGET RX",
                    "5": "GND",
                    "6": "EN / RESET",
                },
            },
        },
    },
    # test_protected_charger.py connects battery -> pmos -> pmos_load -> pin2.
    "ProtectedCharger": {
        "schema": 1,
        "components": {
            "pmos.mp1": {"description": "Battery reverse protection with bidirectional charge path"},
            "pmos_load.fet": {"description": "Protected battery/charger node feeds load reverse protection"},
            "pwr_pins": {"description": "Protected load output", "pin_names": {"1": "GND", "2": "LOAD+", "3": "GND"}},
        },
    },
    # StTscSenseChannel.contents terminates res.b in DummyPassive. It models the
    # touch input but creates no physical electrode/connector footprint.
    "UsbKey": {
        "schema": 1,
        "components": {
            "ts1.res": {"description": "Touch channel 1; electrode geometry is not modeled in PB"},
            "ts2.res": {"description": "Touch channel 2; electrode geometry is not modeled in PB"},
        },
        "interfaces": [
            {"component": "ts1.res", "pin": "2", "name": "Touch electrode 1 endpoint"},
            {"component": "ts2.res", "pin": "2", "name": "Touch electrode 2 endpoint"},
        ],
    },
    # FpgaProgrammingHeader.pwr is optional and receives no board connection.
    # Ft232hl.contents connects internal VCCD regulator output to VCCIO.
    "UsbFpgaProgrammer": {
        "schema": 1,
        "components": {
            "out.conn": {
                "description": "FPGA MPSSE target; pin 1 is unconnected in this PB design",
                "pin_names": {
                    "1": "PWR (unconnected)",
                    "2": "CS",
                    "3": "GND",
                    "4": "SCK",
                    "5": "GND",
                    "6": "MOSI",
                    "8": "MISO",
                    "9": "GND",
                    "10": "RESET",
                },
            },
            "ft232.ic": {"description": "USB MPSSE bridge; VCCIO supplied by internal VCCD regulator"},
        },
    },
    # test_iot_led_driver.py explicitly omits connectors and uses DummyPassive
    # loads. Tps92200 connects leda to output capacitor +, ledk to sense resistor b.
    "IotLedDriver": {
        "schema": 1,
        "components": {
            **{
                f"led_drv[{i}].power_path.out_cap.cap": {
                    "description": f"LED channel {i + 1} output; solder external LED anode to this positive node"
                }
                for i in range(4)
            },
            **{
                f"led_drv[{i}].rsense.res.res": {
                    "description": f"LED channel {i + 1} return; external LED cathode connects at pin 2"
                }
                for i in range(4)
            },
        },
        "interfaces": [
            {
                "component": f"led_drv[{i}].power_path.out_cap.cap",
                "pin": "1",
                "name": f"LED{i + 1}+ (solder connection)",
            }
            for i in range(4)
        ]
        + [
            {"component": f"led_drv[{i}].rsense.res.res", "pin": "2", "name": f"LED{i + 1}- (solder connection)"}
            for i in range(4)
        ],
    },
}


def presentation_for(design_name: str) -> SchematicPresentation:
    """Return an independent typed presentation, empty for unannotated examples."""
    return SchematicPresentation.from_dict(PRESENTATIONS.get(design_name, {"schema": 1}))
