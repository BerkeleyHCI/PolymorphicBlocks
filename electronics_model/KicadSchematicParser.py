import itertools
from typing import List, Any, Dict, Tuple, TypeVar, Type

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

def parse_xy(sexp: List[Any], expected_car: str = 'xy') -> Tuple[float, float]:
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


class KicadLibPin:
  def __repr__(self):
    return f"{self.__class__.__name__}({self.number} @ {self.pt})"

  def __init__(self, sexp: List[Any]):
    assert parse_symbol(sexp[0]) == 'pin'
    sexp_dict = group_by_car(sexp)
    self.pt = parse_at(extract_only(sexp_dict['at']))
    self.number = test_cast(extract_only(sexp_dict['number'])[1], str)


class KicadLibSymbol:
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
    pins = [KicadLibPin(pin_sexp) for pin_sexp in symbol_elts_dict.get('pin', [])]
    print(pins)


class KicadWire:
  def __repr__(self):
    return f"{self.__class__.__name__}({self.pt1}, {self.pt2})"

  def __init__(self, sexp: List[Any]):
    assert parse_symbol(sexp[0]) == 'wire'
    sexp_dict = group_by_car(sexp)
    pts = extract_only(sexp_dict['pts'])
    assert len(pts) == 3  # pts, pt0, pt1
    self.pt1 = parse_xy(pts[1], 'xy')
    self.pt2 = parse_xy(pts[2], 'xy')


class KicadSchematic:
  def __init__(self, data: str):
    schematic_top = sexpdata.loads(data)
    assert parse_symbol(schematic_top[0]) == 'kicad_sch'
    top_groups = group_by_car(schematic_top)
    wires = [KicadWire(elt) for elt in top_groups.get('wire', [])]
    lib_symbols = [KicadLibSymbol(elt) for elt in extract_only(top_groups.get('lib_symbols', []))[1:]]  # slice to discard car
    print(lib_symbols)

    # TODO support hierarchy with sheet_instances and symbol_instances
