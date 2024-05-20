from typing import *
import unittest

from edg_core import *
from .VoltagePorts import VoltageSinkBridge


class VoltageBridgeTestCase(unittest.TestCase):
  def setUp(self):
    self.pb = VoltageSinkBridge()._elaborated_def_to_proto()

  def test_metadata(self):
    self.assertIn('nets', self.pb.meta.members.node)