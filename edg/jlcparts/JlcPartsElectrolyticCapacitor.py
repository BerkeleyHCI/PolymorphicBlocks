from typing import Any, Optional, Dict
import re
from ..abstract_parts import *
from .JlcPartsBase import JlcPartsBase, JlcPartsAttributes


class JlcPartsElectrolyticCapacitor(TableCapacitor, AluminumCapacitor, JlcPartsBase):
    _JLC_PARTS_FILE_NAMES = ["CapacitorsAluminum_Electrolytic_Capacitors___SMD"]
    _PACKAGE_PARSER = re.compile(r"^SMD,D([\d.]+)xL([\d.]+)mm$")

    @classmethod
    def _entry_to_table_row(cls, row_dict: Dict[PartsTableColumn, Any], filename: str, package: str, attributes: JlcPartsAttributes) \
            -> Optional[Dict[PartsTableColumn, Any]]:

        match = cls._PACKAGE_PARSER.match(package)
        if match is None:
            return None
        row_dict[cls.KICAD_FOOTPRINT] = f"Capacitor_SMD:CP_Elec_{match.group(1)}x{match.group(2)}",

        try:
            nominal_capacitance = attributes.get("Capacitance", float, sub='capacitance')
            row_dict[cls.CAPACITANCE] = PartParserUtil.parse_abs_tolerance(
                attributes.get("Tolerance", str), nominal_capacitance, '')
            row_dict[cls.NOMINAL_CAPACITANCE] = nominal_capacitance
            row_dict[cls.VOLTAGE_RATING] = Range.zero_to_upper(
                attributes.get("Allowable voltage", float, sub='voltage'))

            return row_dict
        except (KeyError, TypeError, PartParserUtil.ParseError):
            return None


lambda: JlcPartsElectrolyticCapacitor()  # ensure class is instantiable (non-abstract)
