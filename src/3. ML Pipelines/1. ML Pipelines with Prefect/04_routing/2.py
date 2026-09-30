"""
Multi-Branch Routing

Demonstrates routing to multiple destinations:
- Evaluate a metric
- Route to one of several flows based on thresholds

Question: How do I route to more than two destinations?
"""

from prefect import flow


@flow
def calculate_priority(order: dict) -> str:
    """
    Calculate order priority based on value and urgency.

    Returns: "critical", "high", "medium", or "low"
    """
    value = order.get("value", 0)
    urgent = order.get("urgent", False)

    if value > 1000 and urgent:
        return "critical"
    elif value > 500 or urgent:
        return "high"
    elif value > 100:
        return "medium"
    else:
        return "low"


@flow
def handle_critical(order: dict) -> str:
    """Handle critical priority orders"""
    print(f"[CRITICAL] Immediate escalation: order #{order['id']}")
    print("  -> Notifying on-call team")
    print("  -> Expedited processing")
    return "critical_handled"


@flow
def handle_high(order: dict) -> str:
    """Handle high priority orders"""
    print(f"[HIGH] Priority processing: order #{order['id']}")
    print("  -> Fast-track queue")
    return "high_handled"


@flow
def handle_medium(order: dict) -> str:
    """Handle medium priority orders"""
    print(f"[MEDIUM] Standard processing: order #{order['id']}")
    print("  -> Normal queue")
    return "medium_handled"


@flow
def handle_low(order: dict) -> str:
    """Handle low priority orders"""
    print(f"[LOW] Batch processing: order #{order['id']}")
    print("  -> Batched for later")
    return "low_handled"


@flow
def multi_branch_routing(order: dict) -> str:
    """
    Route to one of four handlers based on priority.

    Multi-branch pattern using a dispatch dictionary.
    """
    print("=" * 50)
    print("ROUTING PIPELINE - Multi-Branch")
    print("=" * 50)
    print()

    print(f"Order: #{order['id']}, value=${order['value']}, urgent={order['urgent']}")

    # Calculate priority
    priority = calculate_priority(order)
    print(f"Calculated priority: {priority.upper()}")
    print()

    # Dispatch to appropriate handler
    handlers = {
        "critical": handle_critical,
        "high": handle_high,
        "medium": handle_medium,
        "low": handle_low,
    }

    handler = handlers[priority]
    result = handler(order)

    print()
    print("=" * 50)
    print("Routing complete!")
    print("=" * 50)

    return result


if __name__ == "__main__":
    orders = [
        {"id": 1, "value": 2000, "urgent": True},   # critical
        {"id": 2, "value": 800, "urgent": False},   # high
        {"id": 3, "value": 200, "urgent": False},   # medium
        {"id": 4, "value": 50, "urgent": False},    # low
    ]

    for order in orders:
        print(f"\n{'='*60}\n")
        result = multi_branch_routing(order)
        print(f"\nResult: {result}")
