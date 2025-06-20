"""
Utility script that crawls a local KiCad installation's library files and builds the table of footprint area.
This file is pregenerated and committed to the repository, and used by the parts tables.
"""
import os
from typing import Dict, List, Tuple, Any, Optional
import sexpdata  # type: ignore
from pydantic import RootModel, BaseModel

KICAD_FP_DIRECTORIES = ["C:/Program Files/KiCad/8.0/share/kicad/footprints"]
OUTPUT_FILE = "kicad_footprints.json"


Point = Tuple[float, float]
Line = Tuple[Point, Point]  # start, end


def lines_to_closed_path(lines: List[Line]) -> Optional[List[Line]]:
    """Given a set of unordered lines, returns them ordered in a closed path, starting with the first line"""
    adjacency: Dict[Point, List[Point]] = {}  # bidirectional
    if len(lines) < 2:
        return None
    for line in lines[1:]:  # element 0 is anchor
        adjacency.setdefault(line[0], []).append(line[1])
        adjacency.setdefault(line[1], []).append(line[0])
    closed_path = [lines[0]]
    while closed_path[-1][1] != closed_path[0][0]:  # while the path is not closed
        last_point = closed_path[-1][1]
        adjacent_points = adjacency.get(last_point, [])
        if len(adjacent_points) != 1:  # ambiguous next point
            return None
        this_point = adjacent_points.pop()
        closed_path.append((last_point, this_point))
        adjacency[this_point].remove(last_point)
        if not adjacency[this_point]:
            del adjacency[this_point]
        if not adjacency[last_point]:
            del adjacency[last_point]
    if len(adjacency) > 0:  # unused points not handled
        return None
    return closed_path


def polygon_lines_area(lines: List[Line]) -> Optional[float]:
    """return the area enclosed by a set of lines (potentially unordered) forming a closed path
    from https://www.geeksforgeeks.org/slicker-algorithm-to-find-the-area-of-a-polygon-in-java/
    """
    closed_path = lines_to_closed_path(lines)
    if closed_path is None:
        return None
    sum: float = 0
    for line in closed_path:
        sum += line[1][0] * line[0][1] - line[0][0] * line[1][1]
    return abs(sum) / 2


def sexp_list_find_all(container: list, key: str) -> List[List[Any]]:
    """Given a sexp list, return all elements which are lists where the first element is a symbol of key."""
    matching_elts = []
    for elt in container:
        if isinstance(elt, list) and elt and \
                isinstance(elt[0], sexpdata.Symbol) and elt[0].value() == key:
            matching_elts.append(elt)
    return matching_elts


def calculate_area(fp_contents: str) -> Optional[float]:
    fp_top: List[Any] = sexpdata.loads(fp_contents)
    assert isinstance(fp_top[0], sexpdata.Symbol) and fp_top[0].value() == 'footprint'

    # gather all expressions with type fp_line and layer F.CrtYd, and parse XYs
    fp_lines: List[Line] = []
    for fp_line_elt in sexp_list_find_all(fp_top, 'fp_line'):
        layers = sexp_list_find_all(fp_line_elt, 'layer')
        assert len(layers) == 1
        if layers[0][1] != 'F.CrtYd':
            continue
        start = sexp_list_find_all(fp_line_elt, 'start')
        end = sexp_list_find_all(fp_line_elt, 'end')
        assert len(start) == 1 and len(end) == 1 and len(start[0]) == 3 and len(end[0]) == 3
        fp_lines.append(((float(start[0][1]), float(start[0][2])),
                         (float(end[0][1]), float(end[0][2]))))

    area_opt = polygon_lines_area(fp_lines)
    if area_opt is not None:
        area_opt = round(area_opt, 6)  # round to remove excess precision
    return area_opt


def calculate_bbox(fp_contents: str) -> Optional[Tuple[float, float, float, float]]:  # x_min, y_min, x_max, y_max
    fp_top: List[Any] = sexpdata.loads(fp_contents)
    assert isinstance(fp_top[0], sexpdata.Symbol) and fp_top[0].value() == 'footprint'

    min_x = min_y = float('inf')
    max_x = max_y = float('-inf')

    # gather all expressions with type fp_line and layer F.CrtYd, and parse XYs
    for fp_line_elt in sexp_list_find_all(fp_top, 'fp_line'):
        layers = sexp_list_find_all(fp_line_elt, 'layer')
        assert len(layers) == 1
        if layers[0][1] != 'F.CrtYd':
            continue
        start = sexp_list_find_all(fp_line_elt, 'start')
        end = sexp_list_find_all(fp_line_elt, 'end')
        assert len(start) == 1 and len(end) == 1 and len(start[0]) == 3 and len(end[0]) == 3
        min_x = min(min_x, float(start[0][1]), float(end[0][1]))
        max_x = max(max_x, float(start[0][1]), float(end[0][1]))
        min_y = min(min_y, float(start[0][2]), float(end[0][2]))
        max_y = max(max_y, float(start[0][2]), float(end[0][2]))

    if min_x == float('inf') or min_y == float('inf') or max_x == float('-inf') or max_y == float('-inf'):
        return None
    return min_x, min_y, max_x, max_y


class FootprintData(BaseModel):
    area: float
    bbox: List[float]  # [x_min, y_min, x_max, y_max]


class FootprintJson(RootModel):  # script relpath imports are weird so this is duplicated here
    root: dict[str, FootprintData]  # footprint name -> data


if __name__ == "__main__":
    fp_data_dict: Dict[str, FootprintData] = {}
    for kicad_dir in KICAD_FP_DIRECTORIES:
        for dir, subdirs, _ in os.walk(kicad_dir):
            for subdir in subdirs:
                lib_name = subdir.split('.pretty')[0]
                for subdir, _, files in os.walk(os.path.join(dir, subdir)):
                    for file in files:
                        fp_filename = file.split('.kicad_mod')[0]
                        with open(os.path.join(subdir, file)) as f:
                            fp_data = f.read()
                        fp_area = calculate_area(fp_data)
                        fp_bbox = calculate_bbox(fp_data)

                        if fp_area is not None and fp_bbox is not None:
                            fp_name = lib_name + ":" + fp_filename
                            fp_data_dict[fp_name] = FootprintData(
                                area=fp_area,
                                bbox=fp_bbox
                            )
                            print(f"  {fp_name} -> {fp_area:.3g}, {fp_bbox}")
                        else:
                            print(f"skip {fp_name}")
    json = FootprintJson(fp_data_dict)
    with open(OUTPUT_FILE, 'w') as f:
        f.write(json.model_dump_json(indent=2))
