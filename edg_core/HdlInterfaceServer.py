from types import ModuleType
from typing import Generator, Optional, Set, Dict, Type, cast, List

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


# Cacheing layer around library elements that also provides LibraryPath to class
# (instead of from module and class path) resolution.
class LibraryElementResolver():
  def __init__(self):
    self.seen_modules: Set[ModuleType] = set()
    self.module_contains: Dict[str, Set[str]] = {}
    self.lib_class_map: Dict[str, Type[LibraryElement]] = {}

  def load_module(self, module_name: str) -> None:
    """Loads a module and indexes the contained library elements so they can be accesed by LibraryPath.
    Avoids re-loading previously loaded modules with cacheing.
    """
    self._search_module(importlib.import_module(module_name))

  def discard_module(self, module_name: str) -> Set[str]:
    discarded = self.module_contains.get(module_name, set())
    for discard in discarded:
      self.lib_class_map.pop(discard, None)
    module = importlib.import_module(module_name)
    if module in self.seen_modules:  # TODO better discard behavior for never seen module
      self.seen_modules.remove(module)
    self.module_contains.pop(module_name, None)
    importlib.reload(module)
    return discarded

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
        else:  # for ports, recurse into links and stuff
          if issubclass(member, Port):  # TODO for some reason, Links not in __init__ are sometimes not found
            obj = member()  # TODO can these be clss definitions?
            if hasattr(obj, 'link_type'):
              self._search_module(importlib.import_module(obj.link_type.__module__))

        self.lib_class_map[name] = member
        self.module_contains.setdefault(member.__module__, set()).add(name)

  def class_from_path(self, path: edgir.LibraryPath) -> Optional[Type[LibraryElement]]:
    """Assuming modules have been loaded, retrieves a LibraryElement class by LibraryPath."""
    dict_key = path.target.name
    if dict_key not in self.lib_class_map:
      return None
    else:
      return self.lib_class_map[dict_key]


class HdlInterface(edgrpc.HdlInterfaceServicer):  # type: ignore
  def __init__(self, library: LibraryElementResolver, *, verbose: bool = False):
    self.library = library
    self.verbose = verbose

  def LibraryElementsInModule(self, request: edgrpc.ModuleName, context) -> \
      Generator[edgir.LibraryPath, None, None]:
    raise NotImplementedError

  def ClearCached(self, request: edgrpc.ModuleName, context) -> Generator[edgir.LibraryPath, None, None]:
    discarded = self.library.discard_module(request.name)
    if self.verbose:
      print(f"ClearCached({request.name}) -> None (discarding {len(discarded)})")
    for discard in discarded:
      pb = edgir.LibraryPath()
      pb.target.name = discard
      yield pb
    self.library.load_module(request.name)

  @staticmethod
  def _elaborate_class(elt_cls: Type[LibraryElement]) -> edgir.Library.NS.Val:
    obj = elt_cls()
    if isinstance(obj, Block):
      block_proto = builder.elaborate_toplevel(obj, f"in elaborating library block {elt_cls}",
                                               replace_superclass=False,)
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
    for module_name in request.modules:  # TODO: this isn't completely hermetic in terms of library searching
      self.library.load_module(module_name)

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
      print(f"while serving library element request for {request.element.target.name}")
      response.error = str(e)

    if self.verbose:
      if response.HasField('error'):
        print(f"GetLibraryElement([{', '.join(request.modules)}], {request.element.target.name}) -> {response.error}")
      else:
        print(f"GetLibraryElement([{', '.join(request.modules)}], {request.element.target.name}) -> ...")

    return response

  def ElaborateGenerator(self, request: edgrpc.GeneratorRequest, context) -> edgir.HierarchyBlock:
    for module_name in request.modules:  # TODO: this isn't completely hermetic in terms of library searching
      self.library.load_module(module_name)

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
      generated: Optional[edgir.HierarchyBlock] = builder.elaborate_toplevel(
        generator_obj, f"in generate {request.fn} for {request.element}",
        replace_superclass=False,
        generate_fn_name=request.fn, generate_values=generator_values)
    except BaseException as e:
      traceback.print_exc()
      print(f"while serving generator request for {request.element.target.name}")
      generated = None

    if generated is not None:
      if self.verbose:
        print(f"ElaborateGenerator([{', '.join(request.modules)}], {request.element.target.name, ...}) -> None")
      return generated
    else:
      if self.verbose:
        print(f"ElaborateGenerator([{', '.join(request.modules)}], {request.element.target.name, ...}) -> None")
      return edgir.HierarchyBlock()
