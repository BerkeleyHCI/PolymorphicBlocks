from typing import TypeVar, Generic, Type, List, Optional, get_args, get_origin, Tuple, Callable

from .Core import non_library, HasMetadata
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
    BaseType = TypeVar('BaseType', bound=HasMetadata)
    @classmethod
    def _get_bases_of(cls, base_type: Type[BaseType]) -> Tuple[List[Type[BaseType]], List[Type[BaseType]]]:
        ordered_direct_bases, ordered_indirect_bases = super()._get_bases_of(base_type)
        if cls._is_mixin():  # adds the mixin base defined in MixinBaseType to the list of bases
            mixin_base = cls._get_mixin_base()
            all_bases = ordered_direct_bases + ordered_indirect_bases
            all_bases_has_mixin_base = map(lambda bcls: issubclass(bcls, BlockInterfaceMixin) and
                                                        bcls._get_mixin_base() == mixin_base,
                                           all_bases)

            if any(all_bases_has_mixin_base):  # mixin has been inherited, add mixin base to the end
                ordered_indirect_bases.append(mixin_base)  # type: ignore
            else:  # mixin has not been inherited, add to the end of direct bases
                ordered_direct_bases.append(mixin_base)  # type: ignore

        return ordered_direct_bases, ordered_indirect_bases

    @classmethod
    def _get_mixin_base(cls) -> Type['BlockInterfaceMixin']:
        mixin_base: Optional[Type[BlockInterfaceMixin]] = None
        for bcls in cls.__orig_bases__:  # type: ignore
            if get_origin(bcls) == BlockInterfaceMixin:
                bcls_args = get_args(bcls)
                if mixin_base is not None or len(bcls_args) != 1:
                    raise BlockDefinitionError(cls, "multiple mixin bases defined")
                mixin_base = bcls_args[0]
        if mixin_base is None:
            raise BlockDefinitionError(cls, "no mixin base defined")
        if (mixin_base, AbstractBlockProperty) not in mixin_base._elt_properties:
            raise BlockDefinitionError(cls, "mixin base must be abstract")
        return mixin_base

    @classmethod
    def _is_mixin(cls) -> bool:
        return BlockInterfaceMixin in cls.__bases__ or\
            all(map(lambda bcls: issubclass(bcls, BlockInterfaceMixin) and bcls._is_mixin(), cls.__bases__))

    def __init__(self):
        super().__init__()
        if self._is_mixin():  # all mixins must be abstract
            self._elt_properties[(self.__class__, AbstractBlockProperty)] = None

    def implementation(self, fn: Callable[[MixinBaseType], None]) -> None:
        """Wrap implementation definitions (where MixinBaseType is required) in this. This is only called
        in a concrete class, and ignored when the standalone mixin is instantiated."""
        if not self._is_mixin():
            assert isinstance(self, self._get_mixin_base())
            fn(self)  # type: ignore
