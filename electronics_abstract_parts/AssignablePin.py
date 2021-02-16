from typing import *

from electronics_model.PinAssignmentUtil import leaf_circuit_ports, PinName, ConcretePinName
from electronics_model import *


@non_library
class AssignablePinBlock(GeneratorBlock):
  """Provides two features common to microcontrollers:
  new_io(tpe): returns a fresh IO port of type tpe
  suggest_pin(port, str): suggests a pinmap
  TODO should these be separate?"""
  def __init__(self):
    super().__init__()

    self._all_assignable_ios: List[Port] = []
    self._remaining_assignable_ios: Dict[Type[Port], List[Port]] = {}

    self._suggested_pins_params: ElementDict[StringExpr] = ElementDict()

  # TODO type signature could be enhanced to only allow iterable pin with Bundle type
  PortType = TypeVar('PortType', bound=Union[CircuitPort, Bundle])
  def new_io(self, tpe: Type[PortType], *, pin: Optional[Union[PinName, Iterable[PinName]]] = None) -> PortType:
    # TODO maybe tpe should be a connectable type? or should this be an assign-and-connect op?
    assert tpe in self._remaining_assignable_ios, f"{type(self)} has no IOs of type {tpe}"
    remaining_list = self._remaining_assignable_ios[tpe]
    assert remaining_list, f"{type(self)} has no more IOs of type {tpe}"
    port = remaining_list.pop()

    if pin is not None:
      self._suggest_pin(port, pin)

    return port  # type: ignore

  def _suggest_pin(self, port: Port, pin: Union[PinName, Iterable[PinName]]):
    from edg_core.Builder import builder

    if isinstance(port, CircuitPort) and not isinstance(pin, Iterable):
      if isinstance(pin, (int, str)):
        builder.get_curr_block().assign(
          self._suggested_pins_params[self._name_of(port)], str(pin)
        )
      elif pin is NotConnectedPin:
        builder.get_curr_block().assign(
          self._suggested_pins_params[self._name_of(port)], '_not_connected'
        )
      elif pin is AnyPin:
        pass  # no constraint for any-pin
    elif isinstance(port, Bundle) and isinstance(pin, Iterable):
      leaf_ports = list(leaf_circuit_ports(port))
      pin = list(pin)  # copy in case iterable once  # TODO: avoid converting to list for Sized typecast
      assert len(pin) == len(leaf_ports), f"suggested pins {pin} must be of same length as leaf ports {leaf_ports} in bundle"
      for leaf_port, leaf_pin in zip(leaf_ports, pin):
        self._suggest_pin(leaf_port, leaf_pin)
    else:
      raise ValueError(f"suggest_pin {port}={pin} not supported")

  def _add_assignable_io(self, port: Port):
    self._all_assignable_ios.append(port)
    self._remaining_assignable_ios.setdefault(type(port), []).append(port)

    for leaf_circuit_port in leaf_circuit_ports(port):
      self._suggested_pins_params[self._name_of(leaf_circuit_port)] = self.Parameter(StringExpr())

  def _get_suggested_pin_maps(self) -> IdentityDict[CircuitPort, PinName]:
    pinmap: IdentityDict[CircuitPort, PinName] = IdentityDict()
    for top_port in self._all_assignable_ios:
      for leaf_circuit_port in leaf_circuit_ports(top_port):
        pin_param = self._suggested_pins_params[self._name_of(leaf_circuit_port)]
        if self._has(pin_param):
          pin = self.get(pin_param)
          if pin == '_not_connected':
            pinmap[leaf_circuit_port] = NotConnectedPin
          else:
            pinmap[leaf_circuit_port] = pin
    return pinmap
