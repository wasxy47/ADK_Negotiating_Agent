from mcp.server.fastmcp import FastMCP
import json

mcp = FastMCP("CRM")

# ── Mock CRM Database ──────────────────────────────────────────────────────────
CRM_DB = {
    "user_123": {
        "name": "Alice Smith",
        "lifetime_value": 850000.0,
        "total_orders": 4,
        "past_purchases": ["Mechanical Keyboard", "Titanium Smartwatch"],
        "accepted_mrp_before": True,
        "walked_away_before": False,
        "preferred_categories": ["Accessories", "Wearables"],
        "notes": "Loyal customer, price-conscious but values quality. Has accepted full price twice."
    },
    "user_456": {
        "name": "Bob Jones",
        "lifetime_value": 0.0,
        "total_orders": 0,
        "past_purchases": [],
        "accepted_mrp_before": False,
        "walked_away_before": False,
        "preferred_categories": [],
        "notes": "First-time visitor. No purchase history. Approach with standard consultative pitch."
    },
}


@mcp.tool()
def get_customer_profile(user_id: str) -> str:
    """
    Fetches the full customer profile: name, purchase history, lifetime value,
    whether they have accepted MRP in the past, and negotiation behaviour notes.
    Use this at the START of every negotiation session to understand who you are dealing with.
    """
    profile = CRM_DB.get(user_id)
    if not profile:
        return json.dumps({
            "name": "Guest Customer",
            "lifetime_value": 0.0,
            "total_orders": 0,
            "past_purchases": [],
            "accepted_mrp_before": False,
            "walked_away_before": False,
            "preferred_categories": [],
            "notes": "Unknown customer. Treat as new visitor. Use full consultative approach."
        }, indent=2)
    return json.dumps(profile, indent=2)


@mcp.tool()
def log_negotiation_outcome(user_id: str, product_id: str, outcome: str, final_price: float) -> str:
    """
    Logs the result of a negotiation session to the CRM for future reference.
    Call this at the END of every session (deal or no-deal).
    outcome must be one of: 'sold_at_mrp', 'sold_with_concession', 'customer_walked_away', 'negotiation_failed'
    final_price is the price the customer agreed to (or 0 if no deal).
    """
    valid_outcomes = ["sold_at_mrp", "sold_with_concession", "customer_walked_away", "negotiation_failed"]
    if outcome not in valid_outcomes:
        return json.dumps({"error": f"Invalid outcome. Must be one of: {valid_outcomes}"})

    # In a real system this would persist to DB. Here we return a confirmation.
    return json.dumps({
        "logged": True,
        "user_id": user_id,
        "product_id": product_id,
        "outcome": outcome,
        "final_price": final_price,
        "message": "Negotiation outcome recorded successfully."
    }, indent=2)


if __name__ == "__main__":
    mcp.run()
