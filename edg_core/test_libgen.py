from typing import *
import unittest

from . import test_common, test_hierarchy_block
from . import *

class LibGenTestCase(unittest.TestCase):
  def test_library_detect(self):
    pb = Driver([test_common, test_hierarchy_block]).generate_library_proto()
    pb_keys = pb.root.members.keys()

    self.assertIn('edg_core.test_common.TestLink', pb_keys)
    self.assertIn('edg_core.test_common.TestPortBridge', pb_keys)
    self.assertIn('edg_core.test_common.TestPortBase', pb_keys)
    self.assertIn('edg_core.test_common.TestPortSink', pb_keys)
    self.assertIn('edg_core.test_common.TestPortSource', pb_keys)

    self.assertIn('edg_core.test_common.TestBlockSink', pb_keys)
    self.assertIn('edg_core.test_common.TestBlockSource', pb_keys)
    self.assertIn('edg_core.test_hierarchy_block.TopHierarchyBlock', pb_keys)
