from typing import *
import unittest

from . import test_common, test_hierarchy_block  # needed for library detection
from . import edgir
from .HdlInterfaceServer import LibraryElementResolver
import importlib


class LibGenTestCase(unittest.TestCase):
  def test_library_detect(self):
    lib = LibraryElementResolver()
    lib.load_module(importlib.import_module(self.__module__))

    self.assertIsNotNone(lib.class_from_path(edgir.libpath('edg_core.test_common.TestLink')))
    self.assertIsNotNone(lib.class_from_path(edgir.libpath('edg_core.test_common.TestPortBridge')))
    self.assertIsNotNone(lib.class_from_path(edgir.libpath('edg_core.test_common.TestPortBase')))
    self.assertIsNotNone(lib.class_from_path(edgir.libpath('edg_core.test_common.TestPortSink')))
    self.assertIsNotNone(lib.class_from_path(edgir.libpath('edg_core.test_common.TestPortSource')))

    self.assertIsNotNone(lib.class_from_path(edgir.libpath('edg_core.test_common.TestBlockSink')))
    self.assertIsNotNone(lib.class_from_path(edgir.libpath('edg_core.test_common.TestBlockSource')))
    self.assertIsNotNone(lib.class_from_path(edgir.libpath('edg_core.test_hierarchy_block.TopHierarchyBlock')))
