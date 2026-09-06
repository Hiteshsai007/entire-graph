"""Payment processor — process_order() calls charge().

This is a direct caller of charge, making it depth-1 in the graph.
"""

from payments.api import charge


def process_order(order_id: str, customer_id: str, total: float) -> dict:
    """Process an order by charging the customer.

    Calls charge() directly — this is a depth-1 caller.
    """
    if not order_id:
        raise ValueError("Order ID required")
    receipt = charge(customer_id, total)
    return {
        "order_id": order_id,
        "receipt": receipt,
        "status": "processed",
    }
