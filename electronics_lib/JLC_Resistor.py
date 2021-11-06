class JLCPCB_ResistorTable(ESeriesResistor):
  RESISTANCE = PartsTableColumn(Range)  
  POWER_DISSIPATION = PartsTableColumn(Range)  
  PRICE = PartsTableColumn(float)
  FOOTPRINT = PartsTableColumn(str)
    
  @classmethod
  def _generate_table(cls) -> PartsTable:
    RESISTOR_MATCHES = {
    'resistance': "\s?(\d+(\.\d*)?[GMkmunp]?)?[\u03A9]\s",
    'tolerance': "\s?([\u00B1]\d+(\.\d*)?%)\s",
    'power_dissipation': "\s?([\u00B1]\d+(\.\d*)?ppm)/℃\s"
    }

    def parse_row(row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
      if (row['Library Type'] != 'Basic'):
          return None            
      if (row['First Category'] != 'Resistors'):
          return None

      new_rows: Dict[PartsTableColumn, Any] = {}
      try:
      # handle the footprint first since this is the most likely to filter
      footprint = ""
      new_rows[cls.FOOTPRINT] = footprint
    
      extracted_values = parse(row['Description'], RESISTOR_MATCHES)
    
      new_rows[cls.RESISTANCE] = Range.from_tolerance(
          PartsTableUtil.parse_value(extracted_values['resistance'][0], 'Ohm'),
          PartsTableUtil.parse_tolerance(extracted_values['tolerance'][0])
      )
      new_rows[cls.POWER_DISSIPATION] = PartsTableUtil.parse_value(extracted_values['power_dissipation'][0])
      new_rows[cls.PRICE] = float(max(re.findall(":(\d+\.\d*),", row['Price'])))
    
      new_rows[cls.PRICE] = float(row['Price'])
    
      return new_rows
      except (KeyError, PartsTableUtil.ParseError):
      return None

      raw_table = PartsTable.from_csv_files(PartsTableUtil.with_source_dir([
      'JLCPCB_SMT_Parts_Library.csv'
      ], 'resources'), encoding='utf-8-sig')
      return raw_table.map_new_columns(parse_row)
    
 
 class JLCPCB_Resistor(Resistor, FootprintBlock, GeneratorBlock):
   @init_in_parent
   def __init__(self, **kwargs):
     super().__init__(**kwargs)
     self.part_spec = self.Parameter(StringExpr(""))
     self.footprint_spec = self.Parameter(StringExpr(""))
     self.generator(self.select_inductor, self.inductance, self.current, self.frequency,
                    self.part_spec, self.footprint_spec)

     # Output values
     self.selected_resistance = self.Parameter(RangeExpr())
     self.selected_power_dissipation = self.Parameter(RangeExpr())

   def select_inductor(self, resistance: Range, power_dissipation: Range,
                       part_spec: str, footprint_spec: str) -> None:
     compatible_parts = JLCPCB_ResistorTable.table().filter(lambda row: (
         (not part_spec or part_spec == row['Manufacturer Part Number']) and
         (not footprint_spec or footprint_spec == row[InductorTable.FOOTPRINT]) and
         row[JLCPCB_ResistorTable.RESISTANCE].fuzzy_in(resistance) and
         row[JLCPCB_ResistorTable.POWER_DISSIPATION].fuzzy_in(power_dissipation) and
     ))
     part = compatible_parts.sort_by(
       lambda row: row[JLCPCB_ResistorTable.FOOTPRINT]
     ).sort_by(
       lambda row: row[JLCPCB_ResistorTable.PRICE]
     ).first(f"no resistors in {resistance} Ohm, {power_dissipation} ppm, {[row.value['Manufacturer Part Number'] for row in JLCPCB_ResistorTable.table().rows]}")

     self.assign(self.selected_resistance, part[JLCPCB_ResistorTable.RESISTANCE])
     self.assign(self.selected_power_dissipation, part[JLCPCB_ResistorTable.POWER_DISSIPATION])

     self.footprint(
       'R', part[JLCPCB_ResistorTable.FOOTPRINT],
       {
         '1': self.a,
         '2': self.b,
       },
       mfr=part['Manufacturer'], part=part['Manufacturer Part Number'],
       value=f"{part['Resistance']}, {part['Power_dissipation']}",
       datasheet=part['Datasheets']
     )