from types import ModuleType
from typing import Generator, Optional, Set, Dict, Type, cast, List, Any

import builtins
import importlib
import inspect
import traceback
import sys

from . import edgrpc, edgir
from .Core import builder, LibraryElement
from .Blocks import Link
from .HierarchyBlock import Block, GeneratorBlock
from .DesignTop import DesignTop
from .Ports import Port, Bundle


# Index of module(s) recursively, and providing protobuf LibraryPath to class resolution.
class LibraryElementResolver():
  def __init__(self):
    self.seen_modules: Set[ModuleType] = set()
    self.lib_class_map: Dict[str, Type[LibraryElement]] = {}

    # Every time we reload, we need to get a fresh handle to the relevant base classes
    self.LibraryElementType = getattr(importlib.import_module("edg_core"), "LibraryElement")
    self.PortType = getattr(importlib.import_module("edg_core"), "Port")

  def load_module(self, module: ModuleType) -> None:
    """Loads a module and indexes the contained library elements so they can be accesed by LibraryPath.
    Avoids re-loading previously loaded modules with cacheing.
    """
    self._search_module(module)

  def _search_module(self, module: ModuleType) -> None:
    # avoid repeated work and re-indexing modules
    if (module.__name__ in sys.builtin_module_names
        or not hasattr(module, '__file__')  # apparently load six.moves breaks
        or module in self.seen_modules):
      return
    self.seen_modules.add(module)

    for (name, member) in inspect.getmembers(module):
      if inspect.ismodule(member):  # recurse into visible modules
        self._search_module(member)

      if inspect.isclass(member) and issubclass(member, self.LibraryElementType) \
          and (member, 'non_library') not in member._elt_properties:  # process elements
        name = member._static_def_name()
        if name in self.lib_class_map:
          assert self.lib_class_map[name] == member, f"different redefinition of {name} in {module.__name__}"
          continue  # don't need to re-index

        for mro in member.mro():
          self._search_module(importlib.import_module(mro.__module__))

        if issubclass(member, self.PortType):  # TODO for some reason, Links not in __init__ are sometimes not found
          obj = member()  # TODO can these be class definitions?
          if hasattr(obj, 'link_type'):
            self._search_module(importlib.import_module(obj.link_type.__module__))

        self.lib_class_map[name] = member

  def class_from_path(self, path: edgir.LibraryPath) -> Optional[Type[LibraryElement]]:
    """Assuming modules have been loaded, retrieves a LibraryElement class by LibraryPath."""
    dict_key = path.target.name
    return self.lib_class_map.get(dict_key, None)


# Module reloading solution from http://pyunit.sourceforge.net/notes/reloading.html
class RollbackImporter:
  def __init__(self) -> None:
    "Creates an instance and installs as the global importer"
    self.previousModules: Set[ModuleType] = set(sys.modules.copy().values())
    self.realImport = builtins.__import__
    builtins.__import__ = self._import
    self.newModules: List[ModuleType] = []

  def _import(self, name: str, *args, **kwargs) -> ModuleType:
    module = self.realImport(name, *args, **kwargs)
    if module not in self.newModules \
        and module.__name__ not in sys.builtin_module_names \
        and hasattr(module, '__file__') \
        and module.__file__ \
        and module not in self.previousModules \
        and 'Python37-32' not in module.__file__ \
        and 'site-packages' not in module.__file__ \
        and 'edg_core' not in module.__file__:  # don't rollback internals, bad things happen
      self.newModules.append(module)

    return module

  def clear(self) -> None:
    inverse_modules = {module: name for name, module in sys.modules.items()}
    deleted_modules = []
    for module in self.newModules:
      if module in inverse_modules:
        name = inverse_modules[module]
        if name in sys.modules:
          del sys.modules[name]
          deleted_modules.append(module)
    self.newModules = []

class HdlInterface(edgrpc.HdlInterfaceServicer):  # type: ignore
  def __init__(self, *, verbose: bool = False, rollback: Optional[Any] = None):
    self.library = LibraryElementResolver()  # dummy empty resolver
    self.verbose = verbose
    self.rollback = rollback

  def ReloadModule(self, request: edgrpc.ModuleName, context) -> Generator[edgir.LibraryPath, None, None]:
    if self.verbose:
      print(f"ReloadModule({request.name}) -> ", end='', flush=True)

    try:
      # nuke it from orbit, because we really don't know how to do better right now
      self.library = LibraryElementResolver()  # clear old the old resolver
      if self.rollback is not None:
        self.rollback.clear()

      module = importlib.import_module(request.name)
      self.library.load_module(module)
      if self.rollback is not None:
        self.rollback.newModules.append(module)

      if self.verbose:
        print(f"None (indexed {len(self.library.lib_class_map)})", flush=True)
      for indexed in self.library.lib_class_map.keys():
        pb = edgir.LibraryPath()
        pb.target.name = indexed
        yield pb
    except BaseException as e:
      if self.verbose:
        print(f"Error {e}", flush=True)
      return

  @staticmethod
  def _elaborate_class(elt_cls: Type[LibraryElement]) -> edgir.Library.NS.Val:
    obj = elt_cls()
    if isinstance(obj, Block):
      block_proto = builder.elaborate_toplevel(obj, f"in elaborating library block {elt_cls}",
                                               replace_superclass=False)
      return edgir.Library.NS.Val(hierarchy_block=block_proto)
    elif isinstance(obj, Link):
      link_proto = builder.elaborate_toplevel(obj, f"in elaborating library link {elt_cls}",
                                              replace_superclass=False)
      assert isinstance(link_proto, edgir.Link)  # TODO this needs to be cleaned up
      return edgir.Library.NS.Val(link=link_proto)
    elif isinstance(obj, Bundle):  # TODO: note Bundle extends Port, so this must come first
      return edgir.Library.NS.Val(bundle=obj._def_to_proto())
    elif isinstance(obj, Port):
      return edgir.Library.NS.Val(port=cast(edgir.Port, obj._def_to_proto()))
    else:
      raise RuntimeError(f"didn't match type of library element {elt_cls}")

  def GetLibraryElement(self, request: edgrpc.LibraryRequest, context) -> edgrpc.LibraryResponse:
    if self.verbose:
      print(f"GetLibraryElement({request.element.target.name}) -> ", end='', flush=True)

    response = edgrpc.LibraryResponse()
    try:
      cls = self.library.class_from_path(request.element)
      if cls is None:
        response.error = f"No library elt {request.element}"
      else:
        response.element.CopyFrom(self._elaborate_class(cls))
        if issubclass(cls, DesignTop):  # TODO don't create another instance, perhaps refinements should be static?
          cls().refinements().populate_proto(response.refinements)
    except BaseException as e:
      traceback.print_exc()
      print(f"while serving library element request for {request.element.target.name}", flush=True)
      response.error = str(e)

    if self.verbose:
      if response.HasField('error'):
        print(f"Error {response.error}", flush=True)
      elif response.HasField('refinements'):
        print(f"(elt, w/ refinements)", flush=True)
      else:
        print(f"(elt)", flush=True)

    return response

  def ElaborateGenerator(self, request: edgrpc.GeneratorRequest, context) -> edgrpc.GeneratorResponse:
    if self.verbose:
      print(f"ElaborateGenerator({request.element.target.name}) -> ", end='', flush=True)

    response = edgrpc.GeneratorResponse()
    try:
      generator_type = self.library.class_from_path(request.element)
      assert generator_type is not None, f"no generator {request.element}"
      assert issubclass(generator_type, GeneratorBlock)
      generator_obj = generator_type()
      generator_values_raw = [(value.path, edgir.valuelit_to_lit(value.value))
                              for value in request.values]
      generator_values = [(path, value)  # purge None from values to make the typer happy
                          for (path, value) in generator_values_raw
                          if value is not None]
      response.generated.CopyFrom(builder.elaborate_toplevel(
        generator_obj, f"in generate {request.fn} for {request.element}",
        replace_superclass=False,
        generate_fn_name=request.fn, generate_values=generator_values))
    except BaseException as e:
      if self.verbose:
        traceback.print_exc()
        print(f"while serving generator request for {request.element.target.name}", flush=True)
      response.error = str(e)

    if self.verbose:
      if response.HasField('error'):
        print(f"Error {response.error}", flush=True)
      else:
        print(f"(generated)", flush=True)

    return response
