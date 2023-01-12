import os
import unittest
from typing import Type

from . import *
from . import test_netlist
from .RefdesRefinementPass import RefdesRefinementPass
from .BomBackend import GenerateBom


class NetlistTestCase(unittest.TestCase):
  def generate_net(self, design: Type[Block]):
    compiled = ScalaCompiler.compile(design)
    compiled.append_values(RefdesRefinementPass().run(compiled))

    return NetlistBackend().run(compiled)[0][1], GenerateBom().run(compiled)[0][1]

  def test_basic_kicad(self):
    with open(os.path.splitext(os.path.basename(__file__))[0] + '_basic.net', 'w') as f:
      f.write(self.generate_net(test_netlist.TestBasicCircuit)[0])

    with open(os.path.splitext(os.path.basename(__file__))[0] + '_basic.csv', 'w') as f:
      f.write(self.generate_net(test_netlist.TestBasicCircuit)[1])

  def test_multisink_kicad(self):
    with open(os.path.splitext(os.path.basename(__file__))[0] + '_multisink.net', 'w') as f:
      f.write(self.generate_net(test_netlist.TestMultisinkCircuit)[0])

    with open(os.path.splitext(os.path.basename(__file__))[0] + '_multisink.csv', 'w') as f:
      f.write(self.generate_net(test_netlist.TestMultisinkCircuit)[1])

  def test_multinet_kicad(self):
    with open(os.path.splitext(os.path.basename(__file__))[0] + '_multinet.net', 'w') as f:
      f.write(self.generate_net(test_netlist.TestMultinetCircuit)[0])

    with open(os.path.splitext(os.path.basename(__file__))[0] + '_multinet.csv', 'w') as f:
      f.write(self.generate_net(test_netlist.TestMultinetCircuit)[1])
