"""Independent KiCad XML-netlist acceptance checks for generated schematic views."""

from pathlib import Path
import xml.etree.ElementTree as ET

from .NetlistGenerator import Netlist


def verify_schematic_netlist(expected: Netlist, exported_xml: Path) -> None:
    """Compare KiCad's `sch export netlist --format kicadxml` output to PB.

    Ignore net names and singleton-net omission, but verify the library pin inventory,
    component/footprint identity, and exact partition of connected physical pins.
    Raises ValueError on mismatch. Run once for each independent board scope.
    """
    root = ET.parse(exported_xml).getroot()
    components = {c.attrib["ref"]: c for c in root.findall("./components/comp")}
    blocks = {b.refdes: b for b in expected.blocks}
    if set(components) != set(blocks):
        raise ValueError("schematic component identities differ from PB")
    library_parts = {(p.attrib["lib"], p.attrib["part"]): p for p in root.findall("./libparts/libpart")}
    path_refs = {str(b.full_path): ref for ref, b in blocks.items()}
    expected_pins = {ref: set() for ref in blocks}
    expected_nets = set()
    for net in expected.nets:
        pins = frozenset((path_refs[str(p.block_path)], p.pin_name) for p in net.pins)
        for ref, pin in pins:
            expected_pins[ref].add(pin)
        if len(pins) > 1:
            expected_nets.add(pins)
    # Include modeled pins that the netlister might omit from singleton nets by reading
    # the generated symbol inventory separately in extraction tests.
    for ref, comp in components.items():
        if (comp.findtext("footprint") or "") != blocks[ref].footprint:
            raise ValueError("footprint mismatch: " + ref)
        source = comp.find("libsource")
        if source is None:
            raise ValueError("missing library pin inventory: " + ref)
        part = library_parts[(source.attrib["lib"], source.attrib["part"])]
        actual = {pin.attrib["num"] for pin in part.findall("./pins/pin")}
        if actual != expected_pins[ref]:
            raise ValueError("physical pin inventory mismatch: " + ref)
    actual_nets = set()
    seen = set()
    for net in root.findall("./nets/net"):
        pins = frozenset((p.attrib["ref"], p.attrib["pin"]) for p in net.findall("node"))
        if seen.intersection(pins):
            raise ValueError("physical pin occurs on multiple nets")
        seen.update(pins)
        if len(pins) > 1:
            actual_nets.add(pins)
    if actual_nets != expected_nets:
        raise ValueError("schematic connectivity differs from PB (merged, split, missing, or extra net)")
