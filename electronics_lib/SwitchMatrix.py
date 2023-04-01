from electronics_abstract_parts import *


class SwitchMatrix(HumanInterface, GeneratorBlock):
  """A switch matrix that generates (rows * cols) switches while only using max(rows, cols) IOs, by arranging
  them in a matrix, having the driver drive one row high at a time and reading which cols are connected
  (with all cols weakly pulled low).
  This uses the Switch abstract class, which can be refined into e.g. a tactile switch or mechanical keyswitch.

  This generates per-switch diodes which allows multiple keys to be pressed once. Diode anodes are attached to
  the rows, while cathodes go through each switch to the cols.
  """

