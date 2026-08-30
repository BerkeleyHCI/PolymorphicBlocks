import warnings
from functools import wraps
from typing import Tuple, Callable, TypeVar, Any, Union

CallableType = TypeVar("CallableType", bound=Callable[..., Any])


def deprecated_param_remap(*params: Tuple[Union[int, str], str]) -> Callable[[CallableType], CallableType]:
    """Decorator to remap deprecated parameter positional arg or kwarg names to new kwarg names.

    Args:
        *params: A list of tuples where each tuple contains the old positional index (int) or kwarg name (str)
         and the new kwarg name.
    """

    def decorator(func: CallableType) -> CallableType:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # last arg-params first to avoid shifting issues
            sorted_params = sorted(params, key=lambda x: -x[0] if isinstance(x[0], int) else float("inf"))
            for old_param, new_param in sorted_params:
                if isinstance(old_param, int) and old_param < len(args):
                    warnings.warn(
                        f"Positional argument {old_param} (0-based, including self) is deprecated and replaced with {new_param}",
                        DeprecationWarning,
                        stacklevel=2,
                    )
                    if new_param in kwargs:
                        raise ValueError(
                            f"both old positional argument {old_param} and new {new_param} parameter specified"
                        )
                    kwargs[new_param] = args[old_param]
                    args = args[:old_param] + args[old_param + 1 :]
                elif isinstance(old_param, str) and old_param in kwargs:
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
