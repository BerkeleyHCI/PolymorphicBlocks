import argparse
import csv
import math
import os
from typing import Dict, Tuple, Optional

parser = argparse.ArgumentParser(description="Post-process KiCad BoM and position files to be compatible with JLC.")
parser.add_argument(
    "file_path_prefix",
    type=str,
    help="Path prefix to the part data, without the .csv or -top-post.csv postfix, "
    + "for example LedMatrix/gerbers/LedMatrix",
)
parser.add_argument(
    "--merge-boms",
    type=str,
    nargs="*",
    help="BoM CSVs to merge, for panelization. " + "If specified, replaces the BoM CSV in the file_path_prefix.",
)
args = parser.parse_args()


# Correct the rotations on a per-part-number-basis
PART_ROTATIONS = {
    "C425057": -90,  # resistor array 750ohm 4x0603
    "C20197": -90,  # resistor array 1k 4x0603
    "C2962219": -90,  # 2x5 1.27mm header shrouded
}

_FOOTPRINT_ROTATIONS = {
    "Package_TO_SOT_SMD:SOT-23": 180,
    "Package_TO_SOT_SMD:SOT-23-5": 180,
    "Package_TO_SOT_SMD:SOT-23-6": 180,
    "Package_TO_SOT_SMD:SOT-23-8": 180,
    "Package_TO_SOT_SMD:SOT-89-3": 180,
    "Package_TO_SOT_SMD:SOT-323_SC-70": 180,
    "Package_TO_SOT_SMD:SOT-363_SC-70-6": 180,
    "Package_TO_SOT_SMD:SOT-223-3_TabPin2": 180,
    "Package_TO_SOT_SMD:TO-252-2": 180,
    "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm": -90,
    "Package_SO:SOIC-8_5.23x5.23mm_P1.27mm": -90,
    "Package_DFN_QFN:PQFN-8-EP_6x5mm_P1.27mm_Generic": -90,
    "Package_DFN_QFN:UDFN-4-1EP_1x1mm_P0.65mm_EP0.48x0.48mm": -90,
    # note, SMD e-cap are sometimes flipped but are not included here as it's inconsistent
}

# footprint position export doesn't include the footprint library name
PACKAGE_ROTATIONS = {footprint.split(":")[-1]: rot for footprint, rot in _FOOTPRINT_ROTATIONS.items()}

# translational offsets using KiCad coordinate conventions, -y is up
# offsets estimated visually
PART_OFFSETS: Dict[str, Tuple[float, float]] = {}
_FOOTPRINT_OFFSETS: Dict[str, Tuple[float, float]] = {
    "Package_TO_SOT_SMD:SOT-89-3": (-0.6, 0),
    "Package_TO_SOT_SMD:TO-252-2": (-2, 0),
}
PACKAGE_OFFSETS = {footprint.split(":")[-1]: offset for footprint, offset in _FOOTPRINT_OFFSETS.items()}

if __name__ == "__main__":

    def remap_by_dict(elt: str, remap_dict: Dict[str, str]) -> str:
        if elt in remap_dict:
            return remap_dict[elt]
        else:
            return elt

    if args.merge_boms:
        if os.path.exists(f"{args.file_path_prefix}.csv"):  # remove previous one to avoid confusion
            os.remove(f"{args.file_path_prefix}.csv")
        with open(f"{args.file_path_prefix}.csv", "w", newline="") as bom_out:
            merged_csv_out: Optional[csv.DictWriter[str]] = None
            for input_bom_file in args.merge_boms:
                with open(input_bom_file, "r", newline="") as bom_in:
                    csv_dict_in = csv.DictReader(bom_in)
                    if merged_csv_out is None:
                        assert csv_dict_in.fieldnames is not None
                        merged_csv_out = csv.DictWriter(bom_out, fieldnames=csv_dict_in.fieldnames)
                        merged_csv_out.writeheader()
                    for row_dict in csv_dict_in:
                        merged_csv_out.writerow(row_dict)

    # while we don't need to modify the BoM, we do need the JLC P/N to refdes map and
    # hdl-defined rotations / offsets (if specified)
    refdes_lcsc_map: Dict[str, str] = {}  # refdes -> LCSC part number
    refdes_rot_offset: Dict[str, float] = {}  # refdes -> rotational offset  (if specified)
    refdes_offset: Dict[str, Tuple[float, float]] = {}  # refdes -> position offset (if specified)

    with open(f"{args.file_path_prefix}.csv", "r", newline="") as bom_in:
        csv_in = csv.reader(bom_in)

        rows = list(csv_in)
        refdes_list_index = rows[0].index("Designator")
        lcsc_index = rows[0].index("JLCPCB Part #")
        pnp_rot_index = rows[0].index("PNP Rotation Offset")
        pnp_offset_x_index = rows[0].index("PNP Offset X")
        pnp_offset_y_index = rows[0].index("PNP Offset Y")

        for i, row in enumerate(rows[1:]):
            if not row[lcsc_index]:  # ignore rows without part number
                continue
            refdes_list = row[refdes_list_index].split(",")
            for refdes in refdes_list:
                assert refdes not in refdes_lcsc_map, f"duplicate refdes {refdes} in row {i+1}"
                refdes_lcsc_map[refdes] = row[lcsc_index]

            if row[pnp_rot_index]:
                for refdes in refdes_list:
                    refdes_rot_offset[refdes] = float(row[pnp_rot_index])
            if row[pnp_offset_x_index] and row[pnp_offset_y_index]:
                for refdes in refdes_list:
                    refdes_offset[refdes] = (float(row[pnp_offset_x_index]), float(row[pnp_offset_y_index]))

    print(f"read {args.file_path_prefix}.csv")

    # Process position CSV
    POS_HEADER_MAP = {
        "Ref": "Designator",
        "PosX": "Mid X",
        "PosY": "Mid Y",
        "Rot": "Rotation",
        "Side": "Layer",
    }
    for pos_postfix in ["top", "bottom"]:
        with (
            open(f"{args.file_path_prefix}-{pos_postfix}-pos.csv", "r", newline="") as pos_in,
            open(f"{args.file_path_prefix}-{pos_postfix}-pos_jlc.csv", "w", newline="") as pos_out,
        ):
            csv_in = csv.reader(pos_in)
            csv_out = csv.writer(pos_out)

            rows = list(csv_in)
            rows[0] = [remap_by_dict(elt, POS_HEADER_MAP) for elt in rows[0]]

            refdes_index = rows[0].index("Designator")
            package_index = rows[0].index("Package")
            rot_index = rows[0].index("Rotation")
            x_index = rows[0].index("Mid X")
            y_index = rows[0].index("Mid Y")

            csv_out.writerow(rows[0])

            for i, row in enumerate(rows[1:]):
                refdes = row[refdes_index]
                package = row[package_index]
                lcsc_opt = refdes_lcsc_map.get(refdes, None)

                # correct offsets before applying rotation
                if refdes in refdes_offset:
                    xoff, yoff = refdes_offset[refdes]
                    rot = math.radians(float(row[rot_index]))
                    row[x_index] = str((float(row[x_index]) + xoff * math.cos(rot) + yoff * math.sin(rot)))
                    row[y_index] = str((float(row[y_index]) + xoff * math.sin(rot) - yoff * math.cos(rot)))
                    print(f"correct BoM offset for row {i+1} ref {refdes}, {lcsc_opt}")
                elif lcsc_opt is not None and lcsc_opt in PART_OFFSETS:
                    xoff, yoff = PART_OFFSETS[lcsc_opt]
                    rot = math.radians(float(row[rot_index]))
                    row[x_index] = str((float(row[x_index]) + xoff * math.cos(rot) + yoff * math.sin(rot)))
                    row[y_index] = str((float(row[y_index]) + xoff * math.sin(rot) - yoff * math.cos(rot)))
                    print(f"correct offset for row {i+1} ref {refdes}, {lcsc_opt}")
                elif package in PACKAGE_OFFSETS:
                    xoff, yoff = PACKAGE_OFFSETS[package]
                    rot = math.radians(float(row[rot_index]))
                    row[x_index] = str((float(row[x_index]) + xoff * math.cos(rot) + yoff * math.sin(rot)))
                    row[y_index] = str((float(row[y_index]) + xoff * math.sin(rot) - yoff * math.cos(rot)))
                    print(f"correct offset for row {i+1} ref {refdes}, {package}")

                if refdes in refdes_rot_offset:
                    row[rot_index] = str((float(row[rot_index]) + refdes_rot_offset[refdes]) % 360)
                    print(f"correct BoM rotation for row {i+1} ref {refdes}, {lcsc_opt}")
                elif lcsc_opt is not None and lcsc_opt in PART_ROTATIONS:
                    row[rot_index] = str((float(row[rot_index]) + PART_ROTATIONS[lcsc_opt]) % 360)
                    print(f"correct rotation for row {i+1} ref {refdes}, {lcsc_opt}")
                elif package in PACKAGE_ROTATIONS:
                    row[rot_index] = str((float(row[rot_index]) + PACKAGE_ROTATIONS[package]) % 360)
                    print(f"correct rotation for row {i+1} ref {refdes}, {package}")

                csv_out.writerow(row)

        print(f"wrote {args.file_path_prefix}-{pos_postfix}-pos_jlc.csv")
