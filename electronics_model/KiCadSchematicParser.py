import itertools
from typing import List, Any, Dict, Tuple, TypeVar, Type, Set, NamedTuple

import math
import sexpdata  # type: ignore


TestCaseType = TypeVar('TestCaseType')
def test_cast(x: Any, type: Type[TestCaseType]) -> TestCaseType:
  """Combination of (dynamic) isinstance test and static typing cast."""
  assert isinstance(x, type)
  return x

def extract_only(x: List[TestCaseType]) -> TestCaseType:
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
  """Given a sexp of the form (xy, x, y) (for x, y float), returns (x, y)."""
  assert len(sexp) == 3
  assert sexp[0] == sexpdata.Symbol(expected_car)
  return (float(sexp[1]), float(sexp[2]))

def parse_at(sexp: List[Any], expected_car: str = 'at') -> Tuple[float, float, float]:
  """Given a sexp of the form (at, x, y, r) (for x, y, r float), returns (x, y, r)."""
  assert len(sexp) == 4
  assert sexp[0] == sexpdata.Symbol(expected_car)
  return (float(sexp[1]), float(sexp[2]), float(sexp[3]))

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


class KiCadAnyLabel:
  def __repr__(self):
    return f"{self.__class__.__name__}({self.name} @ {self.pt})"

  def __init__(self, sexp: List[Any]):
    assert parse_symbol(sexp[0]) in ('label', 'global_label')
    sexp_dict = group_by_car(sexp)
    self.name = test_cast(sexp[1], str)
    self.pos = parse_at(extract_only(sexp_dict['at']))
    self.pt = (self.pos[0], self.pos[1])  # version without rotation


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
    self.pos = parse_at(extract_only(sexp_dict['at']))


class KiCadPin:
  def __repr__(self):
    return f"{self.__class__.__name__}({self.refdes}.{self.pin_number} @ {self.pt})"

  def __init__(self, symbol: KiCadSymbol, pin: KiCadLibPin):
    self.pin = pin
    self.symbol = symbol
    self.refdes = self.symbol.refdes
    self.pin_number = self.pin.number
    symbol_rot = math.radians(symbol.pos[2])  # degrees to radians
    self.pt = (  # round so the positions line up exactly
      round(symbol.pos[0] + pin.pos[0] * math.cos(symbol_rot) - pin.pos[1] * math.sin(symbol_rot), 2),
      round(symbol.pos[1] - pin.pos[0] * math.sin(symbol_rot) - pin.pos[1] * math.cos(symbol_rot), 2)
    )


class ParsedNet(NamedTuple):
  labels: List[KiCadAnyLabel]
  pins: List[KiCadPin]

  def __repr__(self):
    return f"{self.__class__.__name__}(labels={self.labels}, pins={self.pins})"


class KiCadSchematic:
  def __init__(self, data: str):
    schematic_top = sexpdata.loads(data)
    assert parse_symbol(schematic_top[0]) == 'kicad_sch'
    sexp_dict = group_by_car(schematic_top)

    self.lib_symbols = {symbol.name: symbol
                        for symbol in [KiCadLibSymbol(elt)
                                       for elt in extract_only(sexp_dict.get('lib_symbols', []))[1:]]}  # discard car

    wires = [KiCadWire(elt) for elt in sexp_dict.get('wire', [])]
    labels = [KiCadAnyLabel(elt) for elt in sexp_dict.get('label', []) + sexp_dict.get('global_label', [])]

    self.symbols = [KiCadSymbol(elt) for elt in sexp_dict.get('symbol', [])]
    symbol_pins = list(itertools.chain(*[[KiCadPin(symbol, pin)
                                          for pin in self.lib_symbols[symbol.lib].pins]
                                         for symbol in self.symbols]))

    # now, actually build the netlist, with graph traversal to find connected components
    # and by converting wires (and stuff) into lists of connected points

    # build adjacency matrix
    edges: Dict[PointType, List[PointType]] = {}
    for wire in wires:
      edges.setdefault(wire.pt1, []).append(wire.pt2)
      edges.setdefault(wire.pt2, []).append(wire.pt1)

    # build adjacency matrix for pin locations
    pin_points: Dict[PointType, List[KiCadPin]] = {}
    for pin in symbol_pins:
      pin_points.setdefault(pin.pt, []).append(pin)
    label_points: Dict[PointType, List[KiCadAnyLabel]] = {}
    for label in labels:
      label_points.setdefault(label.pt, []).append(label)

    # TODO support hierarchy with sheet_instances and symbol_instances
    # TODO also check for intersections - currently pins and labels need to be at wire ends

    # traverse the graph and build up nets
    seen_points: Set[PointType] = set()
    self.nets: List[ParsedNet] = []
    for point, pins in pin_points.items():
      if point in seen_points:
        continue  # already seen and part of another net
      net_pins: List[KiCadPin] = []
      net_labels: List[KiCadAnyLabel] = []
      def traverse_point(point: PointType) -> None:
        if point in seen_points:
          return  # already seen, don't traverse again
        seen_points.add(point)

        for pin in pin_points.get(point, []):
          net_pins.append(pin)
        for label in label_points.get(point, []):
          net_labels.append(label)
        for point2 in edges.get(point, []):
          traverse_point(point2)

      traverse_point(point)
      self.nets.append(ParsedNet(net_labels, net_pins))
