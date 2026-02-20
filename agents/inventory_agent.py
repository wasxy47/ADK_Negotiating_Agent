import json
from adk.engine import Agent
from mcp_servers.inventory_server import check_stock, reserve_inventory


def handoff_to_order(product_id: str, agreed_price: float, reserved_qty: int) -> str:
    """
    Transfers the conversation to the Order Taking Agent after stock has been
    successfully reserved. Pass the product_id, agreed_price and reserved_qty.
    """
    return json.dumps({
        "handoff_to": "OrderTaking",
        "product_id": product_id,
        "agreed_price": agreed_price,
        "reserved_qty": reserved_qty
    })


def end_transaction(reason: str) -> str:
    """
    Ends the transaction if the item is out of stock and no alternatives exist.
    Apologise sincerely to the customer before calling this.
    """
    return json.dumps({"handoff_to": "None", "reason": reason})


inventory_instructions = """
You are the Inventory Verification System — a silent, efficient backend agent.
The customer has agreed to a price. Your job is to lock in their item before they proceed to payment.

RULES:
1. Extract the product_id and agreed_price from the shared context (it was passed by the previous agent).
2. Immediately call check_stock for the product. Do NOT wait for user input.
3. If in_stock is True, call reserve_inventory for 1 unit immediately.
4. If reservation succeeds, call handoff_to_order with product_id, agreed_price, and reserved_qty=1.
   Briefly reassure the customer: "Great news — your item is reserved. Moving you to checkout now!"
5. If out of stock, sincerely apologise and call end_transaction.
   Suggestion: "I'm sorry — that item just went out of stock. Would you like to explore an alternative?"

Keep your messages brief. You are a background process — the customer should barely notice the transition.
"""

inventory_agent = Agent(
    name="Inventory",
    instructions=inventory_instructions,
    tools=[check_stock, reserve_inventory, handoff_to_order, end_transaction]
)
