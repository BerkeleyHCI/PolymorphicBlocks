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

  Concept of hierarchical assignable resources?
  Each incoming port can be assigned to a resource. Resources are hierarchical / recursive.
  Each resource can only be claimed by one port (used once).
  TODO: is it ever needed to uspport some kind of mutual exclusion between several resources?
  Resources are first-order matched based on types.
  Each resource, given a resource manager reference, can assess whether it can be assigned.
  Bundle elements can be recursively delegated.
  eg, LPC1549
  [
    # Pin "resource"
    Pin_OneOf('1', 'PIO0_0', [analog_model, digital5v_model])  # ADC capable
    Pin_OneOf('2', 'PIO0_1', [digital5v_model])  # not ADC capable
    ...
    # Peripheral "resource" - name only - switch matrix, IOs delegated
    # Hierarchical? Automatically assign to compatible leaf type, optionally with assigned pins
    Peripheral_SWM('SPI0', spimaster_model)
    # Peripheral "resource" - fixed pins
    Peripheral_Fixed('I2C0', {'sda': '44', 'scl': '45'}, i2c_model)
    # TBD: how to handle
  ]

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