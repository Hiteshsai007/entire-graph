"""Payment API — public charge() function.

This is the symbol GraphGuard will analyze. It is public (no _ prefix),
has direct callers (process_order), and transitive callers (notify_and_bill).
"""


def charge(customer_id: str, amount: float) -> dict:
    """Charge a customer. Returns a receipt dict.

    This is the primary entry point for payments.
    Changes here affect process_order and notify_and_bill transitively.
    """
    if amount <= 0:
        raise ValueError("Amount must be positive")
    if not customer_id:
        raise ValueError("Customer ID required")
    receipt = {
        "customer_id": customer_id,
        "amount": amount,
        "status": "charged",
        "currency": "USD",
    }
    return receipt
