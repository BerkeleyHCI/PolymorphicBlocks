import importlib
import inspect
import sys
from types import ModuleType
from typing import Set, Dict, Type, Optional, Tuple, TypeVar, cast

import edgir
import edgrpc
from edg_core import *


# Index of module(s) recursively, and providing protobuf LibraryPath to class resolution.
class LibraryElementResolver:
  def __init__(self):
    self.seen_modules: Set[ModuleType] = set()
    self.lib_class_map: Dict[str, Type[LibraryElement]] = {}

    # Every time we reload, we need to get a fresh handle to the relevant base classes
    self.LibraryElementType = LibraryElement
    self.PortType = Port

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


LibraryElementType = TypeVar('LibraryElementType', bound=LibraryElement)
def elaborate_class(elt_cls: Type[LibraryElementType]) -> Tuple[LibraryElementType, edgir.Library.NS.Val]:
  obj = elt_cls()
  if isinstance(obj, Block):
    block_proto = builder.elaborate_toplevel(obj)
    return obj, edgir.Library.NS.Val(hierarchy_block=block_proto)  # type: ignore
  elif isinstance(obj, Link):
    link_proto = builder.elaborate_toplevel(obj)
    assert isinstance(link_proto, edgir.Link)  # TODO this needs to be cleaned up
    return obj, edgir.Library.NS.Val(link=link_proto)  # type: ignore
  elif isinstance(obj, Bundle):  # TODO: note Bundle extends Port, so this must come first
    return obj, edgir.Library.NS.Val(bundle=obj._def_to_proto())  # type: ignore
  elif isinstance(obj, Port):
    return obj, edgir.Library.NS.Val(port=cast(edgir.Port, obj._def_to_proto()))  # type: ignore
  else:
    raise RuntimeError(f"didn't match type of library element {elt_cls}")


# In some cases stdout seems to buffer excessively, in which case starting python with -u seems to work
# https://stackoverflow.com/a/35467658/5875811
if __name__ == '__main__':
  library = LibraryElementResolver()  # dummy empty resolver
  stdin_deserializer = BufferDeserializer(edgrpc.HdlRequest, sys.stdin.buffer)
  stdout_serializer = BufferSerializer[edgrpc.HdlResponse](sys.stdout.buffer)

  while True:
    request = stdin_deserializer.read()
    if request is None:  # end of stream
      sys.exit(0)

    response = edgrpc.HdlResponse()
    try:
      if request.HasField('index_module'):
        module = importlib.import_module(request.index_module.name)
        library.load_module(module)
        indexed = [edgir.LibraryPath(target=edgir.LocalStep(name=indexed))
                   for indexed in library.lib_class_map.keys()]
        response.index_module.indexed.extend(indexed)
      elif request.HasField('get_library_element'):
        cls = library.class_from_path(request.get_library_element.element)
        assert cls is not None, f"no class {request.get_library_element.element}"
        obj, obj_proto = elaborate_class(cls)

        response.get_library_element.element.CopyFrom(obj_proto)
        if isinstance(obj, DesignTop):
          obj.refinements().populate_proto(response.get_library_element.refinements)
      elif request.HasField('elaborate_generator'):
        generator_type = library.class_from_path(request.elaborate_generator.element)
        assert generator_type is not None, f"no generator {request.elaborate_generator.element}"
        assert issubclass(generator_type, GeneratorBlock)
        generator_obj = generator_type()

        response.elaborate_generator.generated.CopyFrom(builder.elaborate_toplevel(
          generator_obj,
          is_generator=True,
          generate_values=[(value.path, value.value) for value in request.elaborate_generator.values]))
      elif request.HasField('run_backend'):
        backend_split = request.run_backend.backend_class_name.split('.')
        backend_module = importlib.import_module('.'.join(backend_split[:-1]))
        assert inspect.ismodule(backend_module)
        backend_class = getattr(backend_module, backend_split[-1])
        assert issubclass(backend_class, BaseBackend)
        backend = backend_class()

        results = backend.run(CompiledDesign.from_backend_request(request.run_backend))
        for path, result in results:
          response_result = response.run_backend.results.add()
          response_result.path.CopyFrom(path)
          response_result.text = result
      else:
        raise RuntimeError(f"Unknown request {request}")
    except BaseException as e:
      import traceback
      # exception formatting from https://stackoverflow.com/questions/4564559/get-exception-description-and-stack-trace-which-caused-an-exception-all-as-a-st
      response.error.error = repr(e)
      response.error.traceback = "".join(traceback.TracebackException.from_exception(e).format())
      # also print it, to preserve the usual behavior of errors in Python
      traceback.print_exc()

    sys.stdout.buffer.write(stdin_deserializer.read_stdout())
    stdout_serializer.write(response)
