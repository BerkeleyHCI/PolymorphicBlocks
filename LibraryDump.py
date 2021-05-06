# Simple tool that scans for libraries and dumps the whole thing to a proto file
from edg_core.HdlInterfaceServer import LibraryElementResolver
import edg_core
import edg
from edg_core.Builder import builder


OUTPUT_FILE = "library.edg"

if __name__ == '__main__':
  library = LibraryElementResolver()
  library.load_module(edg)
  pb = edg_core.edgir.Library()

  count = 0
  for (name, cls) in library.lib_class_map.items():
    obj = cls()
    if isinstance(obj, edg_core.Block):
      print(f"Elaborating block {name}")
      block_proto = builder.elaborate_toplevel(obj, f"in elaborating library block {cls}",
                                               replace_superclass=False)
      pb.root.members[name].hierarchy_block.CopyFrom(block_proto)
    elif isinstance(obj, edg_core.Link):
      print(f"Elaborating link {name}")
      link_proto = builder.elaborate_toplevel(obj, f"in elaborating library link {cls}",
                                              replace_superclass=False)
      pb.root.members[name].link.CopyFrom(link_proto)
    elif isinstance(obj, edg_core.Bundle):  # TODO: note Bundle extends Port, so this must come first
      print(f"Elaborating bundle {name}")
      pb.root.members[name].bundle.CopyFrom(obj._def_to_proto())
    elif isinstance(obj, edg_core.Port):
      print(f"Elaborating port {name}")
      pb.root.members[name].port.CopyFrom(obj._def_to_proto())
    else:
      print(f"Unknown category for class {cls}")

    count += 1

  with open(OUTPUT_FILE, 'wb') as file:
    file.write(pb.SerializeToString())

  print(f"Wrote {count} classes to {OUTPUT_FILE}")
