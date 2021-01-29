from typing import *
import unittest

from . import *
from .test_common import TestPortSink


class TestBundle(Bundle):
  def __init__(self, float_param: FloatLike = FloatExpr(),
               a_float_param: FloatLike = FloatExpr(), b_float_param: FloatLike = FloatExpr()) -> None:
    super().__init__()

    self.float_param = self.Parameter(FloatExpr(float_param))

    # self.a = self.Port(TestPortSink(float_param=a_float_param))
    # self.b = self.Port(TestPortSink(float_param=b_float_param))


class BundleProtoTestCase(unittest.TestCase):
  def setUp(self) -> None:
    self.pb = TestBundle()._def_to_proto()

  def test_contains_param(self) -> None:
    self.assertEqual(len(self.pb.params), 1)
    self.assertTrue(self.pb.params['float_param'].HasField('floating'))

  def test_contains_field(self) -> None:
    self.assertEqual(len(self.pb.ports), 2)
    self.assertEqual(self.pb.ports['a'].lib_elem.target.name, "edg_core.test_common.TestPortSink")
    self.assertEqual(self.pb.ports['b'].lib_elem.target.name, "edg_core.test_common.TestPortSink")
