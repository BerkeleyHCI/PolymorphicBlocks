from typing import *
from edg_core import *
from edg_core import edgir
import subprocess
import platform


def is_internal_name(name: str) -> bool:
  return name.startswith('(bridge)') or name.startswith('(adapter)') or name.startswith('(constr)')

def path_to_string(path: edgir.LibraryPath) -> str:
  return path.target.name.split('.')[-1]

def superclasses_to_string(superclasses: Iterable[edgir.LibraryPath]) -> str:
  superclasses_list = [path_to_string(superclass) for superclass in superclasses]
  return ", ".join(superclasses_list)

def open_source_locator_wrapper(filepath: str, line: int) -> Callable[[], None]:
  def inner() -> None:
    # TODO this needs a more intelligent way of detecting IntelliJ locations across different installs
    if platform.system() == 'Windows':
      bin_name = 'C:/Program Files/JetBrains/IntelliJ IDEA Community Edition 2019.1/bin/idea64.exe'
    elif platform.system() == 'Linux':
      bin_name = '/snap/intellij-idea-community/current/bin/idea.sh'
    else:
      raise OSError(f"don't know how to launch IntelliJ for {platform.system()}")
    subprocess.call([bin_name,
                     '--line', str(line), filepath])
  return inner


class Library:
  def __init__(self, *libraries: edgir.Library):
    self.blocks: Dict[bytes, edgir.HierarchyBlock] = {}
    self.block_children: Dict[bytes, List[bytes]] = {}  # superclass lib name -> subclass lib names
    self.block_children[b''] = []  # create default dummy entry for root blocks
    # TODO maybe need inheritance tree on ports and links? but inheritance is less a thing there
    self.ports: Dict[bytes, Union[edgir.Port, edgir.Bundle]] = {}
    self.links: Dict[bytes, edgir.Link] = {}

    for library in libraries:
      self._load_library(library)

  def _load_library(self, library: edgir.Library):
    for name, elt in library.root.members.items():
      path = edgir.LibraryPath()
      path.target.name = name
      path_str = path.SerializeToString()
      if elt.HasField('port'):
        self.ports[path_str] = elt.port
      elif elt.HasField('bundle'):
        self.ports[path_str] = elt.bundle
      elif elt.HasField('link'):
        self.links[path_str] = elt.link
      elif elt.HasField('hierarchy_block'):
        self.blocks[path_str] = elt.hierarchy_block
        if not elt.hierarchy_block.superclasses:
          self.block_children[b''].append(path_str)
        else:
          for block_superclass in elt.hierarchy_block.superclasses:
            self.block_children.setdefault(block_superclass.SerializeToString(), []).append(path_str)
      else:
        raise ValueError(f"Unknown library type {elt}")

  def all_defs(self) -> Dict[str, edgir.EltTypes]:
    out_dict: Dict[str, edgir.EltTypes] = {}
    for name, block in self.blocks.items():
      out_dict[edgir.LibraryPath.FromString(name).target.name] = block
    for name, link in self.links.items():
      out_dict[edgir.LibraryPath.FromString(name).target.name] = link
    for name, port in self.ports.items():
      out_dict[edgir.LibraryPath.FromString(name).target.name] = port
    return out_dict

  @classmethod
  def _to_library_path(cls, serialized: bytes) -> edgir.LibraryPath:
    return edgir.LibraryPath.FromString(serialized)

  def get_child_blocks(self, path: edgir.LibraryPath) -> List[Tuple[edgir.LibraryPath, edgir.BlockTypes]]:
    if path.SerializeToString() not in self.block_children:
      return []
    else:
      subclass_paths = self.block_children[path.SerializeToString()]
      return [(self._to_library_path(subclass_path), self.blocks[subclass_path]) for subclass_path in subclass_paths]

  def get_root_blocks(self) -> List[Tuple[edgir.LibraryPath, edgir.BlockTypes]]:
    return [(self._to_library_path(path), self.blocks[path]) for path in self.block_children[b'']]

  def get_missing_blocks(self) -> List[edgir.LibraryPath]:
    return [self._to_library_path(path)
            for path in self.block_children.keys() if path not in self.blocks and path != b'']

  def get_root_ports(self) -> List[Tuple[edgir.LibraryPath, edgir.PortTypes]]:
    return [(self._to_library_path(path), elt) for path, elt in self.ports.items()]

  def get_root_links(self) -> List[Tuple[edgir.LibraryPath, edgir.Link]]:
    return [(self._to_library_path(path), elt) for path, elt in self.links.items()]
