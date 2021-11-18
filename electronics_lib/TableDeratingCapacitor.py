from electronics_abstract_parts import *
from .PartsTable import *
import math

class TableDeratingCapacitor(Capacitor):
    DERATE_VOLTCO = {
        'Capacitor_SMD:C_0805_2012Metric': 0.08,
        'Capacitor_SMD:C_1206_3216Metric': 0.04,
    }
    DERATE_MIN_VOLTAGE = 3.6  # voltage at which derating is zero
    DERATE_MIN_CAPACITANCE = 1.0e-6
    DERATED_CAPACITANCE = PartsTableColumn(Range)

    PARALLEL_COUNT = PartsTableColumn(int)
    PARALLEL_CAPACITANCE = PartsTableColumn(Range)
    PARALLEL_DERATED_CAPACITANCE = PartsTableColumn(Range)
    PARALLEL_COST = PartsTableColumn(float)

    def derate_row(self, row: PartsTableRow, voltage: Range, Table: Type) -> Optional[Dict[PartsTableColumn, Any]]:
        if voltage.upper < self.DERATE_MIN_VOLTAGE:  # zero derating at low voltages
            derated = row[Table.CAPACITANCE]
        elif row[Table.NOMINAL_CAPACITANCE] <= self.DERATE_MIN_CAPACITANCE:  # don't derate below 1uF
            derated = row[Table.CAPACITANCE]
        elif row[Table.FOOTPRINT] not in self.DERATE_VOLTCO:  # should be rare, small capacitors should hit the above
            return None
        else:  # actually derate
            voltco = self.DERATE_VOLTCO[row[Table.FOOTPRINT]]
            factor = 1 - voltco * (Table.upper - 3.6)
            derated = row[Table.CAPACITANCE] * Range(factor, 1)

        return {self.DERATED_CAPACITANCE: derated}

    def parallel_row(self, row: PartsTableRow, capacitance: Range, Table: Type) -> Optional[Dict[PartsTableColumn, Any]]:
        new_cols: Dict[PartsTableColumn, Any] = {}
        count = math.ceil(capacitance.lower / row[self.DERATED_CAPACITANCE].lower)
        derated_parallel_capacitance = row[self.DERATED_CAPACITANCE] * count
        if not derated_parallel_capacitance.fuzzy_in(capacitance):  # not satisfying spec
            return None

        new_cols[self.PARALLEL_COUNT] = count
        new_cols[self.PARALLEL_DERATED_CAPACITANCE] = derated_parallel_capacitance
        new_cols[self.PARALLEL_CAPACITANCE] = row[Table.CAPACITANCE] * count
        new_cols[self.PARALLEL_COST] = row[Table.COST] * count

        return new_cols
