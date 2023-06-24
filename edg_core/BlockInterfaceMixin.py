from abc import ABC
from typing import TypeVar, Generic
from .HierarchyBlock import BaseBlock, Block

MixinBaseType = TypeVar('MixinBaseType', bound=Block)


class BlockInterfaceMixin(BaseBlock, Generic[MixinBaseType], ABC):
    """An interface mixin, allowing additional interface elements (parameters, ports) to be added to
    a block interface - e.g., IoController with HasI2s.

    This class should be directly part of the superclass list for an implementing class
    (e.g. Nrf52840 which has I2S should extend HasI2s).

    This class should only be directly instantiated when adding the mixin interfaces to an abstract
    class, e.g. IoController.with(HasI2s()). Instances of this class are not really valid on their own.

    This may define __init__ parameters as keyword arguments ONLY. Otherwise, this can mess up
    parameter propagation in super().__init__ calls in implementing classes."""
    pass

