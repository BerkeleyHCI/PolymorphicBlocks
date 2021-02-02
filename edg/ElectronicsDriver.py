from typing import *
from types import ModuleType
import os
import pickle
import copy
import zlib
from contextlib import suppress

from electronics_model import footprint
import electronics_model
import electronics_abstract_parts
from electronics_lib import *
import electronics_lib
import edg_core.TransformUtil as tfu
from edg_core import CheckErrorsTransform


def type_to_lib_path(elt: Type[Block]) -> edgir.LibraryPath:
  out = edgir.LibraryPath()
  out.target.name = elt._static_def_name()
  return out

# TODO should technically be a class method?
def create_remap_dict(remap: Dict[Type[Block], Type[Block]]) -> Dict[bytes, bytes]:
  def create_remap_elt(src: Type[Block], dst: Type[Block]) -> Tuple[edgir.LibraryPath, edgir.LibraryPath]:
    # TODO unify with something in Block that returns a LibraryPath?
    return (type_to_lib_path(src), type_to_lib_path(dst))
  remap_elts = [create_remap_elt(src, dst) for src, dst in remap.items()]
  return {k.SerializeToString(): v.SerializeToString() for k, v in remap_elts}


DefaultRefinement = DesignRefinement(
  class_refinements=create_remap_dict({
    Resistor: ChipResistor,
    Capacitor: SmtCeramicCapacitor,
    Inductor: SmtInductor,
    Switch: SmtSwitch,
    Diode: SmtDiode,
    Led: SmtLed,
    RgbLedCommonAnode: SmtRgbLed,
    ZenerDiode: SmtZenerDiode,
    NFet: SmtNFet,
    PFet: SmtPFet,
    SwitchNFet: SmtSwitchNFet,
    SwitchPFet: SmtSwitchPFet,
  }), instance_refinements={
  }
)


class ElectronicsDriver(Driver):
  """Driver that does instantiation of generic blocks"""
  def __init__(self, libs: Iterable[ModuleType] = [], raw_defs: Dict[str, edgir.EltTypes] = {}) -> None:
    # libraries are separated to allow earlier ones to be cached
    super().__init__(list(libs) + [electronics_model, electronics_abstract_parts, electronics_lib], raw_defs)

  def _schematic_contents(self, children: List[Tuple[str, str]]) -> str:  # name -> type
    def child_to_str(name: str, type_name: str) -> str:
      return f"""
$Sheet
S 0 0 0 0 
U {name}
F0 "{name}" 0
F1 "{type_name}.sch" 0
$EndSheet
      """

    child_strs = '\n\n'.join([child_to_str(name, type_name) for name, type_name in children])

    return f"""
EESchema Schematic File Version 2
EELAYER 25 0
EELAYER END

{child_strs}

$EndSCHEMATC
"""

  def generate_write_block(self, block: Block, target_dir: str,
                           constrs: Dict[tfu.Path, edgir.LitTypes] = {},
                           instance_refinements: Dict[tfu.Path, Type[Block]] = {},
                           continue_on_error=True) -> None:
    if not os.path.exists(target_dir):
      os.makedirs(target_dir)
    assert os.path.isdir(target_dir), f"target_dir {target_dir} to generator_write_block must be directory"

    library_filename = os.path.join(target_dir, 'lib.lib')
    design_raw_filename = os.path.join(target_dir, 'design_raw.edg')
    design_filename = os.path.join(target_dir, 'design.edg')
    entlist_filename = os.path.join(target_dir, 'netlist.net')

    # clear existing files to prevent stale files in case of errors
    with suppress(FileNotFoundError):
      os.remove(library_filename)
    with suppress(FileNotFoundError):
      os.remove(design_raw_filename)
    with suppress(FileNotFoundError):
      os.remove(design_filename)
    with suppress(FileNotFoundError):
      os.remove(entlist_filename)

    raw_design = self.elaborate_toplevel(block)
    with open(design_raw_filename, 'wb') as raw_file:
      raw_file.write(raw_design.SerializeToString())

    refinements_filename = os.path.join(target_dir, "refinement.edgr")
    if os.path.exists(refinements_filename):
      with open(refinements_filename, "rb") as f:
        refinements: Optional[DesignRefinement] = pickle.load(f)
        assert isinstance(refinements, DesignRefinement)
    else:
      refinements = DefaultRefinement

    refinements = copy.deepcopy(refinements)
    refinements.param_settings.update(constrs)
    refinements.instance_refinements.update({path: type_to_lib_path(block).SerializeToString()
      for path, block in instance_refinements.items()})

    with open(library_filename, 'wb') as lib_file:
      lib_file.write(self.generate_library_proto().SerializeToString())

    design, transformer = self._generate_design(raw_design, refinements,
                                                continue_on_error=continue_on_error, name=block._get_def_name())
    check_transform = CheckErrorsTransform(transformer.scp)
    design = check_transform.transform_design(design)
    with open(design_filename, 'wb') as design_file:
      design_file.write(design.SerializeToString())

    writer_transform = WriteSolvedParamTransform(transformer.scp)
    design_scp = writer_transform.transform_design(design)

    netlist = NetlistGenerator().generate(design_scp)  # type: ignore
    raise NotImplementedError

    netlist_string = footprint.generate_netlist(netlist.blocks, netlist.nets)
    with open(entlist_filename, 'w') as net_file:
      net_file.write(netlist_string)

    # TODO restructure schematic code to its own function?
    # TODO this should really be footprint and connectivity based!
    block_contents: Dict[TransformUtil.Path, List[TransformUtil.Path]] = {}  # block name -> list of internal blocks
    for path, block_type in netlist.types.items():
      if path.blocks:
        parent_blocks = path.blocks[:-1]
        parent_path = TransformUtil.Path(parent_blocks, (), (), ())
        block_contents.setdefault(parent_path, []).append(path)
    block_contents = {path: sorted(contents) for path, contents in block_contents.items()}

    block_types: Dict[TransformUtil.Path, Tuple[str, int]] = {}  # block name -> block type, hash of children
    def get_block_type(path: TransformUtil.Path) -> Tuple[str, int]:
      if path in block_types:
        return block_types[path]
      if path not in block_contents:
        return "", 0  # leaf block
      content_types = [(subblock.blocks[-1], get_block_type(subblock)) for subblock in block_contents[path]
                       if not subblock.blocks[-1].startswith('(bridge)') and
                       not subblock.blocks[-1].startswith('(adapter)')]
      content_str = str.encode(str(content_types))
      block_types[path] = netlist.types[path], zlib.adler32(content_str)  # TODO maybe use pickle
      return block_types[path]

    seen_types: Set[Tuple[str, int]] = set()
    def to_type_str(type_name: str, hash: int) -> str:
      return (type_name + ('_%08X' % hash)).replace('.', '_')

    for path, contents in block_contents.items():
      block_type_tup = get_block_type(path)
      if block_type_tup in seen_types:
        continue
      seen_types.add(block_type_tup)

      if not path.blocks:
        sch_name = 'design'
      else:
        sch_name = to_type_str(*block_type_tup)

      children = [(subblock_path.blocks[-1], to_type_str(*get_block_type(subblock_path))) for subblock_path in contents
                  if subblock_path in block_types]

      with open(os.path.join(target_dir, f'{sch_name}.sch'), 'w') as sch_file:
        sch_file.write(self._schematic_contents(children))
