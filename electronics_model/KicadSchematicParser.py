from typing import List, Any, Dict, Tuple, TypeVar, Type

import sexpdata  # type: ignore


TestCaseType = TypeVar('TestCaseType')
def test_cast(x: Any, type: Type[TestCaseType]) -> TestCaseType:
  """Combination of (dynamic) isinstance test and static typing cast."""
  assert isinstance(x, type)
  return x

def group_by_car(elts: List[Any]) -> Dict[Any, List[List[Any]]]:
  """Groups a list of elements by each element's car (its first element).
  Discards elements that have a non-symbol car or elements that are just a symbol."""
  out_dict: Dict[Any, List[List[Any]]] = {}
  for elt in elts:
    if isinstance(elt, list) and isinstance(elt[0], sexpdata.Symbol):
      out_dict.setdefault(elt[0].value(), []).append(elt)
    # otherwise discard
  return out_dict

def parse_xy(sexp: List[Any], expected_car: str) -> Tuple[float, float]:
  """Given a sexp of the form (expected_car, a, b) (for a, b float), returns (a, b)."""
  assert len(sexp) == 3
  assert sexp[0] == sexpdata.Symbol(expected_car)
  return (test_cast(sexp[1], float), test_cast(sexp[2], float))

def parse_symbol(sexp: Any) -> str:
  """Asserts sexp is a Symbol and returns its value."""
  assert isinstance(sexp, sexpdata.Symbol)
  return sexp.value()


class KicadLibSymbol:
  def __repr__(self):
    return f"{self.__class__.__name__}({self.name})"

  def __init__(self, sexp: List[Any]):
    assert parse_symbol(sexp[0]) == 'symbol'
    self.name = test_cast(sexp[1], str)
    sexp_dict = group_by_car(sexp)
    self.properties: Dict[str, str] = {test_cast(prop[1], str): test_cast(prop[2], str)
                                       for prop in sexp_dict.get('property', [])}


class KicadWire:
  def __repr__(self):
    return f"{self.__class__.__name__}({self.pt1}, {self.pt2})"

  def __init__(self, sexp: List[Any]):
    assert parse_symbol(sexp[0]) == 'wire'
    sexp_dict = group_by_car(sexp)
    assert len(sexp_dict['pts']) == 1 and len(sexp_dict['pts'][0]) == 3  # including pts itself
    self.pt1 = parse_xy(sexp_dict['pts'][0][1], 'xy')
    self.pt2 = parse_xy(sexp_dict['pts'][0][2], 'xy')


class KicadSchematic:
  def __init__(self, data: str):
    schematic_top = sexpdata.loads(data)
    assert parse_symbol(schematic_top[0]) == 'kicad_sch'
    top_groups = group_by_car(schematic_top)
    print(top_groups.keys())
    print(top_groups['wire'])

    wires = [KicadWire(elt) for elt in top_groups.get('wire', [])]
    print(wires)
    lib_symbols = [KicadLibSymbol(elt) for elt in top_groups.get('lib_symbols', [])[0][1:]]  # slice to discard car
    print(lib_symbols)

    sexpdata.Symbol('kicad_sch').value()