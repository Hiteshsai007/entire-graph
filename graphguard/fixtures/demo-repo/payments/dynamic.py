"""Dynamic dispatch — uses getattr so the graph cannot see the call to charge.

This is the Contradicted demo: GraphGuard will predict no test impact
from this path, but breaking charge will actually break dispatch("charge", ...).
"""

import payments.api as api_module


def dispatch(func_name: str, *args, **kwargs):
    """Dynamically call a function from the payments API module.

    Uses getattr — the graph cannot resolve this call statically.
    This is a known blind spot: reflection/getattr.
    """
    fn = getattr(api_module, func_name, None)
    if fn is None:
        raise AttributeError(f"No function {func_name!r} in payments.api")
    return fn(*args, **kwargs)
