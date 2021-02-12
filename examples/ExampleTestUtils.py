from typing import Type

from edg import Block
from edg.BoardCompiler import compile_board

def run_test(top: Type[Block]):
  compile_board(top, top.__module__, top.__name__)
