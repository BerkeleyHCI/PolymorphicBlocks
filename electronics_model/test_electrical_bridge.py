from typing import *
import unittest

from edg_core import *
from .ElectricalPorts import ElectricalSinkBridge


class ElectricalBridgeTestCase(unittest.TestCase):
  def setUp(self):
    self.pb = ElectricalSinkBridge()._elaborated_def_to_proto()

  def test_metadata(self):
    self.assertIn('nets', self.pb.meta.members.node)