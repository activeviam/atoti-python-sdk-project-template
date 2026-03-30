from collections.abc import Callable, Coroutine
from functools import wraps
from inspect import iscoroutinefunction, isfunction
from typing import Final

from opentelemetry import trace

TRACER: Final = trace.get_tracer(__name__)


def traced[**P, R](func: Callable[P, R], /) -> Callable[P, R]:
    """Thin wrapper around :meth:`opentelemetry.trace.Tracer.start_as_current_span`'s automatically using the decorated's function qualified name as the span name."""
    assert isfunction(func)

    if iscoroutinefunction(func):

        @wraps(func)
        async def wrapper(
            *args: P.args, **kwargs: P.kwargs
        ) -> Coroutine[object, object, R]:
            with TRACER.start_as_current_span(func.__qualname__):
                return await func(*args, **kwargs)

        return wrapper  # ty: ignore[invalid-return-type]

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        with TRACER.start_as_current_span(func.__qualname__):
            return func(*args, **kwargs)

    return wrapper
