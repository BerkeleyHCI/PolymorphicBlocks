from types import ModuleType
from typing import  Generator, cast, Optional, Set, Dict, Type

import grpc  # type: ignore
from concurrent import futures

import importlib
import inspect

from edg_core import edgrpc, edgir, LibraryElement


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
    self._search_module(importlib.import_module('edg_core'))

  def _search_module(self, module: ModuleType) -> None:
    # avoid repeated work and re-indexing modules
    if module in self.seen_modules:
      return
    self.seen_modules.add(module)

    for (name, member) in inspect.getmembers(module):
      if inspect.ismodule(member):
        self._search_module(member)
      if inspect.isclass(member) and issubclass(member, LibraryElement) \
          and (member, 'non_library') not in member._elt_properties:
        name = member._static_def_name()
        assert name not in self.lib_class_map, f"re-loaded {name}"
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
  def _elaborate_class(cls, elt_cls: Type[LibraryElement]) -> edgir.Library.NS.Val:
    obj = elt_cls()
    if isinstance(obj, Block):
      pass




class HdlInterface(edgrpc.HdlInterfaceServicer):  # type: ignore
  def __init__(self, library: CachedLibrary):
    self.library = library

  def LibraryElementsInModule(self, request: edgrpc.ModuleName, context) ->\
          Generator[edgir.LibraryPath, None, None]:
    return  # TODO implement me

  def GetLibraryElement(self, request: edgir.LibraryPath, context) -> edgir.Library.NS.Val:
    # TODO: this isn't completely hermetic in terms of library searching
    print(request)
    return edgir.Library.NS.Val()

  def ElaborateGenerator(self, request: edgrpc.GeneratorRequest, context) -> edgir.HierarchyBlock:
    # TODO: this isn't completely hermetic in terms of library searching
    print(request)
    return edgir.HierarchyBlock()


if __name__ == '__main__':
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
  edgrpc.add_HdlInterfaceServicer_to_server(HdlInterface(), server)  # type: ignore
  server.add_insecure_port('[::]:50051')
  print("started server")
  # server.start()
  # server.wait_for_termination()

  module = importlib.import_module('edg_core')
  module = importlib.import_module('electronics_abstract_parts')
  module = importlib.import_module('edg_core.test_generator')
  module = importlib.import_module('electronics_lib')


  from edg_core import Block, Port, Bundle, Link

  for (name, cls) in inspect.getmembers(module):
    if inspect.ismodule(cls):
      print(f"{cls}")
    if inspect.isclass(cls) and issubclass(cls, LibraryElement)\
            and (cls, 'non_library') not in cls._elt_properties:
      # obj = cast(LibraryElement, cls())
      # obj_name = obj._get_def_name()
      obj_name = cls._static_def_name()
      # print(f"{cls} {obj_name}")

