from .HierarchyBlock import Block
from .Refinements import Refinements

class DesignTop(Block):
  """A top-level design, which may not have ports (including exports), but may define definements.
  Subclasses should define refinements by stacking new refinements on a super().refinements() call.

  TODO: also support generators?
  """
  def Port(self, *args, **kwargs):
    raise ValueError("Can't create ports on design top")

  def Export(self, *args, **kwargs):
    raise ValueError("Can't create ports on design top")

  def refinements(self) -> Refinements:
    return Refinements()
