from types import ModuleType
from typing import  Generator, Optional, Set, Dict, Type, cast

import importlib
import inspect
import traceback
import sys

from . import edgrpc, edgir
from .Core import builder, LibraryElement
from .Blocks import Link
from .HierarchyBlock import Block
from .Ports import Port, Bundle


# Cacheing layer around library elements that also provides LibraryPath to class and proto
# (instead of from module and class path) resolution.
class CachedLibrary():
  def __init__(self):
    self.seen_modules: Set[ModuleType] = set()
    self.lib_class_map: Dict[str, Type[LibraryElement]] = {}
    self.lib_proto_map: Dict[str, edgir.Library.NS.Val] = {}

  # Loads a module and indexes the contained library elements so they can be accesed by LibraryPath.
  # Avoids re-loading previously loaded modules with cacheing.
  def load_module(self, module_name: str) -> None:
    self._search_module(importlib.import_module(module_name))

  def _search_module(self, module: ModuleType) -> None:
    # avoid repeated work and re-indexing modules
    if (module.__name__ in sys.builtin_module_names
        or not hasattr(module, '__file__')  # apparently load six.moves breaks
        or module in self.seen_modules):
      return
    self.seen_modules.add(module)

    for (name, member) in inspect.getmembers(module):
      if inspect.ismodule(member):
        self._search_module(member)
      if inspect.isclass(member) and issubclass(member, LibraryElement) \
          and (member, 'non_library') not in member._elt_properties:
        name = member._static_def_name()
        if name in self.lib_class_map:
          assert self.lib_class_map[name] == member, f"different redefinition of {name} in {module.__name__}"
        self.lib_class_map[name] = member

  # Assuming the module has been loaded, retrieves a library element by LibraryPath.
  def find_by_path(self, path: edgir.LibraryPath) -> Optional[edgir.Library.NS.Val]:
    dict_key = path.target.name
    if path.target.name in self.lib_proto_map:
      return self.lib_proto_map[dict_key]
    else:
      if dict_key not in self.lib_class_map:
        return None
      else:
        elaborated = self._elaborate_class(self.lib_class_map[dict_key])
        self.lib_proto_map[dict_key] = elaborated
        return elaborated

  @staticmethod
  def _elaborate_class(elt_cls: Type[LibraryElement]) -> edgir.Library.NS.Val:
    obj = elt_cls()
    if isinstance(obj, Block):
      block_proto = builder.elaborate_toplevel(obj, f"in elaborating library block {elt_cls}")
      return edgir.Library.NS.Val(hierarchy_block=block_proto)
    elif isinstance(obj, Link):
      link_proto = builder.elaborate_toplevel(obj, f"in elaborating library link {elt_cls}")
      assert isinstance(link_proto, edgir.Link)  # TODO this needs to be cleaned up
      return edgir.Library.NS.Val(link=link_proto)
    elif isinstance(obj, Bundle):  # TODO: note Bundle extends Port, so this must come first
      return edgir.Library.NS.Val(bundle=obj._def_to_proto())
    elif isinstance(obj, Port):
      return edgir.Library.NS.Val(port=cast(edgir.Port, obj._def_to_proto()))
    else:
      raise RuntimeError(f"didn't match type of library element {elt_cls}")


class HdlInterface(edgrpc.HdlInterfaceServicer):  # type: ignore
  def __init__(self, library: CachedLibrary):
    self.library = library

  def LibraryElementsInModule(self, request: edgrpc.ModuleName, context) -> \
      Generator[edgir.LibraryPath, None, None]:
    raise NotImplementedError

  def GetLibraryElement(self, request: edgrpc.LibraryRequest, context) -> edgir.Library.NS.Val:
    # TODO: this isn't completely hermetic in terms of library searching
    for module_name in request.modules:
      self.library.load_module(module_name)

    try:
      library_elt = self.library.find_by_path(request.element)
    except BaseException as e:
      traceback.print_exc()
      print(f"while serving library element request for {request.element.target.name}")
      library_elt = None

    if library_elt is not None:
      return library_elt
    else:
      return edgir.Library.NS.Val()  # TODO better more explicit failure?

  def ElaborateGenerator(self, request: edgrpc.GeneratorRequest, context) -> edgir.HierarchyBlock:
    # TODO: this isn't completely hermetic in terms of library searching
    for module_name in request.modules:
      self.library.load_module(module_name)

    try:
      pass
    except BaseException as e:
      traceback.print_exc()
      print(f"while serving generator request for {request.element.target.name}")

    return edgir.HierarchyBlock()
