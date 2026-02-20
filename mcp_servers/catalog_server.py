from mcp.server.fastmcp import FastMCP
import json

mcp = FastMCP("Catalog")

# ── Product Catalog ────────────────────────────────────────────────────────────
# Fields:
#   mrp        – Maximum Retail Price (what the tag shows, anchor price)
#   price      – Current selling/asking price presented to the customer
#   cost_price – What the store paid (INTERNAL — never share with customer)
#   key_features – Selling points for value-based negotiation
# ──────────────────────────────────────────────────────────────────────────────
CATALOG_DB = [
    {
        "id": "p1",
        "name": "Gaming Laptop",
        "mrp": 490000.0,
        "price": 450000.0,
        "cost_price": 350000.0,
        "category": "Computers",
        "description": "High-performance gaming laptop with an RTX 4090 and 240Hz OLED display.",
        "key_features": [
            "NVIDIA RTX 4090 GPU — console-quality ray tracing",
            "240Hz OLED display — butter-smooth visuals with infinite contrast",
            "32GB DDR5 RAM + 2TB NVMe SSD",
            "2-year on-site manufacturer warranty",
            "Thunderbolt 4 & Wi-Fi 7 ready"
        ]
    },
    {
        "id": "p2",
        "name": "Smart Display",
        "mrp": 135000.0,
        "price": 120000.0,
        "cost_price": 85000.0,
        "category": "Electronics",
        "description": "Next-gen smart display that projects 3D holographic interfaces for your smart home.",
        "key_features": [
            "3D holographic projection technology",
            "Compatible with all major smart-home ecosystems",
            "4K resolution with HDR10+",
            "Built-in AI voice assistant",
            "1-year carry-in warranty"
        ]
    },
    {
        "id": "p3",
        "name": "VR Headset",
        "mrp": 280000.0,
        "price": 250000.0,
        "cost_price": 185000.0,
        "category": "Gaming",
        "description": "Fully immersive virtual reality headset with brain-computer interface technology.",
        "key_features": [
            "Brain-computer interface (BCI) — thought-based navigation",
            "8K per-eye resolution — zero screen-door effect",
            "6DoF inside-out tracking, no base stations needed",
            "Integrated spatial audio with head tracking",
            "Access to 500+ exclusive VR game titles"
        ]
    },
    {
        "id": "p4",
        "name": "Mechanical Keyboard",
        "mrp": 21000.0,
        "price": 18500.0,
        "cost_price": 11500.0,
        "category": "Accessories",
        "description": "Ultra-responsive mechanical keyboard featuring optical switches and per-key RGB.",
        "key_features": [
            "Optical switches — 0.2ms actuation, no debounce lag",
            "Per-key RGB with 16.8M colours",
            "Aluminium aircraft-grade body",
            "Hot-swappable switches — no soldering needed",
            "USB-C braided cable + Bluetooth 5.0"
        ]
    },
    {
        "id": "p5",
        "name": "Pro OLED Monitor",
        "mrp": 200000.0,
        "price": 185000.0,
        "cost_price": 138000.0,
        "category": "Computers",
        "description": "Stunning 32-inch 4K OLED monitor with infinite contrast and 1ms response time.",
        "key_features": [
            "32-inch 4K OLED — infinite contrast ratio",
            "1ms response time — zero ghosting",
            "DisplayHDR True Black 400 certified",
            "USB-C 90W power delivery — one cable setup",
            "Factory colour-calibrated — Delta E < 1"
        ]
    },
    {
        "id": "p6",
        "name": "Titanium Smartwatch",
        "mrp": 72000.0,
        "price": 65000.0,
        "cost_price": 44000.0,
        "category": "Wearables",
        "description": "Advanced health tracking smartwatch with a rugged titanium aerospace-grade case.",
        "key_features": [
            "Aerospace-grade titanium case — ultra-light yet indestructible",
            "ECG, SpO2, blood-glucose trend monitoring",
            "18-day battery life in smartwatch mode",
            "5ATM water resistance + MIL-STD-810H rated",
            "GPS + Satellite SOS emergency messaging"
        ]
    },
    {
        "id": "p7",
        "name": "Noise Cancelling Earbuds",
        "mrp": 36000.0,
        "price": 32000.0,
        "cost_price": 19500.0,
        "category": "Audio",
        "description": "True wireless earbuds featuring state-of-the-art active noise cancellation and spatial audio.",
        "key_features": [
            "Industry-leading ANC — blocks up to 42dB of ambient noise",
            "Spatial Audio with dynamic head tracking",
            "11mm custom drivers — audiophile-grade bass",
            "40hr total battery (10hr buds + 30hr case)",
            "IPX5 sweat & water resistant"
        ]
    },
]

# ── Internal pricing lookup (keyed by product id) ─────────────────────────────
_PRICING = {p["id"]: p for p in CATALOG_DB}


@mcp.tool()
def search_catalog(query: str) -> str:
    """
    Search products by name, category, or description keyword.
    Returns matching products with name, price, mrp and description.
    NEVER reveal cost_price in the output.
    """
    results = []
    q = query.lower()
    for item in CATALOG_DB:
        if q in item["name"].lower() or q in item["description"].lower() or q in item["category"].lower():
            results.append({
                "id": item["id"],
                "name": item["name"],
                "mrp": item["mrp"],
                "price": item["price"],
                "category": item["category"],
                "description": item["description"],
                "key_features": item["key_features"]
            })
    if not results:
        return "No products found matching your query."
    return json.dumps(results, indent=2)


@mcp.tool()
def get_product_details(product_id: str) -> str:
    """
    Returns full public details of a single product including key features.
    NEVER reveals cost_price.
    """
    item = _PRICING.get(product_id)
    if not item:
        return "Product ID not found."
    return json.dumps({
        "id": item["id"],
        "name": item["name"],
        "mrp": item["mrp"],
        "price": item["price"],
        "category": item["category"],
        "description": item["description"],
        "key_features": item["key_features"]
    }, indent=2)


@mcp.tool()
def list_available_products() -> str:
    """
    Returns a brief list of all available products with their selling price.
    Use this if the user asks what we have for sale.
    """
    lines = [f"• {p['name']} — Rs. {p['price']:,.0f}" for p in CATALOG_DB]
    return "We currently carry:\n" + "\n".join(lines)


@mcp.tool()
def get_product_pricing_intel(product_id: str) -> str:
    """
    INTERNAL TOOL — FOR NEGOTIATOR AGENT ONLY. Never share these numbers with the customer.
    Returns the cost price, floor price (minimum acceptable: cost + 8% margin),
    MRP, current selling price, and gross margin percentage.
    Use this to know your hard limits before entering any price discussion.
    """
    item = _PRICING.get(product_id)
    if not item:
        return json.dumps({"error": "Product not found."})

    cost = item["cost_price"]
    floor = round(cost * 1.08, 2)          # 8% minimum margin — absolute floor
    selling = item["price"]
    mrp = item["mrp"]
    margin_pct = round(((selling - cost) / selling) * 100, 1)

    return json.dumps({
        "product_id": product_id,
        "product_name": item["name"],
        "mrp": mrp,
        "selling_price": selling,
        "cost_price": cost,
        "floor_price": floor,
        "current_margin_percent": margin_pct,
        "max_concession_from_selling": round(selling - floor, 2),
        "note": "CONFIDENTIAL — Do NOT share cost_price or floor_price with the customer."
    }, indent=2)


if __name__ == "__main__":
    mcp.run()
