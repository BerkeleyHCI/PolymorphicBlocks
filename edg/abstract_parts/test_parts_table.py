import os
import unittest

from typing_extensions import override

from .PartsTable import *


class PartsTableTest(unittest.TestCase):
    INT_COLUMN = PartsTableColumn(int)

    # TODO don't test using internal variables
    @override
    def setUp(self) -> None:
        path = os.path.join(os.path.dirname(__file__), "resources", "test_table.csv")
        with open(path, newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            self.table = PartsTable.from_dict_rows([row for row in reader])

    def test_product_table(self) -> None:
        self.assertEqual(len(self.table.rows), 3)
        self.assertEqual(self.table.rows[0].values, {"header1": "1", "header2": "foo", "header3": "9"})
        self.assertEqual(self.table.rows[1].values, {"header1": "2", "header2": "bar", "header3": "8"})
        self.assertEqual(self.table.rows[2].values, {"header1": "3", "header2": "ducks", "header3": "7"})

    def test_multiple(self) -> None:
        path = os.path.join(os.path.dirname(__file__), "resources", "test_table.csv")
        with open(path, newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            rows = [row for row in reader]
            table = PartsTable.from_dict_rows(rows, rows)

        self.assertEqual(len(table.rows), 6)
        self.assertEqual(table.rows[0].values, {"header1": "1", "header2": "foo", "header3": "9"})
        self.assertEqual(table.rows[1].values, {"header1": "2", "header2": "bar", "header3": "8"})
        self.assertEqual(table.rows[2].values, {"header1": "3", "header2": "ducks", "header3": "7"})
        self.assertEqual(table.rows[3].values, {"header1": "1", "header2": "foo", "header3": "9"})
        self.assertEqual(table.rows[4].values, {"header1": "2", "header2": "bar", "header3": "8"})
        self.assertEqual(table.rows[5].values, {"header1": "3", "header2": "ducks", "header3": "7"})

    def test_derived_filter(self) -> None:
        table = self.table.filter(lambda row: row["header1"] != "2")
        self.assertEqual(len(table.rows), 2)
        self.assertEqual(table.rows[0].values, {"header1": "1", "header2": "foo", "header3": "9"})
        self.assertEqual(table.rows[1].values, {"header1": "3", "header2": "ducks", "header3": "7"})

    def test_derived_column(self) -> None:
        def parse_int(row: PartsTableRow) -> Dict[PartsTableColumn, Any]:
            return {self.INT_COLUMN: int(row["header1"])}

        table = self.table.map_new_columns(parse_int)
        self.assertEqual(table.rows[0][self.INT_COLUMN], 1)
        self.assertEqual(table.rows[1][self.INT_COLUMN], 2)
        self.assertEqual(table.rows[2][self.INT_COLUMN], 3)

    def test_derived_column_filter(self) -> None:
        def parse_int(row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
            if row["header1"] == "2":
                return None
            else:
                return {}

        table = self.table.map_new_columns(parse_int)
        self.assertEqual(len(table.rows), 2)
        self.assertEqual(table.rows[0].values, {"header1": "1", "header2": "foo", "header3": "9"})
        self.assertEqual(table.rows[1].values, {"header1": "3", "header2": "ducks", "header3": "7"})

    def test_sort(self) -> None:
        table = self.table.sort_by(lambda row: row["header3"])
        self.assertEqual(table.rows[0].values, {"header1": "3", "header2": "ducks", "header3": "7"})
        self.assertEqual(table.rows[1].values, {"header1": "2", "header2": "bar", "header3": "8"})
        self.assertEqual(table.rows[2].values, {"header1": "1", "header2": "foo", "header3": "9"})

    def test_map(self) -> None:
        output = self.table.map(lambda row: float(row["header1"]))
        self.assertEqual(output, [1, 2, 3])
        self.assertEqual(sum(output), 6)

    def test_first(self) -> None:
        self.assertEqual(self.table.first().values, {"header1": "1", "header2": "foo", "header3": "9"})


class UserFnPartsTableTest(unittest.TestCase):
    @staticmethod
    @ExperimentalUserFnPartsTable.user_fn()
    def user_fn_false() -> Callable[[], bool]:
        def inner() -> bool:
            return False

        return inner

    @staticmethod
    @ExperimentalUserFnPartsTable.user_fn([bool])
    def user_fn_bool_pass(meta_arg: bool) -> Callable[[], bool]:
        def inner() -> bool:
            return meta_arg

        return inner

    @staticmethod
    @ExperimentalUserFnPartsTable.user_fn([float])
    def user_fn_float_pass(meta_arg: float) -> Callable[[], float]:
        def inner() -> float:
            return meta_arg

        return inner

    @staticmethod
    def user_fn_unserialized() -> Callable[[], None]:
        def inner() -> None:
            return None

        return inner

    def test_serialize_deserialize(self) -> None:
        self.assertEqual(ExperimentalUserFnPartsTable.serialize_fn(self.user_fn_false), "user_fn_false")
        self.assertEqual(
            ExperimentalUserFnPartsTable.deserialize_fn(
                ExperimentalUserFnPartsTable.serialize_fn(self.user_fn_false)
            )(),
            False,
        )

        self.assertEqual(
            ExperimentalUserFnPartsTable.serialize_fn(self.user_fn_bool_pass, False), "user_fn_bool_pass;False"
        )
        self.assertEqual(
            ExperimentalUserFnPartsTable.deserialize_fn(
                ExperimentalUserFnPartsTable.serialize_fn(self.user_fn_bool_pass, False)
            )(),
            False,
        )
        self.assertEqual(
            ExperimentalUserFnPartsTable.deserialize_fn(
                ExperimentalUserFnPartsTable.serialize_fn(self.user_fn_bool_pass, True)
            )(),
            True,
        )

        self.assertEqual(
            ExperimentalUserFnPartsTable.serialize_fn(self.user_fn_float_pass, 0.42), "user_fn_float_pass;0.42"
        )
        self.assertEqual(
            ExperimentalUserFnPartsTable.deserialize_fn(
                ExperimentalUserFnPartsTable.serialize_fn(self.user_fn_float_pass, 0.42)
            )(),
            0.42,
        )
