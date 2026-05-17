import inspect
import os
from typing import Type
from edg import *


def run_test_board(design: Type[Block]) -> None:
    from edg import compile_board_inplace

    compile_board_inplace(design)

    dirname = os.path.dirname(inspect.getfile(design))
    ref_net_filenames = [
        f[:-4] for f in os.listdir(dirname) if f.startswith(design.__name__) and f.endswith(".net.ref")
    ]
    net_filenames = [f for f in os.listdir(dirname) if f.startswith(design.__name__) and f.endswith(".net")]

    assert set(ref_net_filenames) == set(
        net_filenames
    ), f"reference netlist files {ref_net_filenames} do not match generated netlist files {net_filenames}"

    for net_filename in net_filenames:
        with open(os.path.join(dirname, net_filename), newline=None) as f:
            generated_netlist = f.read()

        with open(os.path.join(dirname, net_filename + ".ref"), newline=None) as f:
            reference_netlist = f.read()

        assert (
            generated_netlist == reference_netlist
        ), f"netlist differs from reference for {design.__name__}, if this is expected you may need to update the reference"
