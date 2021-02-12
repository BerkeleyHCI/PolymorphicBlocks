from typing import Type

import os
import inspect

from edg import Block
from edg.BoardCompiler import compile_board

def run_test(top: Type[Block]):
  compile_board(top,
                os.path.join(os.path.dirname(inspect.getfile(top)), top.__module__.split(".")[-1]),
                top.__name__)
