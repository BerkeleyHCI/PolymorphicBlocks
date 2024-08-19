"""
Utility script that crawls a local KiCad installation's library files and builds the table of footprint area.
This file is pregenerated and committed to the repository, and used by the parts tables.
"""
import os
from typing import Dict
import sexpdata  # type: ignore


KICAD_FP_DIRECTORIES = ["C:/Program Files/KiCad/8.0/share/kicad/footprints"]
OUTPUT_FILE = "kicad_footprints.json"


def calculate_area(fp_contents: str) -> float:
    return 0


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
