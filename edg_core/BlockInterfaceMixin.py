from typing import TypeVar, Generic, Type, List, Optional, get_args, get_origin

from .Core import non_library
from .Blocks import AbstractBlockProperty
from .HdlUserExceptions import BlockDefinitionError
from .HierarchyBlock import Block

MixinBaseType = TypeVar('MixinBaseType', bound='Block')


@non_library
class BlockInterfaceMixin(Block, Generic[MixinBaseType]):
    """An interface mixin, allowing additional interface elements (parameters, ports) to be added to
    a block interface - e.g., IoController with HasI2s.

    This class should be directly part of the superclass list for an implementing class
    (e.g. Nrf52840 which has I2S should extend HasI2s).

    This class should only be directly instantiated when adding the mixin interfaces to an abstract
    class, e.g. IoController.with(HasI2s()). Instances of this class are not really valid on their own.

    This may define __init__ parameters as keyword arguments ONLY. Otherwise, this can mess up
    parameter propagation in super().__init__ calls in implementing classes.

    This should only be used for defining interface mixins. Implementation mixins should be defined
    using the standard Block class hierarchy, however this acts like any Block just with mixin capabilities.
    TODO: is this a good decision?
    TODO: what about cases where it's a bit mixed, e.g. HasI2s also needs to register the self.i2s port?
    """
    BaseType = TypeVar('BaseType', bound='HasMetadata')
    @classmethod
    def _get_bases_of(cls, base_type: Type[BaseType]) -> List[Type[BaseType]]:
        # adds the mixin base defined in MixinBaseType to the list of bases
        normal_bases = super()._get_bases_of(base_type)  # still handle the mixin hierarchy
        mixin_base: Optional[BlockInterfaceMixin] = None
        for bcls in cls.__orig_bases__:
            if get_origin(bcls) == BlockInterfaceMixin:
                bcls_args = get_args(bcls)
                if mixin_base is not None or len(bcls_args) != 1:
                    raise BlockDefinitionError("multiple mixin bases defined")
                mixin_base = bcls_args[0]
        if mixin_base is None:
            raise BlockDefinitionError("no mixin base defined")
        normal_bases.insert(0, mixin_base)
        return normal_bases

    @classmethod
    def _is_mixin(cls) -> bool:
        return BlockInterfaceMixin in cls.__bases__

    def __init__(self):
        super().__init__()
        if self._is_mixin():
            self._elt_properties[(self.__class__, AbstractBlockProperty)] = None

        # TODO implement me

        pass
