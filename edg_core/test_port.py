import unittest
from typing import cast
from . import edgir

from .test_elaboration_common import TestPortBase, TestPortSource


class PortProtoTestCase(unittest.TestCase):
  def setUp(self):
    self.pb = cast(edgir.Port, TestPortBase()._def_to_proto())  # TODO eliminate cast

  def test_contains_param(self):
    self.assertEqual(len(self.pb.params), 1)
    self.assertTrue(self.pb.params['float_param'].HasField('floating'))


class PortSourceProtoTestCase(unittest.TestCase):
  def setUp(self):
    self.pb = cast(edgir.Port, TestPortSource()._def_to_proto())

  def test_superclass(self):
    self.assertEqual(len(self.pb.superclasses), 1)
    self.assertEqual(self.pb.superclasses[0].target.name, "edg_core.test_elaboration_common.TestPortBase")

    self.assertTrue(self.pb.params['float_param'].HasField('floating'))

  def test_contains_param(self):
    self.assertEqual(len(self.pb.params), 3)
    self.assertTrue(self.pb.params['float_param_limit'].HasField('range'))
    self.assertTrue(self.pb.params['range_param'].HasField('range'))
