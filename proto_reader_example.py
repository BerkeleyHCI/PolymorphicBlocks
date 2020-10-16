from edg_core import *

if __name__ == '__main__':
  design = edgir.Design()
  with open('test_buck_netlist.edg', "rb") as f:
    design.ParseFromString(f.read())

  print(f"===Raw parsed proto===\n{design}\n\n")

  # TODO: for visualizer you might want this to return str (elk representation)
  def process_hierarchy_block(path: TransformUtil.Path, block: edgir.HierarchyBlock) -> None:
    print(f"Found block at {path}")
    for name, port in block.ports.items():
      print(f"... with port {name}")
    for name, link in block.links.items():
      print(f"... with link {name}")
    for name, subblock in block.blocks.items():
      if subblock.HasField('hierarchy'):
        print(f"... with sub-h-block {name}")
        process_hierarchy_block(path.append_block(name), subblock.hierarchy)
      elif subblock.HasField('block'):
        print(f"... with sub-block {name}")
      else:
        raise ValueError(f"unknown sub-block {subblock}")

  process_hierarchy_block(TransformUtil.Path((), None, ()), design.contents)
