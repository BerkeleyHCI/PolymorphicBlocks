from typing import TypeVar, Generic

import edgir
from .HierarchyBlock import BaseBlock, Block

MixinBaseType = TypeVar('MixinBaseType', bound=Block)


class BlockInterfaceMixin(BaseBlock[edgir.HierarchyBlock], Generic[MixinBaseType]):
    """An interface mixin, allowing additional interface elements (parameters, ports) to be added to
    a block interface - e.g., IoController with HasI2s.

    This class should be directly part of the superclass list for an implementing class
    (e.g. Nrf52840 which has I2S should extend HasI2s).

    This class should only be directly instantiated when adding the mixin interfaces to an abstract
    class, e.g. IoController.with(HasI2s()). Instances of this class are not really valid on their own.

    This may define __init__ parameters as keyword arguments ONLY. Otherwise, this can mess up
    parameter propagation in super().__init__ calls in implementing classes.

    This should only be used for defining interface mixins. Implementation mixins should be defined
    using the Block class hierarchy. This class does not inherit Block to avoid inheriting the
    ports of the mixin base class which reduces autocomplete clutter.
    TODO: is this a good decision?
    TODO: what about cases where it's a bit mixed, e.g. HasI2s also needs to register the self.i2s port?
    """
    def __init__(self):
        super().__init__()
        # TODO implement me
        pass

    def contents(self) -> None:
        # TODO implement me
        pass


