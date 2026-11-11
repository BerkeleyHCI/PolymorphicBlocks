"""Opt-in schematic export example; run from the PB checkout.

python -m examples.export_schematic --output /tmp/pb-schematic-example \\
    --symbol-dir /usr/share/kicad/symbols

This writes generated review artifacts to the requested destination. PB Python
remains authoritative; no KiCad installation is needed for generation.
"""

import argparse
from pathlib import Path

from edg import SchematicExportOptions, SchematicPlacement, SchematicPresentation, compile_board
from .test_blinky import TestLed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--symbol-dir", action="append", default=[], help="Ordered symbol library directory (repeatable)"
    )
    parser.add_argument("--orientation-mode", choices=("half_turn", "passive_quarter_turn"),
                        default="half_turn", help="Opt in to four-orientation passive refinement")
    args = parser.parse_args()
    compile_board(
        TestLed,
        (str(args.output), "TestLed"),
        schematic=SchematicExportOptions(
            "TestLed",
            symbol_library_dirs=tuple(args.symbol_dir),
            optimize_orientations=True,  # deterministic fixed-center trials
            orientation_mode=args.orientation_mode,
            presentation=SchematicPresentation.from_dict({
                "schema": 2,
                "circuits": [{
                    "id": "status_indicator",
                    "title": "Status LED",
                    "summary": "Current-limited LED indicator; the series resistor sets LED current.",
                    "components": ["led.res", "led.package"],
                }],
            }),
            placements={
                "led.res": SchematicPlacement("Status LED", 80, 100, lock_rotation=False),
                "led.package": SchematicPlacement("Status LED", 80, 70, rotation=90),
            },
        ),
    )
    print(args.output / "TestLed.schematic")


if __name__ == "__main__":
    main()
