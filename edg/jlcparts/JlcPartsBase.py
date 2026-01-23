import sys
from typing import Any, Optional, Dict, List, TypeVar, Type, ClassVar

from pydantic import BaseModel, RootModel, Field
import gzip
import os

from typing_extensions import override

from ..abstract_parts import *
from ..parts.JlcPart import JlcPart

kTableFilenamePostfix = ".json.gz"
kStockFilenamePostfix = ".stock.json"


class JlcPartsFile(BaseModel):
    category: str
    components: list[list[Any]]  # index-matched with schema
    jlcpart_schema: list[str] = Field(..., alias="schema")


class JlcPartsAttributeEntry(BaseModel):
    # format: Optional[str] = None  # unused, no idea why this exists
    # primary: Optional[str] = None  # unused, no idea why this exists
    values: dict[str, tuple[Any, str]]


ParsedType = TypeVar("ParsedType")  # can't be inside the class or it gets confused as a pydantic model entry


class JlcPartsAttributes(RootModel[Dict[str, JlcPartsAttributeEntry]]):
    root: dict[str, JlcPartsAttributeEntry]

    def get(
        self, key: str, expected_type: Type[ParsedType], default: Optional[ParsedType] = None, sub: str = "default"
    ) -> ParsedType:
        """Utility function that gets an attribute of the specified name, checking that it is the expected type
        or returning some default (if specified)."""
        if key not in self.root:
            if default is not None:
                return default
            else:
                raise KeyError
        value = self.root[key].values[sub][0]
        if not isinstance(value, expected_type):
            if default is not None:
                return default
            else:
                raise TypeError
        return value

    def __contains__(self, key: str) -> bool:
        return key in self.root


class JlcPartsPriceEntry(BaseModel):
    price: float
    qFrom: int
    qTo: Optional[int]  # None = top bucket


class JlcPartsPrice(RootModel[List[JlcPartsPriceEntry]]):
    root: list[JlcPartsPriceEntry]

    def for_min_qty(self) -> float:
        min_seen_price = (sys.maxsize, float(sys.maxsize))  # return ridiculously high if not specified

        for bucket in self.root:
            if bucket.qFrom <= 1 or bucket.qFrom is None:  # short circuit for qty=1
                return bucket.price
            if bucket.qFrom < min_seen_price[0]:
                min_seen_price = (bucket.qFrom, bucket.price)
        return min_seen_price[1]


class JlcPartsStockFile(RootModel[Dict[str, int]]):
    root: dict[str, int]  # LCSC to stock level


class JlcPartsBase(JlcPart, PartsTableAreaSelector, PartsTableFootprintFilter):
    """Base class parsing parts from https://github.com/yaqwsx/jlcparts"""

    _config_parts_root_dir: Optional[str] = None
    _config_min_stock: int = 250

    # overrides from PartsTableBase
    PART_NUMBER_COL = PartsTableColumn(str)
    MANUFACTURER_COL = PartsTableColumn(str)
    DESCRIPTION_COL = PartsTableColumn(str)
    DATASHEET_COL = PartsTableColumn(str)

    # new columns here
    LCSC_COL = PartsTableColumn(str)
    BASIC_PART_COL = PartsTableColumn(bool)
    COST_COL = PartsTableColumn(str)

    @staticmethod
    def config_root_dir(root_dir: str) -> None:
        """Configures the root dir that contains the data files from jlcparts, eg
        CapacitorsMultilayer_Ceramic_Capacitors_MLCC___SMDakaSMT.json.gz
        This setting is on a JlcPartsBase-wide basis."""
        assert (
            JlcPartsBase._config_parts_root_dir is None
        ), f"attempted to reassign config_root_dir, was {JlcPartsBase._config_parts_root_dir}, new {root_dir}"
        JlcPartsBase._config_parts_root_dir = root_dir

    _JLC_PARTS_FILE_NAMES: ClassVar[List[str]]  # set by subclass
    _cached_table: Optional[PartsTable] = None  # set on a per-class basis

    @classmethod
    @override
    def _make_table(cls) -> PartsTable:
        """Return the table, cached if possible"""
        if cls._cached_table is None:
            cls._cached_table = cls._parse_table()
        return cls._cached_table

    @classmethod
    def _entry_to_table_row(
        cls, row_dict: Dict[PartsTableColumn, Any], filename: str, package: str, attributes: JlcPartsAttributes
    ) -> Optional[Dict[PartsTableColumn, Any]]:
        """Given an entry from jlcparts and row pre-populated with metadata, adds category-specific data to the row
        (in-place), and returns the row (or None, if it failed to parse and the row should be discarded)."""
        raise NotImplementedError

    @classmethod
    def _parse_table(cls) -> PartsTable:
        """Parses the file to a PartsTable"""
        jlcparts_dir = os.environ.get("JLCPARTS_DIR")
        if jlcparts_dir is None:
            jlcparts_dir = cls._config_parts_root_dir
        assert jlcparts_dir is not None, (
            "no jlcparts data directory specified, either "
            "set JLCPARTS_DIR environment variable or call JlcPartsBase.config_root_dir "
            "with jlcparts data folder"
        )

        rows: List[PartsTableRow] = []

        for filename in cls._JLC_PARTS_FILE_NAMES:
            with gzip.open(os.path.join(jlcparts_dir, filename + kTableFilenamePostfix), "r") as f:
                data = JlcPartsFile.model_validate_json(f.read())
            with open(os.path.join(jlcparts_dir, filename + kStockFilenamePostfix), "r") as f:
                stocking = JlcPartsStockFile.model_validate_json(f.read())

            lcsc_index = data.jlcpart_schema.index("lcsc")
            part_number_index = data.jlcpart_schema.index("mfr")
            description_index = data.jlcpart_schema.index("description")
            datasheet_index = data.jlcpart_schema.index("datasheet")
            attributes_index = data.jlcpart_schema.index("attributes")
            price_index = data.jlcpart_schema.index("price")

            for component in data.components:
                row_dict: Dict[PartsTableColumn, Any] = {}

                row_dict[cls.LCSC_COL] = lcsc = component[lcsc_index]
                if stocking.root.get(lcsc, 0) < cls._config_min_stock:
                    continue

                row_dict[cls.PART_NUMBER_COL] = component[part_number_index]
                row_dict[cls.DESCRIPTION_COL] = component[description_index]
                row_dict[cls.DATASHEET_COL] = component[datasheet_index]
                row_dict[cls.COST_COL] = JlcPartsPrice(component[price_index]).for_min_qty()

                attributes = JlcPartsAttributes(**component[attributes_index])
                row_dict[cls.BASIC_PART_COL] = attributes.get("Basic/Extended", str) == "Basic"
                row_dict[cls.MANUFACTURER_COL] = attributes.get("Manufacturer", str)

                package = attributes.get("Package", str)
                row_dict_opt = cls._entry_to_table_row(row_dict, filename, package, attributes)
                if row_dict_opt is not None:
                    rows.append(PartsTableRow(row_dict_opt))

        return PartsTable(rows)

    @classmethod
    @override
    def _row_sort_by(cls, row: PartsTableRow) -> Any:
        return [not row[cls.BASIC_PART_COL], cls._row_area(row), super()._row_sort_by(row), row[cls.COST_COL]]

    @override
    def _row_generate(self, row: PartsTableRow) -> None:
        super()._row_generate(row)
        self.assign(self.lcsc_part, row[self.LCSC_COL])
        self.assign(self.actual_basic_part, row[self.BASIC_PART_COL])
