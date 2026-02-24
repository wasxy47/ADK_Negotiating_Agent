from mcp.server.fastmcp import FastMCP
import json
import uuid

mcp = FastMCP("Payment")

@mcp.tool()
def validate_shipping_address(street: str, city: str, zip_code: str, country: str) -> str:
    """
    Validates the shipping address format.
    """
    # Simple mock logic
    if not zip_code or len(zip_code) < 4:
        return json.dumps({"valid": False, "reason": "Invalid zip code format."})
    return json.dumps({"valid": True, "normalized_address": f"{street}, {city}, {zip_code}, {country}"})

@mcp.tool()
def process_payment(user_id: str, amount: float, payment_method: str) -> str:
    """
    Processes a simulated payment and returns a transaction ID if successful.
    """
    if payment_method == "DECLINED_TOKEN":
        return json.dumps({"success": False, "reason": "Card declined by bank."})
        
    transaction_id = str(uuid.uuid4())
    return json.dumps({
        "success": True, 
        "transaction_id": transaction_id, 
        "amount_processed": amount,
        "status": "APPROVED"
    })

@mcp.tool()
def generate_invoice(user_id: str, product_id: str, agreed_price: float, transaction_id: str) -> str:
    """
    Generates the final invoice to push to the fulfillment system.
    """
    invoice_id = f"INV-{str(uuid.uuid4())[:8]}"
    return json.dumps({
        "invoice_id": invoice_id,
        "user_id": user_id,
        "product_id": product_id,
        "total_paid": agreed_price,
        "transaction_reference": transaction_id,
        "fulfillment_status": "READY_TO_SHIP"
    }, indent=2)

if __name__ == "__main__":
    mcp.run()
