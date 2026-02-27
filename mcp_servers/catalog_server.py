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
        "stock": 5,
        "image_url": "https://images.unsplash.com/photo-1593640408182-31c70c8268f5?w=500&q=80",
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
        "stock": 12,
        "image_url": "https://images.unsplash.com/photo-1585435465945-bef5a93f8849?w=500&q=80",
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
        "stock": 8,
        "image_url": "https://images.unsplash.com/photo-1622979135225-d2ba269cf1ac?w=500&q=80",
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
        "stock": 25,
        "image_url": "https://images.unsplash.com/photo-1595225476474-87563907a212?w=500&q=80",
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
        "stock": 3,
        "image_url": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=500&q=80",
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
        "stock": 15,
        "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&q=80",
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
        "stock": 42,
        "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=500&q=80",
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
    {
        "id": "p8",
        "name": "Pro Smartphone",
        "mrp": 350000.0,
        "price": 315000.0,
        "cost_price": 240000.0,
        "stock": 18,
        "image_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500&q=80",
        "category": "Mobile",
        "description": "Flagship titanium smartphone with a pro-grade triple camera system and satellite connectivity.",
        "key_features": [
            "Aero-grade titanium frame with ceramic shield glass",
            "Pro camera system (48MP Main, Ultrawide, 5x Telephoto)",
            "Always-On ProMotion OLED display (1-120Hz)",
            "Satellite SOS and Crash Detection",
            "All-day battery life with fast 45W charging"
        ]
    },
    {
        "id": "p9",
        "name": "Smart Home Hub",
        "mrp": 45000.0,
        "price": 38000.0,
        "cost_price": 28000.0,
        "stock": 30,
        "image_url": "https://images.unsplash.com/photo-1558089687-f282ffcbc126?w=500&q=80",
        "category": "Smart Home",
        "description": "Unified smart home controller with an edge AI processor for totally private, offline automation.",
        "key_features": [
            "Matter and Thread border router built-in",
            "Local Edge AI processing — no cloud subscription required",
            "Compatible with 50,000+ smart devices",
            "10.1-inch wall-mountable HD touchscreen display",
            "Built-in siren and physical privacy shutter for camera"
        ]
    },
    {
        "id": "p10",
        "name": "Pro Drone",
        "mrp": 180000.0,
        "price": 165000.0,
        "cost_price": 125000.0,
        "stock": 7,
        "image_url": "https://images.unsplash.com/photo-1507582020474-9a35b7d455d9?w=500&q=80",
        "category": "Electronics",
        "description": "Foldable cinematic drone featuring a Hasselblad camera and omnidirectional obstacle sensing.",
        "key_features": [
            "4/3 CMOS Hasselblad Camera — 5.1K/50fps video",
            "46-minute max flight time",
            "Omnidirectional obstacle sensing with APAS 5.0",
            "O3+ Video Transmission (15km range)",
            "ActiveTrack 5.0 for cinematic subject following"
        ]
    },
    {
        "id": "p11",
        "name": "Ultra-Wide Gaming Monitor",
        "mrp": 120000.0,
        "price": 105000.0,
        "cost_price": 75000.0,
        "stock": 12,
        "image_url": "https://images.unsplash.com/photo-1527443154391-507e9dc6c5cc?w=500&q=80",
        "category": "Computers",
        "description": "49-inch curved ultra-wide gaming monitor with a 1000R curve and 240Hz refresh rate.",
        "key_features": [
            "49-inch Dual QHD resolution (5120x1440)",
            "1000R pronounced curvature for immersion",
            "240Hz refresh rate with 1ms GTG response",
            "G-Sync and FreeSync Premium Pro compatible",
            "Quantum Mini-LED backlighting"
        ]
    },
    {
        "id": "p12",
        "name": "Professional Mirrorless Camera",
        "mrp": 450000.0,
        "price": 415000.0,
        "cost_price": 320000.0,
        "stock": 4,
        "image_url": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=500&q=80",
        "category": "Electronics",
        "description": "Full-frame mirrorless camera for professional hybrid shooters, capable of 8K RAW internal recording.",
        "key_features": [
            "45MP Full-Frame CMOS Sensor",
            "8K RAW internal video up to 60fps",
            "In-Body Image Stabilization (up to 8 stops)",
            "AI-driven autofocus with vehicle/eye tracking",
            "Weather-sealed magnesium alloy body"
        ]
    },
    {
        "id": "p13",
        "name": "Ergonomic Office Chair",
        "mrp": 85000.0,
        "price": 72000.0,
        "cost_price": 42000.0,
        "stock": 25,
        "image_url": "https://images.unsplash.com/photo-1505843490538-5133c6c7d0e1?w=500&q=80",
        "category": "Office",
        "description": "Premium ergonomic chair designed for extreme support during long 12-hour work or gaming sessions.",
        "key_features": [
            "Dynamic lumbar support tracking",
            "Breathable premium mesh back",
            "4D adjustable armrests",
            "Synchro-tilt mechanism with 4 lock positions",
            "10-year comprehensive warranty"
        ]
    },
    {
        "id": "p14",
        "name": "Portable Power Station",
        "mrp": 160000.0,
        "price": 145000.0,
        "cost_price": 95000.0,
        "stock": 10,
        "image_url": "https://media.istockphoto.com/id/1438212129/photo/portable-power-station-solar-electricity-generator-with-mobile-phone-plugged-in-to-charge.webp?a=1&b=1&s=612x612&w=0&k=20&c=fNpZ5ypGOQPdJMPpbvVv9z5coFpa9tB2sYWt5JRcvnY=",
        "category": "Electronics",
        "description": "High-capacity 2048Wh portable lithium-iron-phosphate (LiFePO4) power station for backup and off-grid use.",
        "key_features": [
            "2000W continuous AC output (4000W surge)",
            "Safe LiFePO4 battery (3000+ charge cycles)",
            "Fast charges 0-80% in just 1 hour via wall outlet",
            "Supports up to 800W solar input",
            "13 output ports including 4x AC and 2x 100W USB-C"
        ]
    },
    {
        "id": "p15",
        "name": "Smart Thermostat",
        "mrp": 32000.0,
        "price": 28000.0,
        "cost_price": 18000.0,
        "stock": 35,
        "image_url": "https://images.unsplash.com/photo-1636569608385-58efc32690ea?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8U21hcnQlMjBUaGVybW9zdGF0fGVufDB8fDB8fHww",
        "category": "Smart Home",
        "description": "Learning smart thermostat that optimizes your HVAC system using AI and remote room sensors.",
        "key_features": [
            "AI schedule learning saves up to 26% on HVAC costs",
            "Includes 1 wireless remote room sensor",
            "Crisp glass touchscreen display",
            "Voice control via Alexa, Google Assistant, Siri",
            "Geofencing automatically adjusts temp when you leave"
        ]
    },
    {
        "id": "p16",
        "name": "Wireless Mechanical Mouse",
        "mrp": 18000.0,
        "price": 15000.0,
        "cost_price": 9000.0,
        "stock": 40,
        "image_url": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=500&q=80",
        "category": "Accessories",
        "description": "Ultra-lightweight competitive gaming mouse with a 30K optical sensor and optical-mechanical switches.",
        "key_features": [
            "Ultra-lightweight 58g symmetric design",
            "Flawless 30,000 DPI optical sensor",
            "Lag-free 2.4GHz wireless connection (4000Hz polling rate)",
            "Optical-mechanical switches rated for 90M clicks",
            "80 hours battery life"
        ]
    },
    {
        "id": "p17",
        "name": "Studio Reference Monitors",
        "mrp": 65000.0,
        "price": 58000.0,
        "cost_price": 38000.0,
        "stock": 14,
        "image_url": "https://images.unsplash.com/photo-1545128485-c400e7702796?w=500&q=80",
        "category": "Audio",
        "description": "Pair of active 5-inch studio reference monitors offering incredibly flat frequency response for producers.",
        "key_features": [
            "Bi-amplified Class D 80W output per speaker",
            "5-inch Kevlar low-frequency transducer",
            "1-inch silk dome high-frequency tweeter",
            "Acoustic Space Control switches for room tuning",
            "TRS, XLR, and RCA inputs"
        ]
    },
    {
        "id": "p18",
        "name": "VR Haptic Gloves",
        "mrp": 145000.0,
        "price": 128000.0,
        "cost_price": 85000.0,
        "stock": 6,
        "image_url": "https://images.unsplash.com/photo-1593508512255-86ab42a8e620?w=500&q=80",
        "category": "Gaming",
        "description": "Enterprise-grade force-feedback haptic gloves that let you physically feel virtual objects.",
        "key_features": [
            "Advanced micro-fluidic force feedback system",
            "Sub-millimeter finger tracking accuracy",
            "Allows users to feel textures and resistance in VR",
            "Wireless Bluetooth 5.0 connection",
            "Compatible with major game engines (Unity, Unreal)"
        ]
    },
    {
        "id": "p19",
        "name": "Smart Lighting Kit",
        "mrp": 25000.0,
        "price": 22000.0,
        "cost_price": 12000.0,
        "stock": 50,
        "image_url": "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=500&q=80",
        "category": "Smart Home",
        "description": "Starter kit containing a bridge and 4 color-changing smart LED bulbs to transform your room.",
        "key_features": [
            "16 million colors + tunable warm/cool white",
            "Includes Zigbee network bridge",
            "Syncs with music, movies, and PC games",
            "Energy efficient equivalent to 75W incandescent",
            "Voice control compatible"
        ]
    },
    {
        "id": "p20",
        "name": "Premium Streaming Microphone",
        "mrp": 28000.0,
        "price": 24000.0,
        "cost_price": 14500.0,
        "stock": 22,
        "image_url": "https://images.unsplash.com/photo-1590602847861-f357a9332bbc?w=500&q=80",
        "category": "Audio",
        "description": "Broadcast-quality dynamic USB/XLR microphone ideal for podcasting, streaming, and vocal recording.",
        "key_features": [
            "Dynamic capsule for rich, deep broadcast sound",
            "Voice Isolation Technology blocks background noise",
            "Dual USB-C and XLR connectivity",
            "Built-in headphone jack for zero-latency monitoring",
            "Customizable LED touch panel"
        ]
    },
]

# ── Internal pricing lookup (keyed by product id) ─────────────────────────────
_PRICING = {p["id"]: p for p in CATALOG_DB}


@mcp.tool()
def search_catalog(query: str) -> str:
    """
    Search products by name, category, or description keyword.
    Matches any word in the query against product name, description, and category.
    Returns matching products with name, price, mrp, stock status, and description.
    NEVER reveal cost_price in the output.
    """
    results = []
    # Split into individual tokens so "pro drone" / "professional drone" all find "Pro Drone"
    tokens = [t.strip() for t in query.lower().split() if len(t.strip()) >= 3]
    # Also keep the full query as one option
    full_q = query.lower().strip()

    def matches(item: dict) -> bool:
        searchable = (
            item["name"].lower() + " " +
            item["description"].lower() + " " +
            item["category"].lower()
        )
        # Full phrase match first
        if full_q in searchable:
            return True
        # Any single meaningful token match
        return any(tok in searchable for tok in tokens)

    seen_ids = set()
    for item in CATALOG_DB:
        if matches(item) and item["id"] not in seen_ids:
            seen_ids.add(item["id"])
            results.append({
                "id": item["id"],
                "name": item["name"],
                "mrp": item["mrp"],
                "price": item["price"],
                "category": item["category"],
                "stock_status": "In Stock" if item["stock"] > 0 else "Out of Stock",
                "stock_count": item["stock"],
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
        "stock_status": "In Stock" if item["stock"] > 0 else "Out of Stock",
        "stock_count": item["stock"],
        "description": item["description"],
        "key_features": item["key_features"]
    }, indent=2)


@mcp.tool()
def list_available_products() -> str:
    """
    Returns a brief list of all available products with their selling price and stock.
    Use this if the user asks what we have for sale.
    """
    lines = [f"• {p['name']} — Rs. {p['price']:,.0f} ({'In Stock' if p['stock'] > 0 else 'Out of Stock'})" for p in CATALOG_DB]
    return "We currently carry:\n" + "\n".join(lines)


@mcp.tool()
def deduct_stock(product_id: str, quantity: int = 1) -> str:
    """
    Deducts stock for a product upon successful purchase.
    """
    item = _PRICING.get(product_id)
    if not item:
        return json.dumps({"success": False, "reason": "Product ID not found."})
    if item["stock"] < quantity:
        return json.dumps({"success": False, "reason": "Insufficient stock."})
    
    item["stock"] -= quantity
    return json.dumps({"success": True, "remaining_stock": item["stock"]})


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
