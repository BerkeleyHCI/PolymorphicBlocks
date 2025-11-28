import unittest

from typing_extensions import override

from .VoltagePorts import VoltageLink


class VoltageLinkTestCase(unittest.TestCase):
  @override
  def setUp(self) -> None:
    self.pb = VoltageLink()._elaborated_def_to_proto()

  def test_metadata(self) -> None:
    self.assertIn('nets', self.pb.meta.members.node)
