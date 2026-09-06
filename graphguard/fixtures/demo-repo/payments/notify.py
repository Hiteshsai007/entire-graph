"""Notification + billing — notify_and_bill() calls process_order().

This is a depth-2 transitive caller of charge.
"""

from payments.processor import process_order


def notify_and_bill(order_id: str, customer_id: str, total: float,
                    email: str) -> dict:
    """Notify customer and bill them.

    Calls process_order() which calls charge() — depth 2 transitive.
    """
    result = process_order(order_id, customer_id, total)
    # Simulate sending notification
    result["notification"] = {
        "email": email,
        "sent": True,
    }
    return result
