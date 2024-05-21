import unittest
from typing import cast

from .. import edgir
from .test_elaboration_common import TestPortBase, TestPortSource


class PortProtoTestCase(unittest.TestCase):
  def setUp(self):
    self.pb = cast(edgir.Port, TestPortBase()._def_to_proto())  # TODO eliminate cast

  def test_contains_param(self):
    self.assertEqual(len(self.pb.params), 1)
    self.assertEqual(self.pb.params[0].name, 'float_param')
    self.assertTrue(self.pb.params[0].value.HasField('floating'))


class PortSourceProtoTestCase(unittest.TestCase):
  def setUp(self):
    self.pb = cast(edgir.Port, TestPortSource()._def_to_proto())

  def test_self_class(self):
    self.assertEqual(self.pb.self_class.target.name, "edg.core.test_elaboration_common.TestPortSource")

  def test_superclasses(self):
    self.assertEqual(len(self.pb.superclasses), 1)
    self.assertEqual(self.pb.superclasses[0].target.name, "edg.core.test_elaboration_common.TestPortBase")

  def test_contains_param(self):
    self.assertEqual(len(self.pb.params), 3)
    self.assertTrue(self.pb.params[0].name, 'float_param')
    self.assertTrue(self.pb.params[0].value.HasField('floating'))
    self.assertTrue(self.pb.params[1].name, 'float_param_limit')
    self.assertTrue(self.pb.params[1].value.HasField('range'))
    self.assertTrue(self.pb.params[2].name, 'range_param')
    self.assertTrue(self.pb.params[2].value.HasField('range'))
