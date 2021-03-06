import os
import unittest

from typing import Type
from edg_core import *
import electronics_model
from . import *
from . import test_netlist
from . import footprint as kicad


class NetlistTestCase(unittest.TestCase):
  def generate_net(self, design: Type[Block]):
    compiled = ScalaCompiler.compile(design)
    net = NetlistGenerator().generate(compiled)
    return kicad.generate_netlist(net.blocks, net.nets)

  def test_basic_kicad(self):
    with open(os.path.splitext(os.path.basename(__file__))[0] + '_basic.net', 'w') as f:
      f.write(self.generate_net(test_netlist.TestBasicCircuit))

  def test_multisink_kicad(self):
    with open(os.path.splitext(os.path.basename(__file__))[0] + '_multisink.net', 'w') as f:
      f.write(self.generate_net(test_netlist.TestMultisinkCircuit))

  def test_multinet_kicad(self):
    with open(os.path.splitext(os.path.basename(__file__))[0] + '_multinet.net', 'w') as f:
      f.write(self.generate_net(test_netlist.TestMultinetCircuit))
