from . import *

"""Common components for elaboration test, where there are parameters defined, 
but do not make a valid compilation problem"""


class TestLinkBase(Link):
    """Inheritance base for TestLink"""
    def __init__(self) -> None:
        super().__init__()


class TestLink(TestLinkBase):
    def __init__(self) -> None:
        super().__init__()
        self.source = self.Port(TestPortSource(), optional=True)
        self.sinks = self.Port(Vector(TestPortSink()), optional=True)

        self.float_param_sink_sum = self.Parameter(FloatExpr(self.sinks.sum(lambda p: p.float_param)))
        self.float_param_sink_range = self.Parameter(RangeExpr())
        self.assign(self.float_param_sink_range,
                    (self.sinks.min(lambda p: p.float_param), self.sinks.max(lambda p: p.float_param)))
        self.range_param_sink_common = self.Parameter(RangeExpr(self.sinks.intersection(lambda p: p.range_limit)))

        self.require(self.float_param_sink_sum - self.source.float_param == 0)
        self.require(self.source.float_param_limit.contains(self.source.float_param))
        self.require(self.range_param_sink_common.contains(self.source.range_param))


class TestPortBase(Port[TestLink]):
    link_type = TestLink

    def __init__(self, float_param: FloatLike = FloatExpr()) -> None:
        super().__init__()
        self.float_param = self.Parameter(FloatExpr(float_param))


class TestPortSource(TestPortBase):
    def __init__(self, float_param_limit: RangeLike = RangeExpr(), range_param: RangeLike = RangeExpr(), float_param: FloatLike = FloatExpr()) -> None:
        super().__init__(float_param)
        self.float_param_limit = self.Parameter(RangeExpr(float_param_limit))
        self.range_param = self.Parameter(RangeExpr(range_param))


class TestPortBridge(PortBridge):
    def __init__(self) -> None:
        super().__init__()
        self.outer_port = self.Port(TestPortSink())
        self.inner_link = self.Port(TestPortSource())

        self.assign(self.outer_port.float_param, self.inner_link.link().float_param_sink_sum)
        self.assign(self.outer_port.range_limit, self.inner_link.link().range_param_sink_common)


class TestPortSink(TestPortBase):
    bridge_type = TestPortBridge

    def __init__(self, range_limit: RangeLike = RangeExpr(), float_param: FloatLike = FloatExpr()) -> None:
        super().__init__(float_param)
        self.range_limit = self.Parameter(RangeExpr(range_limit))


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
