import importlib
import inspect
import sys
from types import ModuleType
from typing import Set, Type, Tuple, TypeVar, cast

from .. import edgir
from .. import edgrpc
from ..core import *
from ..core.Core import NonLibraryProperty


EDG_PROTO_VERSION = 5


class LibraryElementIndexer:
  """Indexer for libraries, recursively searches modules and their LibraryElements."""
  def __init__(self):
    self.seen_modules: Set[ModuleType] = set()
    self.seen_elements: Set[Type[LibraryElement]] = set()

  def index_module(self, module: ModuleType) -> Set[Type[LibraryElement]]:
    assert not self.seen_elements and not self.seen_modules
    self._search_module(module)
    return self.seen_elements

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

      if inspect.isclass(member) and issubclass(member, LibraryElement) and not issubclass(member, DesignTop) \
              and member not in self.seen_elements \
              and (member, NonLibraryProperty) not in member._elt_properties:  # process elements
        self.seen_elements.add(member)

        for mro in member.mro():
          self._search_module(importlib.import_module(mro.__module__))

        if issubclass(member, Port):  # TODO for some reason, Links not in __init__ are sometimes not found
          obj = member()  # TODO can these be class definitions?
          if hasattr(obj, 'link_type'):
            self._search_module(importlib.import_module(obj.link_type.__module__))


LibraryElementType = TypeVar('LibraryElementType', bound=LibraryElement)
def elaborate_class(elt_cls: Type[LibraryElementType]) -> Tuple[LibraryElementType, edgir.Library.NS.Val]:
  obj = elt_cls()
  assert (elt_cls, NonLibraryProperty) not in elt_cls._elt_properties.keys(), \
    f"tried to elaborate non-library {elt_cls.__name__}"

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


LibraryClassType = TypeVar('LibraryClassType')
def class_from_library(elt: edgir.LibraryPath, expected_superclass: Type[LibraryClassType]) -> \
        Type[LibraryClassType]:
  elt_split = elt.target.name.split('.')
  elt_module = importlib.import_module('.'.join(elt_split[:-1]))
  assert inspect.ismodule(elt_module)
  cls = getattr(elt_module, elt_split[-1])
  assert issubclass(cls, expected_superclass)
  return cls


def run_server():
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
        library = LibraryElementIndexer()
        indexed = [edgir.LibraryPath(target=edgir.LocalStep(name=indexed._static_def_name()))
                   for indexed in library.index_module(module)]
        response.index_module.indexed.extend(indexed)
      elif request.HasField('get_library_element'):
        cls = class_from_library(request.get_library_element.element,
                                 LibraryElement)  # type: ignore
        obj, obj_proto = elaborate_class(cls)

        response.get_library_element.element.CopyFrom(obj_proto)
        if isinstance(obj, DesignTop):
          obj.refinements().populate_proto(response.get_library_element.refinements)
      elif request.HasField('elaborate_generator'):
        generator_type = class_from_library(request.elaborate_generator.element,
                                            GeneratorBlock)
        generator_obj = generator_type()

        response.elaborate_generator.generated.CopyFrom(builder.elaborate_toplevel(
          generator_obj,
          is_generator=True,
          generate_values=[(value.path, value.value) for value in request.elaborate_generator.values]))
      elif request.HasField('run_refinement'):
        refinement_pass_class = class_from_library(request.run_refinement.refinement_pass,
                                                   BaseRefinementPass)  # type: ignore
        refinement_pass = refinement_pass_class()

        refinement_results = refinement_pass.run(
          CompiledDesign.from_request(request.run_refinement.design, request.run_refinement.solvedValues))
        response.run_refinement.SetInParent()
        for path, refinement_result in refinement_results:
          new_value = response.run_refinement.newValues.add()
          new_value.path.CopyFrom(path)
          new_value.value.CopyFrom(refinement_result)
      elif request.HasField('run_backend'):
        backend_class = class_from_library(request.run_backend.backend,
                                           BaseBackend)  # type: ignore
        backend = backend_class()

        backend_results = backend.run(
          CompiledDesign.from_request(request.run_backend.design, request.run_backend.solvedValues),
          dict(request.run_backend.arguments))
        response.run_backend.SetInParent()
        for path, backend_result in backend_results:
          response_result = response.run_backend.results.add()
          response_result.path.CopyFrom(path)
          response_result.text = backend_result
      elif request.HasField('get_proto_version'):
        response.get_proto_version = EDG_PROTO_VERSION
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


# In some cases stdout seems to buffer excessively, in which case starting python with -u seems to work
# https://stackoverflow.com/a/35467658/5875811
if __name__ == '__main__':
  run_server()
