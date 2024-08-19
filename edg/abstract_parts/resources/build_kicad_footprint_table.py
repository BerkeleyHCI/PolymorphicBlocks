"""
Utility script that crawls a local KiCad installation's library files and builds the table of footprint area.
This file is pregenerated and committed to the repository, and used by the parts tables.
"""
import os
from typing import Dict, List, Tuple, Any
import sexpdata  # type: ignore


KICAD_FP_DIRECTORIES = ["C:/Program Files/KiCad/8.0/share/kicad/footprints"]
OUTPUT_FILE = "resources/kicad_footprints.json"


def sexp_list_find_all(container: list, key: str) -> List[List[Any]]:
    """Given a sexp list, return all elements which are lists where the first element is a symbol of key."""
    matching_elts = []
    for elt in container:
        if isinstance(elt, list) and elt and \
                isinstance(elt[0], sexpdata.Symbol) and elt[0].value() == key:
            matching_elts.append(elt)
    return matching_elts


def calculate_area(fp_contents: str) -> float:
    fp_top: List[Any] = sexpdata.loads(fp_contents)
    assert isinstance(fp_top[0], sexpdata.Symbol) and fp_top[0].value() == 'footprint'

    # gather all expressions with type fp_line and layer F.CrtYd, and parse XYs
    fp_lines: List[Tuple[Tuple[float, float], Tuple[float, float]]] = []  # startx, stary, endx, endy
    for fp_line_elt in sexp_list_find_all(fp_top, 'fp_line'):
        layers = sexp_list_find_all(fp_line_elt, 'layer')
        assert len(layers) == 1
        if layers[0][1] != 'F.CrtYd':
            continue
        start = sexp_list_find_all(fp_line_elt, 'start')
        end = sexp_list_find_all(fp_line_elt, 'end')
        assert len(start) == 1 and len(end) == 1 and len(start[0]) == 3 and len(end[0]) == 3
        fp_lines.append(((float(start[0][1]), float(start[0][2])), (float(end[0][1]), float(end[0][2]))))

    print(fp_lines)

    return 0.0


if __name__ == "__main__":
    fp_area_dict: Dict[str, float] = {}  # footprint name -> area
    for kicad_dir in KICAD_FP_DIRECTORIES:
        for dir, subdirs, _ in os.walk(kicad_dir):
            for subdir in subdirs:
                lib_name = subdir.split('.pretty')[0]
                for subdir, _, files in os.walk(os.path.join(dir, subdir)):
                    for file in files:
                        fp_name = file.split('.kicad_mod')[0]
                        with open(os.path.join(subdir, file)) as f:
                            fp_area = calculate_area(f.read())
                        print(f"{lib_name}:{fp_name} -> {fp_area}")
                        assert False
