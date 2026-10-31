from typing import Any, Union, Dict
from .Ports import BasePort, Port
from .Blocks import BaseBlock, Link
from .HierarchyBlock import Block


def edg_obj_name(obj: Any) -> str:
    return "%s@%02x" % (obj.get_ref_name(), (id(obj) // 4) & 0xFF)


def edg_to_dict(obj: Union[BasePort, BaseBlock]) -> Dict[str, Any]:
    if isinstance(obj, Port):
        result = {
            "_": edg_obj_name(obj),
            "params": obj._parameters,
            "fields": {obj._name_of(port): edg_to_dict(port) for port in obj._ports},
        }
        if obj._link_instance is not None:
            result["link"] = edg_to_dict(obj._link_instance)
        return result
    elif isinstance(obj, Block) or isinstance(obj, Link):
        return {
            "_": edg_obj_name(obj),
            "params": {obj._name_of(param): param for param in obj._parameters},
            "ports": {obj._name_of(port): edg_to_dict(port) for port in obj._ports},
        }
    else:
        raise ValueError
