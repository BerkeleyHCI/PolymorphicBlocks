import unittest

from . import TransformUtil
from .NetlistGenerator import NetBlock
from .SvgPcbBackend import arrange_blocks, flatten_packed_block, PlacedBlock, BlackBoxBlock


class PartPlacerTestCase(unittest.TestCase):
    def test_placement(self) -> None:
        u1 = NetBlock(
            footprint="Package_QFP:LQFP-48-1EP_7x7mm_P0.5mm_EP3.6x3.6mm",
            refdes="U1",
            part="",
            value="",
            full_path=TransformUtil.Path.empty().append_block("U1"),
            path=[],
            class_path=[],
        )
        r1 = NetBlock(
            footprint="Resistor_SMD:R_0603_1608Metric",
            refdes="R1",
            part="",
            value="",
            full_path=TransformUtil.Path.empty().append_block("R1"),
            path=[],
            class_path=[],
        )
        r2 = NetBlock(
            footprint="Resistor_SMD:R_0603_1608Metric",
            refdes="R2",
            part="",
            value="",
            full_path=TransformUtil.Path.empty().append_block("R2"),
            path=[],
            class_path=[],
        )
        arranged = arrange_blocks([u1, r1, r2])
        self.assertEqual(arranged.elts[0][0], TransformUtil.Path.empty().append_block("U1"))
        self.assertAlmostEqual(arranged.elts[0][1][0], 5.15, places=2)
        self.assertAlmostEqual(arranged.elts[0][1][1], 5.15, places=2)
        self.assertEqual(arranged.elts[1][0], TransformUtil.Path.empty().append_block("R1"))
        self.assertAlmostEqual(arranged.elts[1][1][0], 12.78, places=2)
        self.assertAlmostEqual(arranged.elts[1][1][1], 0.73, places=2)
        self.assertEqual(arranged.elts[2][0], TransformUtil.Path.empty().append_block("R2"))
        self.assertAlmostEqual(arranged.elts[2][1][0], 12.78, places=2)
        self.assertAlmostEqual(arranged.elts[2][1][1], 3.19, places=2)

    def test_placement_hierarchical(self) -> None:
        u1 = NetBlock(
            footprint="Package_QFP:LQFP-48-1EP_7x7mm_P0.5mm_EP3.6x3.6mm",
            refdes="U1",
            part="",
            value="",
            full_path=TransformUtil.Path.empty().append_block("A").append_block("U1"),
            path=[],
            class_path=[],
        )
        r1 = NetBlock(
            footprint="Resistor_SMD:R_0603_1608Metric",
            refdes="R1",
            part="",
            value="",
            full_path=TransformUtil.Path.empty().append_block("A").append_block("R1"),
            path=[],
            class_path=[],
        )
        r2 = NetBlock(
            footprint="Resistor_SMD:R_0603_1608Metric",
            refdes="R2",
            part="",
            value="",
            full_path=TransformUtil.Path.empty().append_block("A").append_block("R2"),
            path=[],
            class_path=[],
        )
        r3 = NetBlock(
            footprint="Resistor_SMD:R_0603_1608Metric",
            refdes="R3",
            part="",
            value="",
            full_path=TransformUtil.Path.empty().append_block("B").append_block("R3"),
            path=[],
            class_path=[],
        )
        arranged = arrange_blocks([u1, r1, r2, r3])

        self.assertAlmostEqual(arranged.elts[0][1][0], 0, places=2)
        self.assertAlmostEqual(arranged.elts[0][1][1], 0, places=2)
        assert isinstance(arranged.elts[0][0], PlacedBlock)
        self.assertEqual(
            arranged.elts[0][0].elts[0][0], TransformUtil.Path.empty().append_block("A").append_block("U1")
        )
        self.assertAlmostEqual(arranged.elts[0][0].elts[0][1][0], 5.15, places=2)
        self.assertAlmostEqual(arranged.elts[0][0].elts[0][1][1], 5.15, places=2)
        self.assertEqual(
            arranged.elts[0][0].elts[1][0], TransformUtil.Path.empty().append_block("A").append_block("R1")
        )
        self.assertAlmostEqual(arranged.elts[0][0].elts[1][1][0], 12.78, places=2)
        self.assertAlmostEqual(arranged.elts[0][0].elts[1][1][1], 0.73, places=2)
        self.assertEqual(
            arranged.elts[0][0].elts[2][0], TransformUtil.Path.empty().append_block("A").append_block("R2")
        )
        self.assertAlmostEqual(arranged.elts[0][0].elts[2][1][0], 12.78, places=2)
        self.assertAlmostEqual(arranged.elts[0][0].elts[2][1][1], 3.19, places=2)

        self.assertAlmostEqual(arranged.elts[1][1][0], 0, places=2)
        self.assertAlmostEqual(arranged.elts[1][1][1], 13.3, places=2)
        assert isinstance(arranged.elts[1][0], PlacedBlock)
        self.assertEqual(
            arranged.elts[1][0].elts[0][0], TransformUtil.Path.empty().append_block("B").append_block("R3")
        )
        self.assertAlmostEqual(arranged.elts[1][0].elts[0][1][0], 1.48, places=2)
        self.assertAlmostEqual(arranged.elts[1][0].elts[0][1][1], 0.73, places=2)

        flattened = flatten_packed_block(arranged)
        self.assertAlmostEqual(
            flattened[TransformUtil.Path.empty().append_block("A").append_block("U1")][0], 5.15, places=2
        )
        self.assertAlmostEqual(
            flattened[TransformUtil.Path.empty().append_block("A").append_block("U1")][1], 5.15, places=2
        )
        self.assertAlmostEqual(
            flattened[TransformUtil.Path.empty().append_block("A").append_block("R1")][0], 12.78, places=2
        )
        self.assertAlmostEqual(
            flattened[TransformUtil.Path.empty().append_block("A").append_block("R1")][1], 0.73, places=2
        )
        self.assertAlmostEqual(
            flattened[TransformUtil.Path.empty().append_block("B").append_block("R3")][0], 1.48, places=2
        )
        self.assertAlmostEqual(
            flattened[TransformUtil.Path.empty().append_block("B").append_block("R3")][1], 14.03, places=2
        )

    def test_placement_bbox(self) -> None:
        r1 = NetBlock(
            footprint="Resistor_SMD:R_0603_1608Metric",
            refdes="R1",
            part="",
            value="",
            full_path=TransformUtil.Path.empty().append_block("R1"),
            path=[],
            class_path=[],
        )
        r2 = NetBlock(
            footprint="Resistor_SMD:R_0603_1608Metric",
            refdes="R2",
            part="",
            value="",
            full_path=TransformUtil.Path.empty().append_block("R2"),
            path=[],
            class_path=[],
        )
        arranged = arrange_blocks(
            [r1, r2], [BlackBoxBlock(TransformUtil.Path.empty().append_block("box"), (-5, -5, 5, 5))]
        )
        self.assertEqual(arranged.elts[0][0], TransformUtil.Path.empty().append_block("box"))
        self.assertAlmostEqual(arranged.elts[0][1][0], 5, places=2)
        self.assertAlmostEqual(arranged.elts[0][1][1], 5, places=2)
        self.assertEqual(arranged.elts[1][0], TransformUtil.Path.empty().append_block("R1"))
        self.assertAlmostEqual(arranged.elts[1][1][0], 12.48, places=2)
        self.assertAlmostEqual(arranged.elts[1][1][1], 0.73, places=2)
        self.assertEqual(arranged.elts[2][0], TransformUtil.Path.empty().append_block("R2"))
        self.assertAlmostEqual(arranged.elts[2][1][0], 12.48, places=2)
        self.assertAlmostEqual(arranged.elts[2][1][1], 3.19, places=2)
