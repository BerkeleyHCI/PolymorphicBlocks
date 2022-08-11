import os
import unittest

from typing import Type
from . import *
from . import test_netlist
from . import footprint as kicad
from .NetlistGenerator import NetlistTransform


class NetlistTestCase(unittest.TestCase):
  def generate_net(self, design: Type[Block]):
    compiled = ScalaCompiler.compile(design)
    netlist = NetlistTransform(compiled).run()
    return kicad.generate_netlist(netlist.blocks, netlist.nets)

  def test_basic_kicad(self):
    with open(os.path.splitext(os.path.basename(__file__))[0] + '_basic.net', 'w') as f:
      f.write(self.generate_net(test_netlist.TestBasicCircuit))

  def test_multisink_kicad(self):
    with open(os.path.splitext(os.path.basename(__file__))[0] + '_multisink.net', 'w') as f:
      f.write(self.generate_net(test_netlist.TestMultisinkCircuit))

  def test_multinet_kicad(self):
    with open(os.path.splitext(os.path.basename(__file__))[0] + '_multinet.net', 'w') as f:
      f.write(self.generate_net(test_netlist.TestMultinetCircuit))
