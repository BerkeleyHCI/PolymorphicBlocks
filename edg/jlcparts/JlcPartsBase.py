from typing import Any, Optional, Dict, List

from pydantic import BaseModel, RootModel, Field
import gzip
import os

from ..abstract_parts import *
from ..parts import JlcPart

kCrystalsTableFilename = "CrystalsakaOscillatorsakaResonatorsCrystals.json.gz"

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

class JlcPartsAttributeEntry(BaseModel):
    # format: Optional[str] = None  # unused, no idea why this exists
    # primary: Optional[str] = None  # unused, no idea why this exists
    values: dict[str, tuple[Any, str]]

class JlcPartsAttributes(RootModel):
    root: dict[str, JlcPartsAttributeEntry]


class JlcPartsBase(JlcPart, PartsTableFootprint, PartsTableBase):
    """Base class parsing parts from https://github.com/yaqwsx/jlcparts"""
    _parts_root_dir: Optional[str] = None

    # overrides from PartsTableBase
    PART_NUMBER_COL = PartsTableColumn(str)
    MANUFACTURER_COL = PartsTableColumn(str)
    DESCRIPTION_COL = PartsTableColumn(str)
    DATASHEET_COL = PartsTableColumn(str)

    # new columns here
    _kColLcsc = PartsTableColumn(str)

    @staticmethod
    def configure_root_dir(root_dir: str):
        """Configures the root dir that contains the data files from jlcparts, eg
        CapacitorsMultilayer_Ceramic_Capacitors_MLCC___SMDakaSMT.json.gz"""
        assert JlcPartsBase._parts_root_dir is None, \
            f"attempted to reassign configure_root_dir, was {JlcPartsBase._parts_root_dir}, new {root_dir}"
        JlcPartsBase._parts_root_dir = root_dir

    _kFileName: str  # set by subclass
    _cached_table: Optional[PartsTable] = None  # set on a per-class basis

    @classmethod
    def _jlc_table(cls) -> PartsTable:
        """Return the table, cached if possible"""
        if cls._cached_table is None:
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
        assert cls._parts_root_dir is not None, "must configure_root_dir with jlcparts data folder"
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
            row_dict[cls.PART_NUMBER_COL] = component[partNumberIndex]
            row_dict[cls.DESCRIPTION_COL] = component[descriptionIndex]
            row_dict[cls.DATASHEET_COL] = component[datasheetIndex]
            row_dict[cls._kColLcsc] = component[lcscIndex]

            attributes = JlcPartsAttributes(**component[attributesIndex])
            row_dict[cls.MANUFACTURER_COL] = list(attributes.root[kAttributeManufacturer].values.values())[0][0]
            package = list(attributes.root[kAttributePackage].values.values())[0][0]

            row_dict_opt = cls._entry_to_table_row(row_dict, package, attributes)
            if row_dict_opt is not None:
                rows.append(PartsTableRow(row_dict_opt))

        return PartsTable(rows)

