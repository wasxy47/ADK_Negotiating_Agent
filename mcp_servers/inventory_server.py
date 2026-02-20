from mcp.server.fastmcp import FastMCP
import json

mcp = FastMCP("Inventory")

# Mock Inventory DB
INVENTORY_DB = {
    "p1": {"stock": 10, "reserved": 2},
    "p2": {"stock": 50, "reserved": 0},
    "p3": {"stock": 3,  "reserved": 3},   # Out of stock (all reserved)
    "p4": {"stock": 100, "reserved": 5},
    "p5": {"stock": 8,  "reserved": 1},   # Pro OLED Monitor
    "p6": {"stock": 25, "reserved": 3},   # Titanium Smartwatch
    "p7": {"stock": 40, "reserved": 0},   # Noise Cancelling Earbuds
}

@mcp.tool()
def check_stock(product_id: str) -> str:
    """
    Real-time check to see how many units of a given product are currently available.
    Available = stock - reserved.
    """
    if product_id not in INVENTORY_DB:
        return json.dumps({"error": "Product not found in inventory system."})
        
    item = INVENTORY_DB[product_id]
    available = item["stock"] - item["reserved"]
    
    return json.dumps({
        "product_id": product_id,
        "total_stock": item["stock"],
        "reserved": item["reserved"],
        "available_to_sell": available,
        "in_stock": available > 0
    }, indent=2)

@mcp.tool()
def reserve_inventory(product_id: str, quantity: int) -> str:
    """
    Temporarily reserves inventory during the validation/negotiation phase to prevent overselling.
    """
    if product_id not in INVENTORY_DB:
        return json.dumps({"success": False, "reason": "Item not found"})
        
    item = INVENTORY_DB[product_id]
    available = item["stock"] - item["reserved"]
    
    if available >= quantity:
        INVENTORY_DB[product_id]["reserved"] += quantity
        return json.dumps({"success": True, "reserved_quantity": quantity})
    else:
        return json.dumps({"success": False, "reason": "Insufficient stock"})

if __name__ == "__main__":
    mcp.run()
