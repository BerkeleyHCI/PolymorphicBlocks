from typing import Any, Tuple, Dict, List, Optional, Callable, Set
from itertools import chain

from tkinter import *
from tkinter import ttk

from edg_core import edgir, MultiBiDict
from edg_core import TransformUtil as tfu

from .ElkGraph import ElkGraph
from .BlockDiagramModel import Block, LinkLike, Link, Export, transform_simplify_bridge, transform_simplify_adapter

class BlockDiagramPanel:
  CANVAS_SCROLL_MARGIN = 10
  SCALE_FACTOR = 1

  BLOCK_FILL = '#c0c0ff'
  PORT_FILL = '#8080ff'
  LINK_FILL = '#000000'
  LINK_WIDTH = 1

  BLOCK_SELECT_FILL = '#00a0ff'
  PORT_SELECT_FILL = '#00a0ff'
  PORT_SELECT_INDIRECT_FILL = '#0060c0'
  LINK_SELECT_FILL = '#00a0ff'
  LINK_SELECT_INDIRECT_FILL = '#0060c0'
  LINK_SELECT_WIDTH = 3

  def __init__(self, parent: ttk.Frame) -> None:
    self.frame = Frame(parent, width=1000, height=500)
    self.canvas = Canvas(self.frame, width=1000, height=500)

    self.scale_frame = Frame(self.frame)
    self.scale_label = ttk.Label(self.scale_frame, text='Block Diagram Render Depth')
    self.scale_label.pack(side=LEFT)
    self.scale = Scale(self.scale_frame, from_=1, to=2, orient=HORIZONTAL)
    self.scale.pack(side=BOTTOM, fill=X)
    self.scale.set(2)
    self.scale.config(command=self._on_scale)  # prevent set-triggered (re)draw on startup
    self.scale_frame.pack(side=BOTTOM, fill=X)

    self.hbar = Scrollbar(self.frame, orient=HORIZONTAL)
    self.hbar.pack(side=BOTTOM, fill=X)
    self.hbar.config(command=self.canvas.xview)
    self.vbar = Scrollbar(self.frame, orient=VERTICAL)
    self.vbar.pack(side=RIGHT, fill=Y)
    self.vbar.config(command=self.canvas.yview)

    self.canvas.pack(expand=True, fill=BOTH)
    self.canvas.config(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)

    self.canvas.bind("<B1-Motion>", lambda event: self.canvas.scan_dragto(event.x, event.y, gain=1))
    self.canvas.bind('<Button-1>', self._on_select)
    def do_zoom(event, factor):
      self.canvas.scale(ALL, self.canvas.canvasx(event.x), self.canvas.canvasy(event.y), factor, factor)
      min_x, min_y, max_x, max_y = self.canvas.bbox(ALL)
      self.canvas.config(scrollregion=(min_x - self.CANVAS_SCROLL_MARGIN, min_y - self.CANVAS_SCROLL_MARGIN,
                                       max_x + self.CANVAS_SCROLL_MARGIN, max_y + self.CANVAS_SCROLL_MARGIN))
    self.canvas.bind("<MouseWheel>", lambda ev: do_zoom(ev, 1.001 ** ev.delta))
    self.canvas.bind("<Button-4>", lambda ev: do_zoom(ev, 1.1))  # cross-platform hack
    self.canvas.bind("<Button-5>", lambda ev: do_zoom(ev, 0.9))

    self.port_links: Dict[tfu.Path, Set[LinkLike]] = {}

    self.block_item_path: MultiBiDict[int, tfu.Path] = MultiBiDict()
    self.port_item_path: MultiBiDict[int, tfu.Path] = MultiBiDict()
    self.link_item_path: MultiBiDict[int, tfu.Path] = MultiBiDict()
    self.selected_items: List[Any] = []

    self.select_fns: List[Callable[[Optional[tfu.Path]], None]] = []

    self.block: Optional[Block] = None

  def _on_scale(self, event) -> None:
    # self.scale.update()
    self.redraw()

  def get_root(self) -> Frame:  # TODO replace with generic superclass
    return self.frame

  def _on_select(self, event) -> None:
    self.canvas.scan_mark(event.x, event.y)

    selected_path: Optional[tfu.Path] = None
    closest = self.canvas.find_closest(self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))
    if not closest:  # empty tuple returned if no items on canvas
      return

    item = closest[0]  # TODO not sure why its returning a tuple of one
    if item in self.block_item_path:
      selected_path = self.block_item_path[item]
    elif item in self.port_item_path:
      selected_path = self.port_item_path[item]
    elif item in self.link_item_path:
      selected_path = self.link_item_path[item]
    for fn in self.select_fns:
      fn(selected_path)

  def on_select(self, fn: Callable[[Optional[tfu.Path]], None]) -> None:
    self.select_fns.append(fn)

  def _render_block_contents(self, node: Any, offs: Tuple[float, float], scale: float, depth: int = 0) -> None:
    for subnode in node.getChildren():
      origin = (subnode.getX() * scale, subnode.getY() * scale)
      subnode_item = self.canvas.create_rectangle(offs[0] + origin[0], offs[1] + origin[1],
                                                  offs[0] + origin[0] + subnode.getWidth() * scale,
                                                  offs[1] + origin[1] + subnode.getHeight() * scale,
                                                  fill=self.BLOCK_FILL)
      if subnode.getIdentifier() in self.graph.blocks:
        self.block_item_path.add(subnode_item, self.graph.blocks[subnode.getIdentifier()])
      for label in subnode.getLabels():
        self.canvas.create_text(offs[0] + origin[0] + label.getX() * scale, offs[1] + origin[1] + label.getY() * scale,
                                anchor=CENTER, text=label.getText())  # TODO scaling

      for subnode_port in subnode.getPorts():
        port_origin = (origin[0] + subnode_port.getX() * scale, origin[1] + subnode_port.getY() * scale)
        port_item = self.canvas.create_rectangle(offs[0] + port_origin[0], offs[1] + port_origin[1],
                                                 offs[0] + port_origin[0] + subnode_port.getWidth() * scale,
                                                 offs[1] + port_origin[1] + subnode_port.getHeight() * scale,
                                                 fill=self.PORT_FILL)
        if subnode_port.getIdentifier() in self.graph.ports:
          self.port_item_path.add(port_item, self.graph.ports[subnode_port.getIdentifier()])

        for label in subnode_port.getLabels():
          if subnode_port.getX() < 0:  # heuristic to guess port side - TODO: use CoreOptions.PORT_SIDE property
            anchor: str = W
          else:
            anchor = E
          self.canvas.create_text(offs[0] + port_origin[0] + label.getX() * scale, offs[1] + port_origin[1] + label.getY() * scale,
                                  anchor=anchor, text=label.getText())  # TODO scaling

      self._render_block_contents(subnode, (offs[0] + origin[0], offs[1] + origin[1]), scale, depth+1)

    for edge in node.getContainedEdges():
        for section in edge.getSections():
          start = (section.getStartX() * scale, section.getStartY() * scale)
          bends = [(bp.getX() * scale, bp.getY() * scale) for bp in section.getBendPoints()]
          end = (section.getEndX() * scale, section.getEndY() * scale)

          all_points = [start] + bends + [end]
          all_points_abs = [(offs[0] + x, offs[1] + y) for x, y in all_points]

          edge_item = self.canvas.create_line(*chain(*all_points_abs),
                                              fill=self.LINK_FILL,
                                              arrow=LAST, arrowshape=f"{8*scale} {10*scale} {3*scale}")
          if edge.getIdentifier() in self.graph.links:
            self.link_item_path.add(edge_item, self.graph.links[edge.getIdentifier()])

  def redraw(self) -> None:
    self.canvas.delete('all')

    self.block_item_path.clear()
    self.port_item_path.clear()
    self.link_item_path.clear()
    self.selected_items = []

    if self.block is None:
      return

    self.graph = ElkGraph(self.block, self.scale.get())
    self._render_block_contents(self.graph.root, (0, 0), self.SCALE_FACTOR)

    bbox = self.canvas.bbox(ALL)
    if bbox is not None:
      min_x, min_y, max_x, max_y = bbox
      self.canvas.config(scrollregion=(min_x - self.CANVAS_SCROLL_MARGIN, min_y - self.CANVAS_SCROLL_MARGIN,
                                       max_x + self.CANVAS_SCROLL_MARGIN, max_y + self.CANVAS_SCROLL_MARGIN))

  def load(self, design: edgir.Design) -> None:
    self.port_links = {}
    self.block = Block(tfu.Path.empty(), design.contents)

    def simplify_block_recursive(block: Block):
      transform_simplify_bridge(block)
      transform_simplify_adapter(block)
      for subblock_name, subblock_obj in block.subblocks.items():
        simplify_block_recursive(subblock_obj)
    simplify_block_recursive(self.block)

    def register_block(block: Block):
      for _, subblock in block.subblocks.items():
        register_block(subblock)
      for _, sublink in block.sublinks.items():
        self.port_links.setdefault(sublink.path(), set()).add(sublink)
        for port_path in sublink.all_ports():
          # TODO this should be processed in the model
          port_path = tfu.Path(port_path.blocks, port_path.links, (port_path.ports[0], ), ())
          self.port_links.setdefault(port_path, set()).add(sublink)
    register_block(self.block)

    self.scale.config(to=self.block.max_depth())
    self.redraw()

  def _moveto_item(self, item: Any) -> None:
    bbox = self.canvas.bbox(ALL)
    bbox_width = bbox[2] - bbox[0]
    bbox_height = bbox[3] - bbox[1]
    item_coords = self.canvas.bbox(item)
    item_width = item_coords[2] - item_coords[0]
    item_height = item_coords[3] - item_coords[1]
    topleft = (self.canvas.canvasx(0), self.canvas.canvasy(0))
    botright = (self.canvas.canvasx(self.canvas.winfo_width()), self.canvas.canvasy(self.canvas.winfo_height()))
    view_width = botright[0] - topleft[0]
    view_height = botright[1] - topleft[1]

    def movetox(coord: float) -> None:  # move left edge to canvas coordinates
      scrollregion = bbox_width + self.CANVAS_SCROLL_MARGIN * 2
      self.canvas.xview_moveto((coord - bbox[0] + self.CANVAS_SCROLL_MARGIN) / scrollregion)

    def movetoy(coord: float) -> None:  # move top edge to canvas coordinates
      scrollregion = bbox_height + self.CANVAS_SCROLL_MARGIN * 2
      self.canvas.yview_moveto((coord - bbox[1] + self.CANVAS_SCROLL_MARGIN) / scrollregion)

    if item_coords[0] < topleft[0] and item_coords[2] > botright[0]:  # contained in viewscreen, don't move
      pass
    elif item_coords[0] < topleft[0]:  # left edge to left of viewport
      if item_width + self.CANVAS_SCROLL_MARGIN * 2 <= view_width:  # fits in viewport
        # entire object + margin appears onscreen
        movetox(item_coords[0] - self.CANVAS_SCROLL_MARGIN)
      else:  # does not fit in viewport
        # "drag" item as fat as possible + margin
        movetox(item_coords[2] + self.CANVAS_SCROLL_MARGIN - view_width)
    elif item_coords[2] > botright[0]:  # right edge to right of viewport
      if item_width + self.CANVAS_SCROLL_MARGIN * 2 <= view_width:
        movetox(item_coords[2] + self.CANVAS_SCROLL_MARGIN - view_width)
      else:
        movetox(item_coords[0] - self.CANVAS_SCROLL_MARGIN)

    if item_coords[1] < topleft[1] and item_coords[3] > botright[1]:  # contained in viewscreen, don't move
      pass
    if item_coords[1] < topleft[1]:  # top edge to top of viewport
      if item_height + self.CANVAS_SCROLL_MARGIN * 2 <= view_height:
        movetoy(item_coords[1] - self.CANVAS_SCROLL_MARGIN)
      else:
        movetoy(item_coords[3] + self.CANVAS_SCROLL_MARGIN - view_height)
    elif item_coords[3] > botright[1]:  # bottom edge to bottom of viewport
      if item_height + self.CANVAS_SCROLL_MARGIN * 2 <= view_height:
        movetoy(item_coords[3] + self.CANVAS_SCROLL_MARGIN - view_height)
      else:
        movetoy(item_coords[1] - self.CANVAS_SCROLL_MARGIN)

  def select_path(self, path: Optional[tfu.Path]) -> None:
    for item in self.selected_items:
      if item in self.block_item_path:
        self.canvas.itemconfig(item, fill=self.BLOCK_FILL)
      elif item in self.port_item_path:
        self.canvas.itemconfig(item, fill=self.PORT_FILL)
      elif item in self.link_item_path:
        self.canvas.itemconfig(item, fill=self.LINK_FILL, width=self.LINK_WIDTH)

    if path is not None:
      def process_link(path: tfu.Path, seen_blocks: Set[tfu.Path]):
        for link in self.port_links.get(path, set()):
          link_block_path = link.path().block_component()
          if link_block_path not in seen_blocks:
            for link_item in self.link_item_path.get_by_value(link.path()):
              self.canvas.itemconfig(link_item, fill=self.LINK_SELECT_INDIRECT_FILL, width=self.LINK_SELECT_WIDTH)
              self.selected_items.append(link_item)
            for link_port in link.all_ports():
              # TODO this should be processed in the model
              link_port_path = tfu.Path(link_port.blocks, link_port.links, (link_port.ports[0], ), ())
              for port_item in self.port_item_path.get_by_value(link_port_path):
                self.canvas.itemconfig(port_item, fill=self.PORT_SELECT_INDIRECT_FILL)
                self.selected_items.append(port_item)
              process_link(link_port_path, seen_blocks.union({link_block_path}))
      process_link(path, set())

      for block_item in self.block_item_path.get_by_value(path):
        self.canvas.itemconfig(block_item, fill=self.BLOCK_SELECT_FILL)
        self.selected_items.append(block_item)
        self._moveto_item(block_item)
      for port_item in self.port_item_path.get_by_value(path):
        self.canvas.itemconfig(port_item, fill=self.PORT_SELECT_FILL)
        self.selected_items.append(port_item)
      for link_item in self.link_item_path.get_by_value(path):
        self.canvas.itemconfig(link_item, fill=self.LINK_SELECT_FILL, width=self.LINK_SELECT_WIDTH)
        self.selected_items.append(link_item)
