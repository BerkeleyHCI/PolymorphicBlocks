from electronics_model import *


@abstract_block
class PinMappableChip(Block):
  """
  Goal: given a pin map description for a chip, map the leaf CircuitPorts to pin numbers which can be used in the
  footprint() block.

  TODO: how to support mutex concerns (ADC / DigitalPorts)? how to support different ports of the same type (eg, 5v tolerant)

  Idea of layers?
  Description layer
  - Pin layer (leaf level - ADC capable, DAC capable, digital IO - incl different voltages)
    - "these pins have these IO models"
  - Peripheral layer (which bundles can map where - leaves must be connectable)
    - Problem: no support for heterogeneous models in peripherals
    - use init_from support? esp in bundle elts?



  Mapping layer
  - Take in ports with suggested-names, returns two mappings:
    - a mapping of pin number to leaf ports - can be directly passed into footprint
    - a mapping of ports to port model - used as initializers
      - this includes both leaves and bundles, so either the leaves will be empty,
        or the bundles will have its member ports be empty so they can be initialized
        from leaves (allowing differentiated IOs)

  """
  def __init__(self) -> None:
    super().__init__()