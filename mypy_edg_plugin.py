from typing import *
from mypy.plugin import Plugin  # type: ignore


class CustomPlugin(Plugin):
  def get_function_hook(self, fullname: str
                        ) -> Optional[Callable[['FunctionContext'], Type]]:
    def inner(fn: 'FunctionContext') -> 'Type':
      print(fn)
      return None

    if 'init_in_parent' in fullname:
      print(f"GetFunctionHook {fullname}")
      return inner
    return None

def plugin(version: str):
  # ignore version argument if the plugin works with all mypy versions.
  return CustomPlugin
