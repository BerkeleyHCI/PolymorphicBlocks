from typing import TypeVar, Generic, Mapping, Union, Dict

from .. import edgir
from .ScalaCompilerInterface import CompiledDesign
from .TransformUtil import TransformContext, Path

# these type vars define the post-transform-result of blocks, ports, or links
# these can be set to None if unused
TransformedPort = TypeVar("TransformedPort", default=None)
TransformedBlock = TypeVar("TransformedBlock", default=None)
TransformedLink = TypeVar("TransformedLink", default=None)


class FnTransformBase(Generic[TransformedPort, TransformedBlock, TransformedLink]):
    """A design tree walking / transform base class that provides the traversal structure.
    Supports both pre-order processing (through the `visit_*` methods) and post-order processing
    (through the `transform_*` methods, which are given the post-order results of their elements).
    """

    def __init__(self, design: CompiledDesign) -> None:
        self._design = design

    def transform(self) -> TransformedBlock:
        """Entry point for the transform. Transforms the design and returns the result.
        Should only be called once per object, undefined behavior if called multiple times."""
        context = TransformContext(Path.empty(), self._design.contents)
        return self.visit_block(context, self._design.contents)

    def _visit_portlike(self, context: TransformContext, elt: edgir.PortLike) -> TransformedPort:
        if elt.HasField("port"):
            return self.visit_port(context, elt.port)
        elif elt.HasField("array"):
            return self.visit_port(context, elt.array)
        elif elt.HasField("lib_elem"):
            raise ValueError(f"unresolved PortLike lib at {context}")
        else:
            raise ValueError(f"unknown PortLike type {elt.WhichOneof('is')} at {context}")

    def _visit_blocklike(self, context: TransformContext, elt: edgir.BlockLike) -> TransformedBlock:
        if elt.HasField("hierarchy"):
            return self.visit_block(context, elt.hierarchy)
        elif elt.HasField("lib_elem"):
            raise ValueError(f"unresolved BlockLike lib at {context}")
        else:
            raise ValueError(f"unknown BlockLike type {elt.WhichOneof('type')} at {context}")

    def _visit_linklike(self, context: TransformContext, elt: edgir.LinkLike) -> TransformedLink:
        if elt.HasField("link"):
            return self.visit_link(context, elt.link)
        elif elt.HasField("array"):
            return self.visit_link(context, elt.array)
        elif elt.HasField("lib_elem"):
            raise ValueError(f"unresolved LinkLike lib at {context}")
        else:
            raise ValueError(f"unknown LinkLike type {elt.WhichOneof('type')} at {context}")

    def visit_port(self, context: TransformContext, elt: Union[edgir.Port, edgir.PortArray]) -> TransformedPort:
        """visit_block, but for ports."""
        transformed_ports: Dict[str, TransformedPort] = {}
        if isinstance(elt, edgir.Port):
            for port_pair in elt.ports:
                transformed_ports[port_pair.name] = self._visit_portlike(
                    context.append_port(port_pair.name), port_pair.value
                )
        elif isinstance(elt, edgir.PortArray):
            for port_pair in elt.ports.ports:
                transformed_ports[port_pair.name] = self._visit_portlike(
                    context.append_port(port_pair.name), port_pair.value
                )
        else:
            raise TypeError(f"unknown Port type {elt.WhichOneof('is')} at {context}")
        return self.transform_port(context, elt, transformed_ports)

    def visit_block(self, context: TransformContext, elt: edgir.HierarchyBlock) -> TransformedBlock:
        """Called during root-down traversal of the design. Returns the transformed results.
        This call "lasts" for the duration of traversal of the block and all its contained elements.
        Optionally add pre-hooks for pre-order processing."""
        transformed_ports: Dict[str, TransformedPort] = {}
        for port_pair in elt.ports:
            transformed_ports[port_pair.name] = self._visit_portlike(
                context.append_port(port_pair.name), port_pair.value
            )
        transformed_blocks: Dict[str, TransformedBlock] = {}
        for block_pair in elt.blocks:
            transformed_blocks[block_pair.name] = self._visit_blocklike(
                context.append_block(block_pair.name), block_pair.value
            )
        transformed_links: Dict[str, TransformedLink] = {}
        for link_pair in elt.links:
            transformed_links[link_pair.name] = self._visit_linklike(
                context.append_link(link_pair.name), link_pair.value
            )
        return self.transform_block(context, elt, transformed_ports, transformed_blocks, transformed_links)

    def visit_link(self, context: TransformContext, elt: Union[edgir.Link, edgir.LinkArray]) -> TransformedLink:
        """visit_block, but for links."""
        transformed_ports: Dict[str, TransformedPort] = {}
        for port_pair in elt.ports:
            transformed_ports[port_pair.name] = self._visit_portlike(
                context.append_port(port_pair.name), port_pair.value
            )
        transformed_links: Dict[str, TransformedLink] = {}
        for link_pair in elt.links:
            transformed_links[link_pair.name] = self._visit_linklike(
                context.append_link(link_pair.name), link_pair.value
            )
        return self.transform_link(context, elt, transformed_ports, transformed_links)

    def transform_port(
        self,
        context: TransformContext,
        elt: Union[edgir.Port, edgir.PortArray],
        ports: Mapping[str, TransformedPort],
    ) -> TransformedPort:
        """transform_block, but for ports."""
        return None  # type: ignore

    def transform_block(
        self,
        context: TransformContext,
        elt: edgir.HierarchyBlock,
        ports: Mapping[str, TransformedPort],
        blocks: Mapping[str, TransformedBlock],
        links: Mapping[str, TransformedLink],
    ) -> TransformedBlock:
        """Called after all of a block's contained elements have been transformed, and is given the results of those
        transforms. Returns the transformed result of the block itself."""
        return None  # type: ignore

    def transform_link(
        self,
        context: TransformContext,
        elt: Union[edgir.Link, edgir.LinkArray],
        ports: Mapping[str, TransformedPort],
        links: Mapping[str, TransformedLink],
    ) -> TransformedLink:
        """transform_block, but for links."""
        return None  # type: ignore
