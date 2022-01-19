from .TableDeratingCapacitor import *

class JlcTable(CapacitorTable):
  """Shared base class for JlCPCB product tables that contains common row definitions."""
  JLC_PART_NUMBER = PartsTableColumn(str)
  MANUFACTURER = 'Manufacturer'
  PART_NUMBER = 'MFR.Part'
  DATASHEETS = 'Datasheet'
  DESCRIPTION = 'Description'
  COST = PartsTableColumn(float)

  @classmethod
  def _parse_jlcpcb_common(cls, row: PartsTableRow) -> Dict[PartsTableColumn, Any]:
    """Returns a dict with the cost row, or errors out with KeyError."""

    #extracts out all the available prices for a given part by order quantity
    price_list = re.findall(":(\d+\.\d*),", row['Price'])
    float_array = [float(x) for x in price_list]

    return {
      #chooses the highest price, which is for the lowest quantity
      cls.COST: float(max(float_array)),
      cls.JLC_PART_NUMBER: row['LCSC Part']
    }

  """Uses regex to extract out component values from the "Description" column of JlCPCB_SMT_Parts_Library.csv
     Ex: Gvien 'Description' => 1MΩ ±1% ±100ppm/℃ 0.25W 1206 Chip Resistor - Surface Mount ROHS
               'Regex_Dictionary' => {
                 'resistance': "(^|\s)(\d+(?:\.\d*)?[GMkmunp]?[\u03A9])($|\s)",
                 'tolerance': "(^|\s)([\u00B1]\d+(?:\.\d*)?%)($|\s)",
                 'power': "(^|\s)(\d+(?:\.\d*)?[GMkmunp]?W)($|\s)",
               }
                
         Returns resistance:  1MΩ
           resistance tolerance:  ±1%
           power dissipation:  0.25W """

  @staticmethod
  def parse(description, regex_dictionary):
    extraction_table = {}

    for key in regex_dictionary:
      matches = re.findall(regex_dictionary[key], description)
      if matches:  # discard if not matched
        assert len(matches) == 1  # excess matches fail noisily
        assert key not in extraction_table  # duplicate matches fail noisily
        extraction_table[key] = matches[0]

    return extraction_table
