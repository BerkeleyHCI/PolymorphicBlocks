from typing import *
from abc import abstractmethod
from itertools import chain

from edg_core import *
from .VoltagePorts import CircuitPort


def leaf_circuit_ports(prefix: str, port: Port) -> Iterable[Tuple[str, CircuitPort]]:
  if isinstance(port, CircuitPort):
    return [(prefix, port)]
  elif isinstance(port, Bundle):
    return chain(*[leaf_circuit_ports(f"{prefix}.{name}", port)
                   for (name, port) in port._ports.items()])
  else:
    raise ValueError(f"unable to flatten {port}")


class SpecialPin():
  pass


NotConnectedPin = SpecialPin()
AnyPin = SpecialPin()

PinName = Union[str, int, SpecialPin]
ConcretePinName = str


class AssignablePinGroup():
  """Base class for assignable pin definitions"""
  @abstractmethod
  def get_assignable_ports(self) -> Iterable[Port]: ...  # returns all top-level assignable ports

  @abstractmethod
  def assign(self, port: Port, preassigns: IdentityDict[CircuitPort, PinName], assigned: Set[ConcretePinName]) ->\
      Optional[Dict[ConcretePinName, CircuitPort]]: ...  # returns an assignment of all leaf ports given a top-level port


class AnyPinAssign(AssignablePinGroup):
  """Pin assignment where any leaf port can be connected to any pin.
  All leaf ports must be CircuitPort.
  Useful for devices with a switch matrix, or for assigning GPIOs"""
  def __init__(self, ports: Iterable[Port], pins: Iterable[Union[str, int]]) -> None:
    self.all_ports = list(ports)
    self.pins = set(str(pin) for pin in pins)

  def get_assignable_ports(self) -> Iterable[Port]:
    return self.all_ports

  def assign(self, port: Port, preassigns: IdentityDict[CircuitPort, PinName], assigned: Set[ConcretePinName]) ->\
      Optional[Dict[ConcretePinName, CircuitPort]]:
    assignments: Dict[ConcretePinName, CircuitPort] = {}
    available_pins = self.pins.difference(assigned).difference(preassigns.values())
    for leaf_name, leaf_port in leaf_circuit_ports("", port):
      if leaf_port in preassigns:
        preassign_pin = preassigns[leaf_port]
        if isinstance(preassign_pin, str):  # shouldn't have ints based on how params propagated
          assert preassign_pin in self.pins, f"preassign for {preassign_pin}={port} not in pin set {self.pins} for {self}"
          assignments[preassign_pin] = leaf_port
        elif preassign_pin == NotConnectedPin:
          pass
        else:
          raise ValueError(f"bad preassign value {preassign_pin}")
      elif not available_pins:
        return None
      else:
        assignments[available_pins.pop()] = leaf_port
    return assignments


class PeripheralPinAssign(AssignablePinGroup):
  """Pin assignment where the Bundle must be assigned as a whole.
  Remappable leaf nodes are permitted.
  Each pin list is for one port (eg Bundle), with each element being the pin(s) assignable for that leaf wire."""
  def __init__(self, ports: Iterable[Port], *pin_groups: List[Union[List[Union[int, str]], int, str]]) -> None:
    self.all_ports = list(ports)
    def process_assignable_pin(leaf_pins: Union[List[Union[int, str]], int, str]) -> List[str]:
      if isinstance(leaf_pins, list):
        return [str(pin) for pin in leaf_pins]
      else:
        return [str(leaf_pins)]

    self.pins: List[List[List[str]]] = [
      [process_assignable_pin(leaf_pins) for leaf_pins in pin_group] for pin_group in pin_groups
    ]

  def get_assignable_ports(self) -> Iterable[Port]:
    return self.all_ports

  def assign(self, port: Port, preassigns: IdentityDict[CircuitPort, PinName], assigned: Set[ConcretePinName]) -> \
      Optional[Dict[ConcretePinName, CircuitPort]]:
    leaf_name_ports = list(leaf_circuit_ports("", port))

    for group_pins in self.pins:
      assert len(group_pins) == len(leaf_name_ports)

      group_dict: Dict[ConcretePinName, CircuitPort] = {}
      group_failed = False
      for available_pins, (leaf_name, leaf_port) in zip(group_pins, leaf_name_ports):
        if group_failed:
          continue

        if leaf_port in preassigns and preassigns[leaf_port]:  # preassigned pin
          preassign_pin = preassigns[leaf_port]

          if preassign_pin is NotConnectedPin:
            pass
          elif isinstance(preassign_pin, str):
            if preassign_pin in available_pins:
              group_dict[preassign_pin] = leaf_port
            else:
              group_failed = True
          else:
            raise ValueError(f"bad preassign value {preassign_pin}")
        else:  # non-preassigned pin
          available_pins = [pin for pin in available_pins if pin not in assigned]
          if available_pins:
            group_dict[available_pins[0]] = leaf_port
          else:
            group_failed = True

      if not group_failed:
        return group_dict
    return None

class PinAssignmentUtil:
  """Utility for pin assignment, given a list of ports and assignable pin definitions, assigns each leaf CircuitPort
  port to a pin."""
  def __init__(self, *assignables: AssignablePinGroup) -> None:
    self.assignables_by_port = IdentityDict[Port, AssignablePinGroup]()

    for assignable in assignables:
      for port in assignable.get_assignable_ports():
        self.assignables_by_port[port] = assignable

  def assign(self, ports: Iterable[Port], preassigns: IdentityDict[CircuitPort, PinName] = IdentityDict()) ->\
      Dict[ConcretePinName, CircuitPort]:
    assignments: Dict[ConcretePinName, CircuitPort] = {}
    for port in ports:
      port_assignment = self.assignables_by_port[port].assign(port, preassigns, set(assignments.keys()))
      assert port_assignment is not None  # TODO more robust and backtracking
      assignments.update(port_assignment)
    return assignments
