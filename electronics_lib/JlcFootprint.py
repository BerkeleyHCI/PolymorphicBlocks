from electronics_abstract_parts import *

class JlcFootprint(Block):
    def __init__(self):
        super().__init__()
        self.lcsc_part = self.Parameter(StringExpr())
