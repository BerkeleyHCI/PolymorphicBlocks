import unittest

from typing_extensions import override

from ..core import *
from .VoltagePorts import VoltageSinkBridge


class VoltageBridgeTestCase(unittest.TestCase):
  @override
  def setUp(self) -> None:
    self.pb = VoltageSinkBridge()._elaborated_def_to_proto()

  def test_metadata(self) -> None:
    self.assertIn('nets', self.pb.meta.members.node)