import warnings
from functools import wraps
from typing import Tuple, Callable, ParamSpec, TypeVar, Any

P = ParamSpec("P")
R = TypeVar("R")


def deprecated_param_remap(*params: Tuple[str, str]) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorator to remap deprecated parameter names to new names.

    Args:
        *params: A list of tuples where each tuple contains the old parameter name and the new parameter name.
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(self: Any, *args: Any, **kwargs: Any) -> R:
            for old_param, new_param in params:
                if old_param in kwargs:
                    warnings.warn(
                        f"{old_param} is deprecated and replaced with {new_param}",
                        DeprecationWarning,
                        stacklevel=2,
                    )
                    assert new_param not in kwargs, f"both old {old_param} and new {new_param} parameters specified"
                    kwargs[new_param] = kwargs.pop(old_param)
            return func(self, *args, **kwargs)

        return wrapper  # type: ignore

    return decorator
