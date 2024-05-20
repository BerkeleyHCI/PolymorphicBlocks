from typing import *
import os

from . import *

"""Example EDG input definitions (ports, links, blocks) for unit testing structural compilation.
Does not include parameters and constraints, which should be tested separately
"""


class TestLink(Link):
  def __init__(self) -> None:
    super().__init__()
    self.source = self.Port(TestPortSource(), optional=True)
    self.sinks = self.Port(Vector(TestPortSink()), optional=True)


class TestPortBase(Port[TestLink]):
  link_type = TestLink


class TestPortSource(TestPortBase):
  pass


class TestPortBridge(PortBridge):
  def __init__(self) -> None:
    super().__init__()
    self.outer_port = self.Port(TestPortSink())
    self.inner_link = self.Port(TestPortSource())


class TestPortSink(TestPortBase):
  bridge_type = TestPortBridge


class TestBlockSink(Block):
  def __init__(self) -> None:
    super().__init__()
    self.sink = self.Port(TestPortSink(), optional=True)


ImplicitSink = PortTag(TestPortSink)


class TestBlockImplicitSink(Block):
  def __init__(self) -> None:
    super().__init__()
    self.sink = self.Port(TestPortSink(), [ImplicitSink])


class TestBlockSource(Block):
  def __init__(self) -> None:
    super().__init__()
    self.source = self.Port(TestPortSource(), optional=True)


def problem_name_from_module_file(file: str) -> str:
  return os.path.splitext(os.path.basename(file))[0] + '.edg'
