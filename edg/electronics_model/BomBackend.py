import io
from typing import List, Tuple, Dict, NamedTuple, Optional

from typing_extensions import override

from .. import edgir
from ..core import BaseBackend, CompiledDesign, TransformUtil

import csv


class BomItem(NamedTuple):
    footprint: str
    value: str
    jlc_number: str
    manufacturer: str
    part: str
    pnp_rot: Optional[float]
    pnp_offset: Optional[Tuple[float, float]]


class GenerateBom(BaseBackend):  # creates and populates .csv file
    @override
    def run(self, design: CompiledDesign, args: Dict[str, str] = {}) -> List[Tuple[edgir.LocalPath, str]]:
        assert not args
        bom_list = BomTransform(design).run()

        bom_string = io.StringIO()
        csv_data = [
            "Id",
            "Designator",
            "Footprint",
            "Quantity",
            "Designation",
            "Supplier and Ref",
            "JLCPCB Part #",
            "Manufacturer",
            "Part",
            "PNP Rotation Offset",
            "PNP Offset X",
            "PNP Offset Y",
        ]  # populates headers
        writer = csv.writer(bom_string, lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
        writer.writerow(csv_data)
        for index, (key, value) in enumerate(bom_list.items(), 1):  # populates the rest of the rows
            csv_data = [
                str(index),
                ",".join(bom_list[key]),
                key.footprint,
                str(len(bom_list[key])),
                key.value,
                "",
                key.jlc_number,
                key.manufacturer,
                key.part,
                str(key.pnp_rot) if key.pnp_rot is not None else "",
                str(key.pnp_offset[0]) if key.pnp_offset is not None else "",
                str(key.pnp_offset[1]) if key.pnp_offset is not None else "",
            ]
            writer.writerow(csv_data)

        return [(edgir.LocalPath(), bom_string.getvalue())]


class BomTransform(TransformUtil.Transform):
    def __init__(self, design: CompiledDesign):
        self.design = design
        self.bom_list: Dict[BomItem, List[str]] = {}  # BomItem -> list of refdes

    @override
    def visit_block(self, context: TransformUtil.TransformContext, block: edgir.BlockTypes) -> None:
        footprint = self.design.get_value(context.path.to_tuple() + ("fp_footprint",))
        refdes = self.design.get_value(context.path.to_tuple() + ("fp_refdes",))
        if footprint is not None and refdes is not None:
            value = self.design.get_value(context.path.to_tuple() + ("fp_value",)) or ""
            jlc_number = self.design.get_value(context.path.to_tuple() + ("lcsc_part",)) or ""
            manufacturer = self.design.get_value(context.path.to_tuple() + ("fp_mfr",)) or ""
            part = self.design.get_value(context.path.to_tuple() + ("fp_part",)) or ""
            pnp_rot = self.design.get_value(context.path.to_tuple() + ("fp_pnp_rot",))
            pnp_offset_x = self.design.get_value(context.path.to_tuple() + ("fp_pnp_offset_x",))
            pnp_offset_y = self.design.get_value(context.path.to_tuple() + ("fp_pnp_offset_y",))
            assert (
                isinstance(footprint, str)
                and isinstance(refdes, str)
                and isinstance(jlc_number, str)
                and isinstance(value, str)
                and isinstance(manufacturer, str)
                and isinstance(part, str)
                and isinstance(pnp_rot, (float, type(None)))
                and isinstance(pnp_offset_x, (float, type(None)))
                and isinstance(pnp_offset_y, (float, type(None)))
            )
            bom_item = BomItem(
                footprint=footprint,
                value=value,
                jlc_number=jlc_number,
                manufacturer=manufacturer,
                part=part,
                pnp_rot=pnp_rot,
                pnp_offset=(
                    (pnp_offset_x, pnp_offset_y) if pnp_offset_x is not None and pnp_offset_y is not None else None
                ),
            )
            self.bom_list.setdefault(bom_item, []).append(refdes)

    def run(self) -> Dict[BomItem, List[str]]:
        self.transform_design(self.design.design)
        return self.bom_list
