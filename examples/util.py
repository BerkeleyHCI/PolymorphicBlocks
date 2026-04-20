import inspect
import os
from typing import Type
from edg import *


def run_test_board(design: Type[Block]) -> None:
    from edg import compile_board_inplace

    compile_board_inplace(design)

    designfile = inspect.getfile(design)
    with open(os.path.join(os.path.dirname(designfile), design.__name__, design.__name__ + ".net"), newline=None) as f:
        generated_netlist = f.read()

    with open(
        os.path.join(os.path.dirname(designfile), design.__name__, design.__name__ + ".net.ref"), newline=None
    ) as f:
        reference_netlist = f.read()

    assert (
        generated_netlist == reference_netlist
    ), f"netlist differs from reference for {design.__name__}, if this is expected you may need to update the reference"
