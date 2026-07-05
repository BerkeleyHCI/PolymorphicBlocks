import warnings
from abc import abstractmethod
from typing import Optional, Union, Any

from typing_extensions import override

from ..electronics_model import *
from .PartsTable import PartsTable, PartsTableColumn, PartsTableRow
from .StandardFootprint import HasStandardFootprint


class PartsTableBase:
    """A base class defining infrastructure for building a (cached) parts table.
    Subclasses should implement _make_table, which returns the underlying parts table.
    Additional filtering can be done by the generator."""

    _TABLE: Optional[PartsTable] = None

    # These need to be implemented by the part table
    PART_NUMBER_COL: Union[str, PartsTableColumn[str]]
    MANUFACTURER_COL: Union[str, PartsTableColumn[str]]
    DESCRIPTION_COL: Union[str, PartsTableColumn[str]]
    DATASHEET_COL: Union[str, PartsTableColumn[str]]

    @classmethod
    @abstractmethod
    def _make_table(cls) -> PartsTable:
        """Returns a parts table for this device. Implement me."""
        ...

    @classmethod
    def _get_table(cls) -> PartsTable:
        if cls._TABLE is None:
            cls._TABLE = cls._make_table()
            if len(cls._TABLE) == 0:
                raise ValueError(f"{cls.__name__} _make_table returned empty table")
        return cls._TABLE


@abstract_block
class PartsTablePart(Block):
    """An interface mixin for a part that is selected from a table, defining parameters to allow manual part selection
    as well as matching parts."""

    def __init__(
        self,
        *args: Any,
        part: StringLike = "",
        excluded_parts: ArrayStringLike = [],
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.part = self.ArgParameter(part)
        self.excluded_parts = self.ArgParameter(excluded_parts)
        self.actual_part = self.Parameter(StringExpr())
        self.matching_parts = self.Parameter(ArrayStringExpr())


@non_library
class PartsTableSelector(PartsTablePart, GeneratorBlock, PartsTableBase):
    """PartsTablePart that includes the parts selection framework logic.
    Subclasses only need to extend _row_filter and _row_generate with part-specific logic."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.generator_param(self.part)
        self.generator_param(self.excluded_parts)

    def _row_filter(self, row: PartsTableRow) -> bool:
        """Returns whether the candidate row satisfies the requirements (should be kept).
        Only called within generate(), so has access to GeneratorParam.get().
        Subclasses should chain this by and-ing with a super() call."""
        part = self.get(self.part)
        excluded_parts = self.get(self.excluded_parts)
        return ((not part) or (row[self.PART_NUMBER_COL] == part)) and (
            (not excluded_parts) or (row[self.PART_NUMBER_COL] not in excluded_parts)
        )

    def _table_postprocess(self, table: PartsTable) -> PartsTable:
        """Optional postprocessing step that takes a table and returns a transformed table.
        Only called within generate(), so has access to GeneratorParam.get().
        Subclasses should chain with the results of a super() call."""
        return table

    @classmethod
    def _row_sort_by(cls, row: PartsTableRow) -> Any:
        """Defines an optional sorting key for rows of this parts table."""
        return []

    def _row_generate(self, row: PartsTableRow) -> None:
        """Once a row is selected, this is called to generate the implementation given the part selection.
        Subclasses super chain this with a super() call.
        If there is no matching row, this is not called."""
        self.assign(self.actual_part, row[self.PART_NUMBER_COL])

    @override
    def generate(self) -> None:
        super().generate()

        matching_table = self._get_table().filter(lambda row: self._row_filter(row))
        postprocessed_table = self._table_postprocess(matching_table)
        postprocessed_table = postprocessed_table.sort_by(self._row_sort_by)
        self.assign(self.matching_parts, postprocessed_table.map(lambda row: row[self.PART_NUMBER_COL]))
        assert len(postprocessed_table) > 0, "no matching part"  # crash to make generator failures more obvious
        selected_row = postprocessed_table.first()
        self._row_generate(selected_row)


@abstract_block
class SelectorFootprint(PartsTablePart):
    """Mixin that allows a specified footprint, for Blocks that automatically select a part."""

    def __init__(
        self, *args: Any, filter_footprints: ArrayStringLike = [], footprint_spec: StringLike = "", **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)
        self.filter_footprints = self.ArgParameter(filter_footprints)  # actual_footprint left to the actual footprint
        self.footprint_spec = self.ArgParameter(footprint_spec)  # deprecated, named because self.footprint taken


@non_library
class PartsTableFootprintFilter(PartsTableSelector, SelectorFootprint):
    """A combination of PartsTableSelector with SelectorFootprint, with row filtering on filter_footprints.
    Does not create the footprint itself, this can be used as a base class where footprint filtering is desired
    but an internal block is created instead."""

    KICAD_FOOTPRINT = PartsTableColumn(str)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.generator_param(self.filter_footprints, self.footprint_spec)

    @override
    def generate(self) -> None:
        super().generate()
        if self.get(self.footprint_spec):
            warnings.warn(f"footprint_spec replaced with filter_footprints taking an array", DeprecationWarning)

    @override
    def _row_filter(self, row: PartsTableRow) -> bool:
        filter_footprints = self.get(self.filter_footprints)
        if self.get(self.footprint_spec):
            filter_footprints.append(self.get(self.footprint_spec))
        return super()._row_filter(row) and ((not filter_footprints or row[self.KICAD_FOOTPRINT] in filter_footprints))


@non_library
class PartsTableSelectorFootprint(PartsTableFootprintFilter, FootprintBlock, HasStandardFootprint):
    """PartsTableFootprintFilter, but also with footprint creation. Must define a standard pinning."""

    @override
    def _row_generate(self, row: PartsTableRow) -> None:
        super()._row_generate(row)
        self.footprint(
            self._standard_footprint().REFDES_PREFIX,
            row[self.KICAD_FOOTPRINT],
            self._standard_footprint()._make_pinning(self, row[self.KICAD_FOOTPRINT]),
            mfr=row[self.MANUFACTURER_COL],
            part=row[self.PART_NUMBER_COL],
            value=row[self.DESCRIPTION_COL],
            datasheet=row[self.DATASHEET_COL],
        )
