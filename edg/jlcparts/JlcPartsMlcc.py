from typing import Any, Optional, Dict
from ..abstract_parts import *
from ..parts.JlcCapacitor import JlcCapacitor, JlcDummyCapacitor
from .JlcPartsBase import JlcPartsBase, JlcPartsAttributes


class JlcPartsMlcc(TableDeratingCapacitor, CeramicCapacitor, PartsTableSelectorFootprint, JlcPartsBase):
    _JLC_PARTS_FILE_NAMES = ["CapacitorsMultilayer_Ceramic_Capacitors_MLCC___SMDakaSMT"]

    @init_in_parent
    def __init__(self, *args, capacitance_minimum_size: BoolLike = True, **kwargs):
        super().__init__(*args, **kwargs)
        self.capacitance_minimum_size = self.ArgParameter(capacitance_minimum_size)
        self.generator_param(self.capacitance_minimum_size)

    @classmethod
    def _entry_to_table_row(cls, row_dict: Dict[PartsTableColumn, Any], filename: str, package: str, attributes: JlcPartsAttributes) \
            -> Optional[Dict[PartsTableColumn, Any]]:
        try:
            footprint = JlcCapacitor.PACKAGE_FOOTPRINT_MAP[package]
            row_dict[cls.KICAD_FOOTPRINT] = footprint

            nominal_capacitance = attributes.get("Capacitance", float, sub='capacitance')
            # note, tolerance not specified for many devices
            row_dict[cls.CAPACITANCE] = PartParserUtil.parse_abs_tolerance(
                attributes.get("Tolerance", str), nominal_capacitance, '')
            row_dict[cls.NOMINAL_CAPACITANCE] = nominal_capacitance
            row_dict[cls.VOLTAGE_RATING] = Range.from_abs_tolerance(  # voltage rating for ceramic caps is bidirectional
                0, attributes.get("Allowable voltage", float, 0, sub='voltage'))
            row_dict[cls.VOLTCO] = JlcCapacitor.DERATE_VOLTCO_MAP[footprint]

            # arbitrary filter - TODO parameterization
            tempco = attributes.get("Temperature coefficient", str)
            if len(tempco) < 3 or tempco[0] not in ('X', 'C', 'N') or tempco[2] not in ('R', 'S', 'G', '0'):
                return None

            return row_dict
        except (KeyError, TypeError, PartParserUtil.ParseError):
            return None

    def _table_postprocess(self, table: PartsTable) -> PartsTable:
        # TODO deduplicate w/ JlcCapacitor
        def filter_minimum_size(row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
            # enforce minimum packages, note the cutoffs are exclusive
            nominal_capacitance = row[self.NOMINAL_CAPACITANCE]
            footprint = row[self.KICAD_FOOTPRINT]
            if nominal_capacitance > 10e-6 and footprint not in [
                'Capacitor_SMD:C_1206_3216Metric',
            ]:
                return None
            elif nominal_capacitance > 1e-6 and footprint not in [
                'Capacitor_SMD:C_0805_2012Metric',
                'Capacitor_SMD:C_1206_3216Metric',
            ]:
                return None
            return {}
        table = super()._table_postprocess(table)
        if self.get(self.capacitance_minimum_size):
            table = table.map_new_columns(filter_minimum_size)
        return table

    @classmethod
    def _row_sort_by(cls, row: PartsTableRow) -> Any:
        return [row[cls.PARALLEL_COUNT], super(JlcPartsMlcc, cls)._row_sort_by(row)]

    def _make_parallel_footprints(self, row: PartsTableRow) -> None:
        cap_model = JlcDummyCapacitor(set_lcsc_part=row[self.LCSC_COL],
                                      set_basic_part=row[self.BASIC_PART_COL],
                                      footprint=row[self.KICAD_FOOTPRINT],
                                      manufacturer=row[self.MANUFACTURER_COL], part_number=row[self.PART_NUMBER_COL],
                                      value=row[self.DESCRIPTION_COL],
                                      capacitance=row[self.NOMINAL_CAPACITANCE],
                                      voltage=self.voltage)
        self.c = ElementDict[JlcDummyCapacitor]()
        for i in range(row[self.PARALLEL_COUNT]):
            self.c[i] = self.Block(cap_model)
            self.connect(self.c[i].pos, self.pos)
            self.connect(self.c[i].neg, self.neg)

        self.assign(self.lcsc_part, row[self.LCSC_COL])
        self.assign(self.actual_basic_part, row[self.BASIC_PART_COL])


lambda: JlcPartsMlcc()  # ensure class is instantiable (non-abstract)
