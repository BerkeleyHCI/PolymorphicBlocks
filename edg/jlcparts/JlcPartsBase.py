from typing import Any, Optional, Dict, List, TypeVar, Type

from pydantic import BaseModel, RootModel, Field
import gzip
import os

from ..abstract_parts import *
from ..parts import JlcPart

kTableFilenamePostfix = ".json.gz"
kStockFilenamePostfix = ".stock.json"

kSchemaLcsc = "lcsc"  # JLC part number
kSchemaPartNumber = "mfr"  # manufacturer part name
kSchemaDatasheet = "datasheet"  # URL
kSchemaDescription = "description"
kSchemaAttributes = "attributes"  # attribute table

# common attributes across categories
kAttributeManufacturer = "Manufacturer"
kAttributePackage = "Package"
kAttributeStatus = "Status"  # stocking status
kAttributeBasicType = "Basic/Extended"
kAttributeBasicTypeBasic = "Basic"
kAttributeStatusFilters = ["Discontinued"]  # parts with these statuses are filtered out

class JlcPartsFile(BaseModel):
    category: str
    components: list[list[Any]]  # index-matched with schema
    jlcpart_schema: list[str] = Field(..., alias='schema')

class JlcPartsAttributeEntry(BaseModel):
    # format: Optional[str] = None  # unused, no idea why this exists
    # primary: Optional[str] = None  # unused, no idea why this exists
    values: dict[str, tuple[Any, str]]

ParsedType = TypeVar('ParsedType')  # can't be inside the class or it gets confused as a pydantic model entry

class JlcPartsAttributes(RootModel):
    root: dict[str, JlcPartsAttributeEntry]

    def get(self, key: str, expected_type: Type[ParsedType], default: Optional[ParsedType] = None) -> ParsedType:
        """Utility function that gets an attribute of the specified name, checking that it is the expected type
        or returning some default (if specified)."""
        if key not in self.root:
            if default is not None:
                return default
            else:
                raise KeyError
        entry_dict = self.root[key].values
        assert len(entry_dict) == 1
        value = next(iter(entry_dict.values()))[0]
        if not isinstance(value, expected_type):
            if default is not None:
                return default
            else:
                raise TypeError
        return value


class JlcPartsStockFile(RootModel):
    root: dict[str, int]  # LCSC to stock level


class JlcPartsBase(JlcPart, PartsTableSelector, PartsTableFootprint):
    """Base class parsing parts from https://github.com/yaqwsx/jlcparts"""
    _config_parts_root_dir: Optional[str] = None
    _config_min_stock: int = 1000

    # overrides from PartsTableBase
    PART_NUMBER_COL = PartsTableColumn(str)
    MANUFACTURER_COL = PartsTableColumn(str)
    DESCRIPTION_COL = PartsTableColumn(str)
    DATASHEET_COL = PartsTableColumn(str)

    # new columns here
    LCSC_COL = PartsTableColumn(str)
    BASIC_PART_COLL = PartsTableColumn(bool)

    @staticmethod
    def config_root_dir(root_dir: str):
        """Configures the root dir that contains the data files from jlcparts, eg
        CapacitorsMultilayer_Ceramic_Capacitors_MLCC___SMDakaSMT.json.gz
        This setting is on a JlcPartsBase-wide basis."""
        assert JlcPartsBase._config_parts_root_dir is None, \
            f"attempted to reassign configure_root_dir, was {JlcPartsBase._config_parts_root_dir}, new {root_dir}"
        JlcPartsBase._config_parts_root_dir = root_dir

    _JLC_PARTS_FILE_NAME: str  # set by subclass
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
        assert cls._config_parts_root_dir is not None, "must configure_root_dir with jlcparts data folder"
        with gzip.open(os.path.join(cls._config_parts_root_dir, cls._JLC_PARTS_FILE_NAME + kTableFilenamePostfix), 'r') as f:
            data = JlcPartsFile.model_validate_json(f.read())
        with open(os.path.join(cls._config_parts_root_dir, cls._JLC_PARTS_FILE_NAME + kStockFilenamePostfix), 'r') as f:
            stocking = JlcPartsStockFile.model_validate_json(f.read())

        lcsc_index = data.jlcpart_schema.index(kSchemaLcsc)
        part_number_index = data.jlcpart_schema.index(kSchemaPartNumber)
        description_index = data.jlcpart_schema.index(kSchemaDescription)
        datasheet_index = data.jlcpart_schema.index(kSchemaDatasheet)
        attributes_index = data.jlcpart_schema.index(kSchemaAttributes)

        rows: List[PartsTableRow] = []
        for component in data.components:
            row_dict: Dict[PartsTableColumn, Any] = {}

            row_dict[cls.LCSC_COL] = lcsc = component[lcsc_index]
            if stocking.root.get(lcsc, 0) < cls._config_min_stock:
                continue

            row_dict[cls.PART_NUMBER_COL] = component[part_number_index]
            row_dict[cls.DESCRIPTION_COL] = component[description_index]
            row_dict[cls.DATASHEET_COL] = component[datasheet_index]

            attributes = JlcPartsAttributes(**component[attributes_index])
            status = attributes.get(kAttributeStatus, str)
            if status in kAttributeStatusFilters:
                continue
            basic_extended = attributes.get(kAttributeBasicType, str)
            row_dict[cls.BASIC_PART_COLL] = basic_extended == kAttributeBasicTypeBasic

            row_dict[cls.MANUFACTURER_COL] = attributes.get(kAttributeManufacturer, str)
            package = attributes.get(kAttributePackage, str)

            row_dict_opt = cls._entry_to_table_row(row_dict, package, attributes)
            if row_dict_opt is not None:
                rows.append(PartsTableRow(row_dict_opt))

        return PartsTable(rows)

    @classmethod
    def _row_sort_by(cls, row: PartsTableRow) -> Any:
        return [row[cls.BASIC_PART_COLL], row[cls.KICAD_FOOTPRINT]]

    def _row_generate(self, row: PartsTableRow) -> None:
        super()._row_generate(row)
        self.assign(self.lcsc_part, row[self.LCSC_COL])
        self.assign(self.actual_basic_part, row[self.BASIC_PART_COLL])
