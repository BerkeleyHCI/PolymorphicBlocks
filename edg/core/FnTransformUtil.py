from typing import TypeVar, Generic, Mapping, Union

from .. import edgir
from .TransformUtil import TransformContext, Path

# these type vars define the post-transform-result of blocks, ports, or links
# these can be set to None if unused
TransformedBlock = TypeVar("TransformedBlock", default=None)
TransformedPort = TypeVar("TransformedPort", default=None)
TransformedLink = TypeVar("TransformedLink", default=None)


class FnTransformBase(Generic[TransformedBlock, TransformedPort, TransformedLink]):
    """A design tree walking / transform base class that provides the traversal structure.
    Supports both pre-order processing (through the `visit_*` methods) and post-order processing
    (through the `transform_*` methods, which are given the post-order results of their elements).
    """

    def transform(self, design: edgir.Design) -> TransformedBlock:
        """Entry point for the transform. Transforms the design and returns the  result."""
        context = TransformContext(Path.empty(), design)
        return self.visit_block(context, design.contents)

    def _visit_blocklike(self, context: TransformContext, elt: edgir.BlockLike) -> TransformedBlock:
        pass

    def _visit_portlike(self, context: TransformContext, elt: edgir.PortLike) -> TransformedBlock:
        pass

    def _visit_linklike(self, context: TransformContext, elt: edgir.LinkLike) -> TransformedBlock:
        pass

    def visit_block(self, context: TransformContext, block: edgir.HierarchyBlock) -> TransformedBlock:
        """Called during root-down traversal of the design. Returns the transformed results.
        This call "lasts" for the duration of traversal of the block and all its contained elements.
        Optionally add pre-hooks for pre-order processing."""
        pass

    def visit_port(self, context: TransformContext, port: Union[edgir.Port, edgir.PortArray]) -> TransformedPort:
        """visit_block, but for ports."""
        pass

    def visit_link(self, context: TransformContext, link: edgir.Link) -> TransformedLink:
        """visit_block, but for links."""
        pass

    def transform_block(
        self,
        context: TransformContext,
        elt: edgir.HierarchyBlock,
        blocks: Mapping[str, TransformedBlock],
        ports: Mapping[str, TransformedPort],
        links: Mapping[str, TransformedLink],
    ) -> TransformedBlock:
        """Called after all of a block's contained elements have been transformed, and is given the results of those
        transforms. Returns the transformed result of the block itself."""
        raise NotImplementedError

    def transform_port(
        self,
        elt: Union[edgir.Port, edgir.PortArray],
        ports: Mapping[str, TransformedPort],
    ) -> TransformedPort:
        """Post-order processing of a port. By default, returns the port unchanged."""
        raise NotImplementedError

    def transform_link(
        self,
        elt: edgir.Link,
        ports: Mapping[str, TransformedPort],
        links: Mapping[str, TransformedLink],
    ) -> TransformedLink:
        """Post-order processing of a link. By default, returns the link unchanged."""
        raise NotImplementedError
