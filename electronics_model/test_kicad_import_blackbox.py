import unittest

from edg_core import Block, Builder
from electronics_model import KiCadSchematicBlock, VoltageSink, Ground, AnalogSource


class KiCadBlackboxBlock(KiCadSchematicBlock):
    """Block with a blackbox part, a sub-blocks that only knows it has a footprint and pins and doesn't
    map to one of the abstract types."""
    def __init__(self) -> None:
        super().__init__()
        self.pwr = self.Port(VoltageSink.empty(), optional=True)
        self.gnd = self.Port(Ground.empty(), optional=True)
        self.out = self.Port(AnalogSource.empty(), optional=True)
        self.import_kicad(self.file_path("resources", "test_kicad_import_blackbox.kicad_sch"),
                          conversions={  # ideal ports only here
                              'U1.Vdd': VoltageSink(),
                              'U1.GND': Ground(),
                              'res.2': AnalogSource(),
                          })


class KiCadImportBlackboxTestCase(unittest.TestCase):
    def test_import_blackbox(self):
        # the elaborate_toplevel wrapper is needed since the inner block uses array ports
        pb = Builder.builder.elaborate_toplevel(KiCadBlackboxBlock())
        print(pb)
