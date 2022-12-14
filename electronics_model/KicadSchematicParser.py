import sexpdata


class KicadSchematic:
  def __init__(self, data: str):
    schematic_top = sexpdata.loads(data)
    print(schematic_top)
    assert schematic_top[0] == sexpdata.Symbol('kicad_sch')
