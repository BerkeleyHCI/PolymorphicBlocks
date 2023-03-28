import itertools
from enum import Enum
from typing import List, Any, Dict, Tuple, TypeVar, Type, Set, NamedTuple, Union

import math
import sexpdata  # type: ignore


# This defines the minimum resolvable grid, so all coordinates are rounded to integer
# coordinates to exact position equality checks can be made without worrying about
# float precision issues.
MIN_GRID = 1.27


TestCastType = TypeVar('TestCastType')
def test_cast(x: Any, type: Type[TestCastType]) -> TestCastType:
  """Combination of (dynamic) isinstance test and static typing cast."""
  assert isinstance(x, type)
  return x

def extract_only(x: List[TestCastType]) -> TestCastType:
  """Asserts the input list only has one element, and returns it."""
  assert len(x) == 1
  return x[0]

def group_by_car(elts: List[Any]) -> Dict[Any, List[List[Any]]]:
  """Groups a list of elements by each element's car (its first element).
  Discards elements that have a non-symbol car or elements that are just a symbol."""
  out_dict: Dict[Any, List[List[Any]]] = {}
  for elt in elts:
    if isinstance(elt, list) and isinstance(elt[0], sexpdata.Symbol):
      out_dict.setdefault(elt[0].value(), []).append(elt)
    # otherwise discard
  return out_dict

PointType = Tuple[float, float]
def parse_xy(sexp: List[Any], expected_car: str = 'xy') -> PointType:
  """Given a sexp of the form (xy, x, y) (for x, y float), returns (x, y).
  X and Y are returned as part of an integer grid and rounded so points line up exactly."""
  assert len(sexp) == 3
  assert sexp[0] == sexpdata.Symbol(expected_car)
  return (round(float(sexp[1]) / MIN_GRID), round(float(sexp[2]) / MIN_GRID))

def parse_at(sexp: List[Any], expected_car: str = 'at') -> Tuple[float, float, float]:
  """Given a sexp of the form (at, x, y, r) (for x, y, r float), returns (x, y, r).
  X and Y are returned as part of an integer grid and rounded so points line up exactly."""
  assert len(sexp) == 4
  assert sexp[0] == sexpdata.Symbol(expected_car)
  return (round(float(sexp[1]) / MIN_GRID), round(float(sexp[2]) / MIN_GRID), float(sexp[3]))

def parse_symbol(sexp: Any) -> str:
  """Asserts sexp is a Symbol and returns its value."""
  assert isinstance(sexp, sexpdata.Symbol)
  return sexp.value()


class KiCadLibPin:
  """Pin in a library symbol"""
  def __repr__(self):
    return f"{self.__class__.__name__}({self.number} @ {self.pos})"

  def __init__(self, sexp: List[Any]):
    assert parse_symbol(sexp[0]) == 'pin'
    sexp_dict = group_by_car(sexp)
    self.pos = parse_at(extract_only(sexp_dict['at']))
    self.name = test_cast(extract_only(sexp_dict['name'])[1], str)
    self.number = test_cast(extract_only(sexp_dict['number'])[1], str)


class KiCadLibSymbol:
  """Symbol in a library"""
  def __repr__(self):
    return f"{self.__class__.__name__}({self.name})"

  def __init__(self, sexp: List[Any]):
    assert parse_symbol(sexp[0]) == 'symbol'
    self.name = test_cast(sexp[1], str)
    sexp_dict = group_by_car(sexp)
    self.properties: Dict[str, str] = {test_cast(prop[1], str): test_cast(prop[2], str)
                                       for prop in sexp_dict.get('property', [])}
    symbol_elts = itertools.chain(*[symbol_sexp[2:]  # discard 'symbol' and the name
                                    for symbol_sexp in sexp_dict.get('symbol', [])])
    symbol_elts_dict = group_by_car(list(symbol_elts))
    self.pins = [KiCadLibPin(pin_sexp) for pin_sexp in symbol_elts_dict.get('pin', [])]
    self.is_power = 'power' in sexp_dict


class KiCadWire:
  def __repr__(self):
    return f"{self.__class__.__name__}({self.pt1}, {self.pt2})"

  def __init__(self, sexp: List[Any]):
    assert parse_symbol(sexp[0]) == 'wire'
    sexp_dict = group_by_car(sexp)
    pts = extract_only(sexp_dict['pts'])
    assert len(pts) == 3  # pts, pt0, pt1
    self.pt1 = parse_xy(pts[1], 'xy')
    self.pt2 = parse_xy(pts[2], 'xy')


class KiCadBaseLabel:
  def __repr__(self):
    return f"{self.__class__.__name__}({self.name} @ {self.pt})"

  def __init__(self, sexp: List[Any]):
    sexp_dict = group_by_car(sexp)
    self.name = test_cast(sexp[1], str)
    self.pos = parse_at(extract_only(sexp_dict['at']))
    self.pt = (self.pos[0], self.pos[1])  # version without rotation


class KiCadLabel(KiCadBaseLabel):
  def __init__(self, sexp: List[Any]):
    super().__init__(sexp)
    assert parse_symbol(sexp[0]) == 'label'


class KiCadGlobalLabel(KiCadBaseLabel):
  def __init__(self, sexp: List[Any]):
    super().__init__(sexp)
    assert parse_symbol(sexp[0]) == 'global_label'


class KiCadHierarchicalLabel(KiCadBaseLabel):
  def __init__(self, sexp: List[Any]):
    super().__init__(sexp)
    assert parse_symbol(sexp[0]) == 'hierarchical_label'


class KiCadSymbol:
  def __repr__(self):
    return f"{self.__class__.__name__}({self.refdes}, {self.lib} @ {self.pos})"

  def __init__(self, sexp: List[Any]):
    assert parse_symbol(sexp[0]) == 'symbol'
    sexp_dict = group_by_car(sexp)
    self.properties: Dict[str, str] = {test_cast(prop[1], str): test_cast(prop[2], str)
                                       for prop in sexp_dict.get('property', [])}
    self.refdes = self.properties.get("Reference", "")
    self.lib = test_cast(extract_only(sexp_dict['lib_id'])[1], str)
    # lib_name (if present) is used for sheet-specific modified symbols to reference that modified symbol
    # but is not a user-specified name, so the interface symbol name is still lib_id
    if 'lib_name' in sexp_dict:
      self.lib_ref = test_cast(extract_only(sexp_dict['lib_name'])[1], str)
    else:
      self.lib_ref = test_cast(extract_only(sexp_dict['lib_id'])[1], str)
    self.pos = parse_at(extract_only(sexp_dict['at']))

    if 'mirror' in sexp_dict:
      self.mirror = parse_symbol(extract_only(sexp_dict['mirror'])[1])
    else:
      self.mirror = ''


class KiCadPin:
  def __repr__(self):
    return f"{self.__class__.__name__}({self.refdes}.{self.pin_number} @ {self.pt})"

  def __init__(self, symbol: KiCadSymbol, pin: KiCadLibPin):
    self.pin = pin
    self.symbol = symbol
    self.refdes = self.symbol.refdes
    self.pin_name = self.pin.name
    self.pin_number = self.pin.number

    pin_x = pin.pos[0]
    pin_y = pin.pos[1]
    symbol_rot = math.radians(symbol.pos[2])  # degrees to radians
    if symbol.mirror == '':
      pass
    elif symbol.mirror == 'x':  # mirror along x axis
      pin_y = -pin_y
      symbol_rot = -symbol_rot
    elif symbol.mirror == 'y':  # mirror along y axis
      assert symbol_rot == 0  # KiCad doesn't seem to generate Y-mirror with rotation, so this can't be tested
      pin_x = -pin_x
    else:
      raise ValueError(f"unexpected mirror value {symbol.mirror}")

    self.pt = (  # round so the positions line up exactly
      round(symbol.pos[0] + pin_x * math.cos(symbol_rot) - pin_y * math.sin(symbol_rot)),
      round(symbol.pos[1] - pin_x * math.sin(symbol_rot) - pin_y * math.cos(symbol_rot))
    )


class ParsedNet(NamedTuple):
  labels: List[KiCadBaseLabel]
  pins: List[KiCadPin]

  def __repr__(self):
    return f"{self.__class__.__name__}(labels={self.labels}, pins={self.pins})"


class SchematicOrder(Enum):
  xy = 'xy'  # in position order, X then Y (left to right first, then top to bottom)
  file = 'file'  # in order symbols are defined in the file


class KiCadSchematic:
  T = TypeVar('T')
  @staticmethod
  def _connected_components(connected: List[List[T]]) -> List[List[T]]:
    """Given a list of connections (as a list components in that connection),
    returns the set of connected components by combining connections where components
    are connected to each other.
    Somewhat maintains order"""
    # transform the list of connections into an adjacency list
    adjacency: Dict['T', List['T']] = {}
    for components in connected:
      for component in components:
        adjacency.setdefault(component, []).extend(components)
    # traverse the graph and build connected components
    all_components = list(itertools.chain(*connected))
    seen_components = set()
    connected_components: List[List['T']] = []
    for component in all_components:
      if component in seen_components:  # already seen and part of another connection
        continue
      connection_components = []

      def traverse_component(component: 'T') -> None:
        if component in seen_components:  # already seen, don't need to traverse again
          return
        seen_components.add(component)

        for connected in adjacency.get(component, []):
          if connected not in connected_components:
            connection_components.append(connected)

        for connected in adjacency.get(component, []):
          traverse_component(connected)

      traverse_component(component)
      connected_components.append(connection_components)
    return connected_components

  def __init__(self, data: str, order: SchematicOrder = SchematicOrder.xy):
    schematic_top = sexpdata.loads(data)
    assert parse_symbol(schematic_top[0]) == 'kicad_sch'
    sexp_dict = group_by_car(schematic_top)

    self.lib_symbols = {symbol.name: symbol
                        for symbol in [KiCadLibSymbol(elt)
                                       for elt in extract_only(sexp_dict.get('lib_symbols', []))[1:]]}  # discard car

    wires = [KiCadWire(elt) for elt in sexp_dict.get('wire', [])]
    labels: List[KiCadBaseLabel] = [KiCadLabel(elt) for elt in sexp_dict.get('label', [])]
    labels.extend([KiCadGlobalLabel(elt) for elt in sexp_dict.get('global_label', [])])
    labels.extend([KiCadHierarchicalLabel(elt) for elt in sexp_dict.get('hierarchical_label', [])])
    # TODO support hierarchy with sheet_instances and symbol_instances
    # TODO also check for intersections - currently pins and labels need to be at wire ends

    all_symbols = [KiCadSymbol(elt) for elt in sexp_dict.get('symbol', [])]
    # separate out power and non-power symbols, power symbols stay internal
    symbols = [symbol for symbol in all_symbols if not self.lib_symbols[symbol.lib_ref].is_power]

    # sorting allows for order-stability which allows for refdes-stability
    if order == SchematicOrder.xy:
      self.symbols = sorted(symbols, key=lambda elt: elt.pos)
    elif order == SchematicOrder.file:
      self.symbols = symbols  # preserve loaded order

    symbol_pins = list(itertools.chain(*[[KiCadPin(symbol, pin)
                                          for pin in self.lib_symbols[symbol.lib_ref].pins]
                                         for symbol in self.symbols]))

    # now, actually build the netlist, with graph traversal to find connected components
    # and by converting wires (and stuff) into lists of connected points

    # start by building a list of connected wire points
    wires_points = [[wire.pt1, wire.pt2] for wire in wires]
    wires_points = self._connected_components(wires_points)

    # build a list of pins and labels by point
    pin_labels_by_point: Dict[PointType, List[Union[KiCadPin, KiCadBaseLabel]]] = {}
    labels_by_name: Dict[str, List[Union[KiCadPin, KiCadBaseLabel]]] = {}  # this also shares a namespace w/ power symbols
    for pin in symbol_pins:
      pin_labels_by_point.setdefault(pin.pt, []).append(pin)
    for label in labels:
      pin_labels_by_point.setdefault(label.pt, []).append(label)
      labels_by_name.setdefault(label.name, []).append(label)
    power_symbols = [symbol for symbol in all_symbols if self.lib_symbols[symbol.lib_ref].is_power]
    power_pins = list(itertools.chain(*[[KiCadPin(symbol, pin)
                                         for pin in self.lib_symbols[symbol.lib_ref].pins]
                                        for symbol in power_symbols]))
    for power_pin in power_pins:
      # note that the power pin itself is handled in the component pin iteration
      labels_by_name.setdefault(power_pin.symbol.properties['Value'], []).append(power_pin)

    # transform that into a list of elements
    wires_elts: List[List[Union[KiCadPin, KiCadBaseLabel]]] = [
      list(itertools.chain(*[pin_labels_by_point.get(point, [])
                             for point in points]))
      for points in wires_points]

    # sanity check to ensure there aren't any degenerate connections
    # TODO IMPLEMENT ME

    # traverse the elements to account for labels
    for (name, name_labels) in labels_by_name.items():
      wires_elts.append(name_labels)
    wires_elts = self._connected_components(wires_elts)

    self.nets: List[ParsedNet] = []
    for elts in wires_elts:
      pins = [elt for elt in elts if isinstance(elt, KiCadPin)]
      labels = [elt for elt in elts if isinstance(elt, KiCadBaseLabel)]
      self.nets.append(ParsedNet(labels, pins))
