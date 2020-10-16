from compiler_gui.BlockDiagramModel import Block, transform_simplify_adapter, transform_simplify_bridge
from compiler_gui.ElkGraph import ElkGraph
from edg_core import edgir
from edg_core import TransformUtil as tfu


if __name__ == '__main__':
  # Online visualizer here: https://rtsys.informatik.uni-kiel.de/elklive/elkgraph.html
  # Generate library from file
  design = edgir.Design()
  with open('examples/test_debugger/design.edg', "rb") as f:
    design.ParseFromString(f.read())

  block = Block(tfu.Path.empty(), design.contents)

  def simplify_block_recursive(block: Block):
    transform_simplify_bridge(block)
    transform_simplify_adapter(block)
    for subblock_name, subblock_obj in block.subblocks.items():
      simplify_block_recursive(subblock_obj)

  simplify_block_recursive(block)

  ElkGraph.start_gateway()
  graph = ElkGraph(block, 2)
  elk_json = graph.to_json(True)

  with open("elk.log", "w") as text_file:  # TODO configurable filename
    text_file.write(elk_json)

  print("done, waiting for ELK JAR to terminate")
  ElkGraph.close_gateway()
