from typing import Any, Tuple, Optional, Dict, List

from pydantic import BaseModel, RootModel, Field
import gzip
import os

from ..abstract_parts import *
from ..parts import JlcPart

kCrystalsTableFilename = "CrystalsakaOscillatorsakaResonatorsCrystals.json.gz"
kMlccTableFilename = "CapacitorsMultilayer_Ceramic_Capacitors_MLCC___SMDakaSMT.json.gz"

kSchemaLcsc = "lcsc"  # JLC part number
kSchemaPartNumber = "mfr"  # manufacturer part name
kSchemaDatasheet = "datasheet"  # URL
kSchemaDescription = "description"
kSchemaAttributes = "attributes"  # attribute table

# common attributes across categories
kAttributeManufacturer = "Manufacturer"
kAttributePackage = "Package"

class JlcPartsFile(BaseModel):
    category: str
    components: list[list[Any]]  # index-matched with schema
    jlcpart_schema: list[str] = Field(..., alias='schema')

class JlcPartsValue(BaseModel):
    default: Tuple[Any, str]  # value, type / units

class JlcPartsAttributeEntry(BaseModel):
    format: str
    primary: str
    values: JlcPartsValue

class JlcPartsAttributes(RootModel):
    root: dict[str, JlcPartsAttributeEntry]


class JlcPartsBase(JlcPart, PartsTableBase):
    """Base class parsing parts from https://github.com/yaqwsx/jlcparts"""
    _parts_root_dir: Optional[str] = None

    @staticmethod
    def configure_root_dir(root_dir: str):
        """Configures the root dir that contains the data files from jlcparts, eg
        CapacitorsMultilayer_Ceramic_Capacitors_MLCC___SMDakaSMT.json.gz"""
        assert JlcPartsBase.parts_root_dir is None, \
            f"attempted to reassign configure_root_dir, was {JlcPartsBase.parts_root_dir}, new {root_dir}"
        JlcPartsBase.parts_root_dir = root_dir

    _kFileName: str  # set by subclass
    _cached_table: Optional[PartsTable] = None  # set on a per-class basis

    @classmethod
    def _jlc_table(cls) -> PartsTable:
        """Return the table, cached if possible"""
        if cls._cached_table is not None:
            cls._cached_table = cls._parse_table()
        return cls._cached_table

    @classmethod
    def _entry_to_table_row(cls, row_dict: Dict[PartsTableColumn, Any], package: str, attributes: JlcPartsAttributes)\
            -> Optional[Dict[PartsTableColumn, Any]]:
        """Given an entry from jlcparts and row pre-populated with metadata, adds category-specific data to the row
        (in-place), and returns the row (or None, if it failed to parse and the row should be discarded)."""
        raise NotImplementedError

    @classmethod
    def _parse_table(cls) -> PartsTable:
        """Parses the file to a PartsTable"""
        with gzip.open(os.path.join(cls._parts_root_dir, cls._kFileName), 'r') as f:
            data = JlcPartsFile.model_validate_json(f.read())
        rows: List[PartsTableRow] = []
        lcscIndex = data.jlcpart_schema.index(kSchemaLcsc)
        partNumberIndex = data.jlcpart_schema.index(kSchemaPartNumber)
        descriptionIndex = data.jlcpart_schema.index(kSchemaDescription)
        datasheetIndex = data.jlcpart_schema.index(kSchemaDatasheet)
        attributesIndex = data.jlcpart_schema.index(kSchemaAttributes)
        for component in data.components:
            row_dict: Dict[PartsTableColumn, Any] = {}
            row_dict[PartsTableBase.PART_NUMBER_COL] = component[partNumberIndex]
            row_dict[PartsTableBase.DESCRIPTION_COL] = component[descriptionIndex]
            row_dict[PartsTableBase.DATASHEET_COL] = component[datasheetIndex]

            attributes = JlcPartsAttributes(**component[attributesIndex])
            row_dict[PartsTableBase.MANUFACTURER_COL] = attributes.root[kAttributeManufacturer].values[0][0]
            package = attributes.root[kAttributePackage].values[0][0]

            row_dict_opt = cls._entry_to_table_row(row_dict, package, attributes)
            if row_dict_opt is not None:
                rows.append(PartsTableRow(row_dict_opt))

        return PartsTable(rows)


if __name__ == "__main__":
    JlcPartsBase.configure_root_dir("../../../../jlcparts/web/public/data/")
