from typing import Any, Optional, Dict
from ..abstract_parts import *
from ..parts.JlcInductor import JlcInductor
from .JlcPartsBase import JlcPartsBase, JlcPartsAttributes


class JlcPartsInductor(PartsTableSelectorFootprint, JlcPartsBase, TableInductor):
    _JLC_PARTS_FILE_NAMES = [
        "InductorsakaCoilsakaTransformersPower_Inductors",
        "InductorsakaCoilsakaTransformersInductors__SMD_",
        "Inductors__Coils__ChokesPower_Inductors",
        "Inductors__Coils__ChokesInductors__SMD_",
    ]

    @classmethod
    def _entry_to_table_row(cls, row_dict: Dict[PartsTableColumn, Any], filename: str, package: str, attributes: JlcPartsAttributes) \
            -> Optional[Dict[PartsTableColumn, Any]]:
        try:
            # some standard sizes eg 0603 can be parsed from the package
            footprint = JlcInductor.PACKAGE_FOOTPRINT_MAP.get(package, None)
            if footprint is None:
                footprint_cols = JlcInductor.parse_full_description(row_dict[cls.PART_NUMBER_COL], JlcInductor.PART_FOOTPRINT_PARSERS)
                if footprint_cols is not None:
                    footprint = footprint_cols[cls.KICAD_FOOTPRINT]
                else:
                    return None
            row_dict[cls.KICAD_FOOTPRINT] = footprint

            row_dict[cls.INDUCTANCE] = PartParserUtil.parse_abs_tolerance(
                attributes.get("Tolerance", str), attributes.get("Inductance", float, sub='inductance'), '')
            row_dict[cls.CURRENT_RATING] = Range.zero_to_upper(
                attributes.get("Rated current", float, 0, sub='current'))
            row_dict[cls.DC_RESISTANCE] = Range.exact(attributes.get("Dc resistance", float, 0, sub='resistance'))
            row_dict[cls.FREQUENCY_RATING] = Range.all()  # TODO ignored for now

            return row_dict
        except (KeyError, TypeError, PartParserUtil.ParseError):
            return None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # because the table does not have frequency specs, the table filter can't enforce frequency ratings
        # so the user must add the actual frequency rating in refinements
        self.manual_frequency_rating = self.Parameter(RangeExpr(Range.exact(0)))
        self.require(self.frequency.within(self.manual_frequency_rating))


lambda: JlcPartsInductor()  # ensure class is instantiable (non-abstract)
