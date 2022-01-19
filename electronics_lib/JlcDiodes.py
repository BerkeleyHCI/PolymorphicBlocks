from electronics_abstract_parts.AbstractDiodes import *
from electronics_abstract_parts.AbstractJlcDiodes import *
from .JlcTable import *

class BaseJlcDiodeTable(JlcTable):
    PACKAGE_FOOTPRINT_MAP = {
        'SMA, DO-214AC': 'Diode_SMD:D_SMA',
        'SMB, DO-214AA': 'Diode_SMD:D_SMB',
        'SMC, DO-214AB': 'Diode_SMD:D_SMC',
        'SOD-123': 'Diode_SMD:D_SOD-123',
        'SOD-123F': 'Diode_SMD:D_SOD-123',
        'SOD-123FL': 'Diode_SMD:D_SOD-123',
        'SOD-323': 'Diode_SMD:D_SOD-323',    # Was originally 'SC-76, SOD-323'
        'SOD-323F': 'Diode_SMD:D_SOD-323',  # Was originally 'SC-90, SOD-323F'
        'TO-252-3, DPak (2 Leads + Tab), SC-63': 'Package_TO_SOT_SMD:TO-252-2',
        'TO-263-3, D²Pak (2 Leads + Tab), TO-263AB': 'Package_TO_SOT_SMD:TO-263-2',
        'LL-34': 'Diode_SMD:D_MiniMELF',
    }

    all_voltages_regex = '(?:^|\s)(\d+(?:\.\d+)?[GMkmunp]?V)(?:$|\s)'
    all_currents_regex =  '(?:^|\s)(\d+(?:\.\d+)?[GMkmunp]?A)(?:$|\s)'

    def str_to_float_list(regex: str, uni: str, row: PartsTableRow) -> List[float]:
        str_results = re.findall(regex, row['Description'])
        float_results = []
        for x in str_results:
            float_results.append(PartsTableUtil.parse_value(x, uni))

        return sorted(float_results, key = float)

    @classmethod
    def footprint_pinmap(cls, footprint: str, anode: CircuitPort, cathode: CircuitPort):
        return {
            'Diode_SMD:D_SMA': {
                '1': cathode,
                '2': anode,
            },
            'Diode_SMD:D_SMB': {
                '1': cathode,
                '2': anode,
            },
            'Diode_SMD:D_SMC': {
                '1': cathode,
                '2': anode,
            },
            'Diode_SMD:D_SOD-123': {
                '1': cathode,
                '2': anode,
            },
            'Diode_SMD:D_SOD-323': {
                '1': cathode,
                '2': anode,
            },
            'Package_TO_SOT_SMD:TO-252-2': {
                '1': anode,
                '2': cathode,
                '3': anode,
            },
            'Package_TO_SOT_SMD:TO-263-2': {
                '1': anode,  # TODO sometimes NC
                '2': cathode,
                '3': anode,
            },
            'Diode_SMD:D_MiniMELF': {
                '1': cathode,
                '2': anode,
            },
        }[footprint]

class JlcDiodeTable(BaseJlcDiodeTable):
    VOLTAGE_RATING = PartsTableColumn(Range)  # tolerable voltages, positive
    CURRENT_RATING = PartsTableColumn(Range)  # tolerable currents, average
    FORWARD_VOLTAGE = PartsTableColumn(Range)  # possible forward voltage range
    REVERSE_RECOVERY = PartsTableColumn(Range)  # possible reverse recovery time
    JUNCTION_TEMP = PartsTableColumn(Range)
    FOOTPRINT = PartsTableColumn(str)  # KiCad footprint name


    @classmethod
    def _generate_table(cls) -> PartsTable:

        def parse_row(row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
            if (row['Library Type'] != 'Basic' or row['First Category'] != 'Diodes'):
                return None

            if ('General Purpose' not in row['Description']
                and 'Schottky Barrier Diodes' not in row['Description']
                and 'Switching Diode' not in row['Description']):
                return None

            new_cols: Dict[PartsTableColumn, Any] = {}
            try:
                new_cols[cls.FOOTPRINT] = cls.PACKAGE_FOOTPRINT_MAP[row['Package']]

                voltages = cls.str_to_float_list(cls.all_voltages_regex, 'V')
                if(len(voltages) > 1):
                    new_cols[cls.FORWARD_VOLTAGE] = Range.zero_to_upper(voltages[0])
                    new_cols[cls.VOLTAGE_RATING] = Range.zero_to_upper(voltages[1])
                else:
                    new_cols[cls.FORWARD_VOLTAGE] = Range.zero_to_upper(float('inf'))
                    new_cols[cls.VOLTAGE_RATING] = Range.zero_to_upper(float('inf'))

                currents = cls.str_to_float_list(cls.all_currents_regex, 'A')
                if (len(currents) > 1):
                    new_cols[cls.CURRENT_RATING] = Range.zero_to_upper(
                        max(currents)
                    )
                elif (len(currents) == 1):
                    new_cols[cls.CURRENT_RATING] = Range.zero_to_upper(
                        currents[0]
                    )
                else:
                    new_cols[cls.CURRENT_RATING] = Range.zero_to_upper(0)

                if ('Switching Diode' in row['Description']):
                    SWITCHING_DIODE_MATCHES = {
                        'junction_temperature': "(?:^|\s)\+(\d+(?:\.\d*)?℃)($|\s)",
                        'reverse_recovery': "(?:^|\s)(\d+(?:\.\d*)?[munp]s)($|\s)",
                    }

                    extracted_values = JlcTable.parse(row[JlcTable.DESCRIPTION], SWITCHING_DIODE_MATCHES)

                    new_cols[cls.JUNCTION_TEMP] = Range.zero_to_upper(
                        PartsTableUtil.parse_value(extracted_values['junction_temperature'], '℃')
                    )

                    reverse_recovery = Range.zero_to_upper(float('inf'))
                    if extracted_values['reverse_recovery'] and extracted_values['reverse_recovery'] != '-':
                        reverse_recovery = Range.zero_to_upper(
                            PartsTableUtil.parse_value(extracted_values['reverse_recovery'], 's')
                        )

                    new_cols[cls.REVERSE_RECOVERY] = reverse_recovery
                else:
                    new_cols[cls.JUNCTION_TEMP] = Range.zero_to_upper(float('inf'))
                    new_cols[cls.REVERSE_RECOVERY] = Range.zero_to_upper(float('inf'))


                new_cols.update(cls._parse_jlcpcb_common(row))

                return new_cols
            except (KeyError, PartsTableUtil.ParseError):
                return None

        raw_table = PartsTable.from_csv_files(PartsTableUtil.with_source_dir([
            'JLCPCB_SMT_Parts_Library.csv'
        ], 'resources'), encoding='gb2312')
        return raw_table.map_new_columns(parse_row).sort_by(
            lambda row: [row[cls.FOOTPRINT], row[cls.COST]]
        )


class JlcDiode(Diode, FootprintBlock, GeneratorBlock):
    @init_in_parent
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_voltage_rating = self.Parameter(RangeExpr())
        self.selected_current_rating = self.Parameter(RangeExpr())
        self.selected_voltage_drop = self.Parameter(RangeExpr())
        self.selected_reverse_recovery_time = self.Parameter(RangeExpr())

        self.generator(self.select_part, self.reverse_voltage, self.current, self.voltage_drop,
                       self.reverse_recovery_time)
        # TODO: also support optional part and footprint name

    def select_part(self, reverse_voltage: Range, current: Range, voltage_drop: Range,
                    reverse_recovery_time: Range) -> None:
        part = JlcDiodeTable.table().filter(lambda row: (
            reverse_voltage.fuzzy_in(row[JlcDiodeTable.VOLTAGE_RATING]) and
            current.fuzzy_in(row[JlcDiodeTable.CURRENT_RATING]) and
            row[JlcDiodeTable.FORWARD_VOLTAGE].fuzzy_in(voltage_drop) and
            row[JlcDiodeTable.REVERSE_RECOVERY].fuzzy_in(reverse_recovery_time)
        )).first(f"no diodes in Vr,max={reverse_voltage} V, I={current} A, Vf={voltage_drop} V, trr={reverse_recovery_time} s")

        self.assign(self.selected_voltage_rating, part[JlcDiodeTable.VOLTAGE_RATING])
        self.assign(self.selected_current_rating, part[JlcDiodeTable.CURRENT_RATING])
        self.assign(self.selected_voltage_drop, part[JlcDiodeTable.FORWARD_VOLTAGE])
        self.assign(self.selected_reverse_recovery_time, part[JlcDiodeTable.REVERSE_RECOVERY])

        self.footprint(
            'D', part[JlcDiodeTable.FOOTPRINT],
            JlcDiodeTable.footprint_pinmap(part[JlcDiodeTable.FOOTPRINT],
                                        self.anode, self.cathode),
            mfr=part[JlcDiodeTable.MANUFACTURER], part=part[JlcDiodeTable.PART_NUMBER],
            value=part[JlcDiodeTable.DESCRIPTION],
            datasheet=part[JlcDiodeTable.DATASHEETS]
        )


class JlcZenerTable(BaseJlcDiodeTable):
    ZENER_VOLTAGE = PartsTableColumn(Range)  # actual zener voltage, positive
    FORWARD_VOLTAGE = PartsTableColumn(Range)  # possible forward voltage range
    POWER_RATING = PartsTableColumn(Range)  # tolerable power
    FOOTPRINT = PartsTableColumn(str)  # KiCad footprint name

    @classmethod
    def _generate_table(cls) -> PartsTable:

        def parse_row(row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
            if (row['Library Type'] != 'Basic' or row['First Category'] != 'Diodes'
                or 'Zener Diodes' not in row['Description']):
                return None

            new_cols: Dict[PartsTableColumn, Any] = {}
            try:
                new_cols[cls.FOOTPRINT] = cls.PACKAGE_FOOTPRINT_MAP[row['Package']]

                voltages = cls.str_to_float_list(cls.all_voltages_regex, 'V')
                if(len(voltages) > 1):
                    new_cols[cls.FORWARD_VOLTAGE] = Range.zero_to_upper(voltages[0])
                    new_cols[cls.ZENER_VOLTAGE] = Range.zero_to_upper(voltages[1])
                else:
                    new_cols[cls.FORWARD_VOLTAGE] = Range.zero_to_upper(float('inf'))
                    new_cols[cls.ZENER_VOLTAGE] = Range.zero_to_upper(float('inf'))

                if ('TVS ROHS' in row['Description']):
                    current = min(cls.str_to_float_list(cls.all_currents_regex, 'A'))

                    new_cols[cls.POWER_RATING] = Range.zero_to_upper(
                        current * new_cols[cls.ZENER_VOLTAGE]
                    )
                else:
                    ZENER_DIODE_MATCHES = {
                        'power_rating': "(?:^|\s)(\d+(?:\.\d+)?[GMkmunp]?W)(?:$|\s)",
                    }

                    extracted_values = JlcTable.parse(row[JlcTable.DESCRIPTION], ZENER_DIODE_MATCHES)

                    new_cols[cls.POWER_RATING] = Range.zero_to_upper(
                        PartsTableUtil.parse_value(extracted_values['power_rating'], 'W')
                    )

                new_cols.update(cls._parse_jlcpcb_common(row))

                return new_cols
            except (KeyError, PartsTableUtil.ParseError):
                return None

        raw_table = PartsTable.from_csv_files(PartsTableUtil.with_source_dir([
            'JLCPCB_SMT_Parts_Library.csv'
        ], 'resources'), encoding='gb2312')
        return raw_table.map_new_columns(parse_row).sort_by(
            lambda row: [row[cls.FOOTPRINT], row[cls.COST]]
        )


class JlcZenerDiode(ZenerDiode, FootprintBlock, GeneratorBlock):
    @init_in_parent
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_zener_voltage = self.Parameter(RangeExpr())
        self.selected_forward_voltage_drop = self.Parameter(RangeExpr())
        self.selected_power_rating = self.Parameter(RangeExpr())

        self.generator(self.select_part, self.zener_voltage, self.forward_voltage_drop, self.power_rating)
        # TODO: also support optional part and footprint name

    def select_part(self, zener_voltage: Range, forward_voltage_drop: Range, power_rating: Range) -> None:
        part = JlcZenerTable.table().filter(lambda row: (
                row[JlcZenerTable.ZENER_VOLTAGE].fuzzy_in(zener_voltage) and
                row[JlcZenerTable.FORWARD_VOLTAGE].fuzzy_in(forward_voltage_drop) and
                row[JlcZenerTable.POWER_RATING].fuzzy_in(power_rating)
        )).first(f"no zener diodes in Vz={zener_voltage} V, Vf={forward_voltage_drop} V, P={power_rating} W")

        self.assign(self.selected_zener_voltage, part[JlcZenerTable.ZENER_VOLTAGE])
        self.assign(self.selected_forward_voltage_drop, part[JlcZenerTable.FORWARD_VOLTAGE])
        self.assign(self.selected_power_rating, part[JlcZenerTable.POWER_RATING])

        self.footprint(
            'D', part[JlcZenerTable.FOOTPRINT],
            JlcZenerTable.footprint_pinmap(part[JlcZenerTable.FOOTPRINT],
                                        self.anode, self.cathode),
            mfr=part[JlcZenerTable.MANUFACTURER], part=part[JlcZenerTable.PART_NUMBER],
            value=part[JlcDiodeTable.DESCRIPTION],
            datasheet=part[JlcZenerTable.DATASHEETS]
        )
