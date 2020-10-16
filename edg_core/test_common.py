from typing import *
import os

from . import *

"""Example EDG input definitions (ports, links, blocks) for unit testing features.

The common port base (abstract-ish) contains:
- a float param (float_param, in(source)/out(sink)), optionally initialized, where the link creates the range spanning values

The source port contains:
- a range param (float_param_limit, limit), optionally initialized, that my float_param must be in
- a range param (range_param, output), optionally initialized 

The sink ports contains:
- a range param (range_limit, output), optionally initialized, that the source's range_param must be in

The port bridge, an external-facing-sink to internal-facing-source adapter does:
- float_param: propagates internal-source float_param to external-sink float_param
- range_param: propagates the intersection of the range_param of the link sinks
  TODO: is this a good abstraction, going directly into the link? the problem is also artificial
  Or perhaps this should be recommended practice, with the port type for type checking only

Note: under current semantics, ports cannot have constraints

The link does:
- calculates a float_param (float_param_sink_sum) that is the sum of sinks' float_param 
- calculates a range_param (float_param_sink_range) that is the range of all ports' float_param
- sums float_params and ensures they balance to zero
- ensures source float_param_limit is respected (constraint on source only)
- ensures sink range_limit is respected (constraint between source and sinks)
- calculates a range_param (range_limit_sink_common) that is the intersection of all sinks' range_limit
"""


class TestLink(Link):
  def __init__(self) -> None:
    super().__init__()
    self.source = self.Port(TestPortSource(), optional=True)
    self.sinks = self.Port(Vector(TestPortSink()), optional=True)

    self.float_param_sink_sum = self.Parameter(FloatExpr(self.sinks.sum(lambda p: p.float_param)))
    self.float_param_sink_range = self.Parameter(RangeExpr())
    self.constrain(self.float_param_sink_range.lower() == self.sinks.min(lambda p: p.float_param))
    self.constrain(self.float_param_sink_range.upper() == self.sinks.max(lambda p: p.float_param))
    self.range_param_sink_common = self.Parameter(RangeExpr(self.sinks.intersection(lambda p: p.range_limit)))

    self.constrain(self.float_param_sink_sum - self.source.float_param == 0)
    self.constrain(self.source.float_param_limit.contains(self.source.float_param))
    self.constrain(self.range_param_sink_common.contains(self.source.range_param))


class TestPortBase(Port[TestLink]):
  def __init__(self, float_param: FloatLike = FloatExpr()) -> None:
    super().__init__()
    self.float_param = self.Parameter(FloatExpr(float_param))
    self.link_type = TestLink


class TestPortSource(TestPortBase):
  def __init__(self, float_param_limit: RangeLike = RangeExpr(), range_param: RangeLike = RangeExpr(), float_param: FloatLike = FloatExpr()) -> None:
    super().__init__(float_param)
    self.float_param_limit = self.Parameter(RangeExpr(float_param_limit))
    self.range_param = self.Parameter(RangeExpr(range_param))


class TestPortSink(TestPortBase):
  def __init__(self, range_limit: RangeLike = RangeExpr(), float_param: FloatLike = FloatExpr()) -> None:
    super().__init__(float_param)
    self.bridge_type = TestPortBridge

    self.range_limit = self.Parameter(RangeExpr(range_limit))


class TestPortBridge(PortBridge):
  def __init__(self) -> None:
    super().__init__()
    self.outer_port = self.Port(TestPortSink())
    self.inner_link = self.Port(TestPortSource())

    self.constrain(self.outer_port.float_param == self.inner_link.link().float_param_sink_sum)
    self.constrain(self.outer_port.range_limit == self.inner_link.link().range_param_sink_common)


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
