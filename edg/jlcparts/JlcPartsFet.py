from typing import Any, Optional, Dict
from ..abstract_parts import *
from ..parts.JlcFet import JlcFet
from .JlcPartsBase import JlcPartsBase, JlcPartsAttributes


class JlcPartsBaseFet(JlcPartsBase, BaseTableFet):
    _JLC_PARTS_FILE_NAMES = ["TransistorsMOSFETs"]
    _CHANNEL_MAP = {
        'N Channel': 'N',
        'P Channel': 'P',
    }

    @classmethod
    def _entry_to_table_row(cls, row_dict: Dict[PartsTableColumn, Any], filename: str, package: str, attributes: JlcPartsAttributes) \
            -> Optional[Dict[PartsTableColumn, Any]]:
        try:
            row_dict[cls.KICAD_FOOTPRINT] = JlcFet.PACKAGE_FOOTPRINT_MAP[package]

            row_dict[cls.CHANNEL] = cls._CHANNEL_MAP[attributes.get("Type", str)]
            row_dict[cls.VDS_RATING] = Range.zero_to_upper(
                attributes.get("Drain source voltage (vdss)", float, sub='voltage'))
            row_dict[cls.IDS_RATING] = Range.zero_to_upper(PartParserUtil.parse_value(
                attributes.get("Continuous drain current (id)", str), 'A'))

            # used as a proxy for lower bound for Vgs,max
            vgs_for_ids = attributes.get("Drain source on resistance (rds(on)@vgs,id)", float, sub='Vgs')
            row_dict[cls.VGS_RATING] = Range.from_abs_tolerance(0, vgs_for_ids)  # bidirectional rating

            row_dict[cls.VGS_DRIVE] = Range(
                attributes.get("Gate threshold voltage (vgs(th)@id)", float, sub='Vgs'),
                vgs_for_ids)
            row_dict[cls.RDS_ON] = Range.exact(
                attributes.get("Drain source on resistance (rds(on)@vgs,id)", float, sub='Rds'))
            row_dict[cls.POWER_RATING] = Range.zero_to_upper(
                attributes.get("Power dissipation (pd)", float, sub='power'))

            try:
                input_capacitance: Optional[float] = attributes.get("Input capacitance (ciss@vds)", float, sub='capacity')
            except (KeyError, TypeError):
                input_capacitance = None
            try:  # not specified for most parts apparently
                gate_charge = attributes.get("Total gate charge (qg@vgs)", float, sub='charge')
            except (KeyError, TypeError):
                if input_capacitance is not None:  # not strictly correct but kind of a guesstimate
                    gate_charge = input_capacitance * vgs_for_ids
                else:
                    gate_charge = 3000e-9  # very pessimistic upper bound
            row_dict[cls.GATE_CHARGE] = Range.exact(gate_charge)

            return row_dict
        except (KeyError, TypeError, PartParserUtil.ParseError):
            return None


class JlcPartsFet(PartsTableSelectorFootprint, JlcPartsBaseFet, TableFet):
    pass


class JlcPartsSwitchFet(PartsTableSelectorFootprint, JlcPartsBaseFet, TableSwitchFet):
    @init_in_parent
    def __init__(self, *args, manual_gate_charge: RangeLike = RangeExpr.ZERO, **kwargs):
        super().__init__(*args, **kwargs)
        # allow the user to specify a gate charge
        self.manual_gate_charge = self.ArgParameter(manual_gate_charge)
        self.generator_param(self.manual_gate_charge)

    def _table_postprocess(self, table: PartsTable) -> PartsTable:
        manual_gate_charge = self.get(self.manual_gate_charge)
        def process_row(row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
            return {self.GATE_CHARGE: manual_gate_charge}

        # must run before TableFet power calculations
        if not manual_gate_charge == Range.exact(0):
            table = table.map_new_columns(process_row, overwrite=True)

        return super()._table_postprocess(table)


lambda: JlcPartsFet(), JlcPartsSwitchFet()  # ensure class is instantiable (non-abstract)
