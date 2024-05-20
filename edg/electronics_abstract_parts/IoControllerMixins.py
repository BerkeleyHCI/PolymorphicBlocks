from .IoController import IoController
from .AbstractCrystal import OscillatorReference
from electronics_model import *


@non_library
class WithCrystalGenerator(IoController, GeneratorBlock):
  """A Block generator mixin that checks if a crystal oscillator is needed, and if so generates it."""
  DEFAULT_CRYSTAL_FREQUENCY: Range

  @init_in_parent
  def __init__(self):
    super().__init__()
    self.xtal_node = self.connect()  # connect this internal node to the microcontroller; this may be empty

  def _crystal_required(self) -> bool:
    """Integration point to determine whether a crystal is required.
    Called within generate, has access to generator params."""
    return False

  def generate(self):
    super().generate()
    if self._crystal_required():
      self.crystal = self.Block(OscillatorReference(self.DEFAULT_CRYSTAL_FREQUENCY))
      self.connect(self.crystal.gnd, self.gnd)
      self.connect(self.xtal_node, self.crystal.crystal)
