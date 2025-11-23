from __future__ import annotations

from typing import *

from .HdlUserExceptions import *


PrototypeType = TypeVar('PrototypeType')
class BasePrototype(Generic[PrototypeType]):
    """A block/port prototype, that contains a type and arguments, but without constructing the entire object
    and running its (potentially expensive) __init__.

    These classes are created via __new__ override on the class they are meant to prototype."""
    def __init__(self, tpe: Type[PrototypeType], args: Tuple[Any, ...], kwargs: Dict[str, Any]) -> None:
        self._tpe = tpe
        self._args = args
        self._kwargs = kwargs

    def _instantiate(self) -> PrototypeType:
        """Creates and returns a concrete instance of the prototyped type. May be called multiple times."""
        return self._tpe(*self._args, **self._kwargs)  # type: ignore

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._tpe}, args={self._args}, kwargs={self._kwargs})"

    def __getattribute__(self, item: str) -> Any:
        if item.startswith("_"):
            return super().__getattribute__(item)
        else:
            raise AttributeError(f"{self.__class__.__name__} has no attributes, must bind to get a concrete instance, tried to get {item}")

    def __setattr__(self, key: str, value: Any) -> None:
        if key.startswith("_"):
            super().__setattr__(key, value)
        else:
            raise AttributeError(f"{self.__class__.__name__} has no attributes, must bind to get a concrete instance, tried to set {key}")
