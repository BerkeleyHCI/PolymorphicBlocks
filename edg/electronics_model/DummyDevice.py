from ..electronics_model import abstract_block, InternalBlock


@abstract_block
class DummyDevice(InternalBlock):
    """Non-physical "device" used to affect parameters or for unit testing."""

    pass
