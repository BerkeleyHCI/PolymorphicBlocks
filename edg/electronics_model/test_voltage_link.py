import unittest

from .VoltagePorts import VoltageLink


class VoltageLinkTestCase(unittest.TestCase):
  def setUp(self):
    self.pb = VoltageLink()._elaborated_def_to_proto()

  def test_metadata(self):
    self.assertIn('nets', self.pb.meta.members.node)
