import warnings
from functools import wraps
from typing import Tuple, Callable, TypeVar, Any

CallableType = TypeVar("CallableType", bound=Callable[..., Any])


def deprecated_param_remap(*params: Tuple[str, str]) -> Callable[[CallableType], CallableType]:
    """Decorator to remap deprecated parameter names to new names.

    Args:
        *params: A list of tuples where each tuple contains the old parameter name and the new parameter name.
    """

    def decorator(func: CallableType) -> CallableType:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            for old_param, new_param in params:
                if old_param in kwargs:
                    warnings.warn(
                        f"{old_param} is deprecated and replaced with {new_param}",
                        DeprecationWarning,
                        stacklevel=2,
                    )
                    if new_param in kwargs:
                        raise ValueError(f"both old {old_param} and new {new_param} parameters specified")
                    kwargs[new_param] = kwargs.pop(old_param)
            return func(*args, **kwargs)

        return wrapper  # type: ignore

    return decorator
