from edg_core import *

from typing import *

def edg_obj_name(obj: Any) -> str:
  return "%s@%02x" % (obj.get_ref_name(), (id(obj)//4) & 0xff)

def edg_to_dict(obj: Union[BasePort, BaseBlock]) -> Dict[str, Any]:
  if isinstance(obj, Bundle):
    return {
      '_': edg_obj_name(obj),
      'params': obj._parameters,
      'fields': {k: edg_to_dict(v) for k, v in obj._ports.items()},
      }
  elif isinstance(obj, Port):
    result = {
      '_': edg_obj_name(obj),
      'params': obj._parameters,
      }
    if obj._link_instance is not None:
      result['link'] = edg_to_dict(obj._link_instance)
    return result
  elif isinstance(obj, Block) or isinstance(obj, Link):
    return {
      '_': edg_obj_name(obj),
      'params': obj._parameters,
      'ports': {k: edg_to_dict(v) for k, v in obj._ports.items()},
      }
  else:
    raise ValueError
