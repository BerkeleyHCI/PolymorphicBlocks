from typing import *
import mypy
from mypy.plugin import Plugin  # type: ignore


class CustomPlugin(Plugin):
  @staticmethod
  def _type_args_of_base(type: mypy.nodes.TypeInfo, base_name: str) -> Optional[Any]:
    """Returns the type arguments of the base of the input type with name base_name."""
    for base in type.bases:
      if base_name in base.type._fullname:
        return base.args
    return None

  def get_function_hook(self, fullname: str
                        ) -> Optional[Callable[[mypy.plugin.FunctionContext], Type]]:
    def inner(fn: mypy.plugin.FunctionContext) -> mypy.types.Type:
      assert isinstance(fn.default_return_type, mypy.types.CallableType)
      print(fn.default_return_type.arg_types)
      for (i, arg_type) in enumerate(fn.default_return_type.arg_types):
        if isinstance(arg_type, mypy.types.Instance):
          assignable_type = self._type_args_of_base(arg_type.type, 'ConstraintAssignable')
          if assignable_type is not None:
            print(assignable_type)

            fn.default_return_type.arg_types[i] = assignable_type[0]  # first type argument is the assignable types

      print(fn.default_return_type.arg_types)

      return fn.default_return_type

    if 'init_in_parent' in fullname:

      return inner
    return None

def plugin(version: str):
  # ignore version argument if the plugin works with all mypy versions.
  return CustomPlugin
