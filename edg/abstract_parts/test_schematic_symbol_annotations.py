"""Verify schematic metadata against the physical pad mappings, including sparse connectors."""

from typing_extensions import override
import json
import unittest
from typing import Any, Dict, Optional, Tuple

from ..electronics_model import Block, FootprintBlock, ScalaCompiler
from .Diode import BaseDiode, DiodeStandardFootprint
from .Led import Led, LedStandardFootprint
from .PassiveConnector import FootprintPassiveConnector
from .Switch import TactileSwitch
from .ZenerDiode import ZenerDiode
from .TvsDiode import TvsDiode


class AnnotationLed(Led, FootprintBlock):
    @override
    def contents(self) -> None:
        super().contents()
        footprint = "LED_SMD:LED_0603_1608Metric"
        self.footprint("D", footprint, LedStandardFootprint._make_pinning(self, footprint))


class AnnotationDiode(BaseDiode, FootprintBlock):
    @override
    def contents(self) -> None:
        super().contents()
        footprint = "Diode_SMD:D_SOD-123"
        self.footprint("D", footprint, DiodeStandardFootprint._make_pinning(self, footprint))


class AnnotationZener(ZenerDiode, FootprintBlock):
    @override
    def contents(self) -> None:
        super().contents()
        footprint = "Diode_SMD:D_SOD-123"
        self.footprint("D", footprint, DiodeStandardFootprint._make_pinning(self, footprint))


class AnnotationTvs(TvsDiode, FootprintBlock):
    @override
    def contents(self) -> None:
        super().contents()
        footprint = "Diode_SMD:D_SOD-123"
        self.footprint("D", footprint, DiodeStandardFootprint._make_pinning(self, footprint))


class AnnotationSwitch(TactileSwitch, FootprintBlock):
    @override
    def contents(self) -> None:
        super().contents()
        self.footprint(
            "SW", "Button_Switch_SMD:SW_SPST_TL3305A", {"1": self.sw, "2": self.sw, "3": self.com, "4": self.com}
        )


class AnnotationConnector(FootprintPassiveConnector):
    allowed_pins = range(1, 5)

    @override
    def part_footprint_mfr_name(self, length: int) -> Tuple[str, str, str]:
        return f"Connector_PinHeader_2.54mm:PinHeader_1x{length:02d}_P2.54mm_Vertical", "", ""


class AnnotationBoard(Block):
    @override
    def contents(self) -> None:
        super().contents()
        self.led = self.Block(AnnotationLed())
        self.diode = self.Block(AnnotationDiode())
        self.zener = self.Block(AnnotationZener(zener_voltage=(4, 6)))
        self.tvs = self.Block(AnnotationTvs(working_voltage=(0, 5)))
        self.sw = self.Block(AnnotationSwitch(voltage=(0, 5)))
        self.conn = self.Block(AnnotationConnector(length=3))
        self.sparse = self.Block(AnnotationConnector(length=3))
        self.connect(
            self.led.a,
            self.diode.anode,
            self.zener.anode,
            self.tvs.anode,
            self.sw.sw,
            self.conn.pins.request("1"),
            self.sparse.pins.request("1"),
        )
        self.connect(
            self.led.k,
            self.diode.cathode,
            self.zener.cathode,
            self.tvs.cathode,
            self.sw.com,
            self.conn.pins.request("2"),
            self.conn.pins.request("3"),
            self.sparse.pins.request("3"),
        )


class SchematicSymbolAnnotationTest(unittest.TestCase):
    def test_verified_physical_pad_mappings(self) -> None:
        compiled = ScalaCompiler.compile(AnnotationBoard)

        def mapping(path: str) -> Optional[Dict[str, Any]]:
            raw = compiled.get_value((path, "sch_symbol"))
            if not raw:
                return None
            assert isinstance(raw, str)
            result: Dict[str, Any] = json.loads(raw)
            return result

        self.assertEqual(mapping("led"), {"lib_id": "Device:LED", "pinning": {"1": "1", "2": "2"}})
        self.assertEqual(mapping("diode"), {"lib_id": "Device:D", "pinning": {"1": "1", "2": "2"}})
        self.assertEqual(mapping("zener"), {"lib_id": "Device:D_Zener", "pinning": {"1": "1", "2": "2"}})
        self.assertIsNone(mapping("tvs"))
        self.assertEqual(
            mapping("sw"),
            {"lib_id": "Switch:SW_Push_Dual", "pinning": {"1": "1", "3": "2", "2": "3", "4": "4"}},
        )
        self.assertEqual(
            mapping("conn"),
            {"lib_id": "Connector_Generic:Conn_01x03", "pinning": {"1": "1", "2": "2", "3": "3"}},
        )
        self.assertIsNone(mapping("sparse"))


if __name__ == "__main__":
    unittest.main()
