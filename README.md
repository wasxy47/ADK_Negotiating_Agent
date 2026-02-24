# 🤖 ADK Negotiation Agent (v2.0)

A multi-agent autonomous retail store powered by **FastAPI**, **WebSockets**, and **LiteLLM (Groq / Llama 3.3)**. Customers can discover products, negotiate prices, check inventory, and complete purchases — all through a real-time chat interface.

**🚀 What's New in Version 2.0:**
- **Premium Storefront Redesign:** A massive, full-width Apple-style dashboard with dark mode and glassmorphism.
- **Dynamic Hero Slideshow:** Auto-fading banner showcasing the top featured products.
- **Real-Time Live Search:** Grid instantly filters matching products as you type.
- **Advanced Negotiator AI:** The sales agent now employs real-world psychological pricing tactics like *Anchoring*, *Reasoned Offers*, and *Small Concessions*.
- **Floating AI Assistant:** Chat seamlessly via a sleek, non-intrusive floating widget rather than a split-screen panel.
- **Interactive UI:** Smooth Quick-View product modals and dynamic cart updates.

---

## ✨ Core Features

- **Multi-Agent Pipeline** — four specialised AI agents work in sequence:
  - 🔍 **Discovery Agent** — product search & recommendations
  - 💰 **Negotiator Agent** — dynamic discounts based on CRM loyalty data
  - 📦 **Inventory Agent** — real-time stock reservation
  - 🧾 **Order Agent** — address validation, payment & invoice generation
- **Real-time WebSocket chat** with streaming responses
- **MCP (Model Context Protocol)** mock servers for Catalog, CRM, Inventory, and Payments
- **FastAPI** REST + WebSocket backend with a static HTML/JS frontend
- **LiteLLM** abstraction layer (swap models by changing one line in `config.py`)

---

## 🗂️ Project Structure

```text
ADK_negotiation_agent/
├── app.py                  # FastAPI entry point (WebSocket + REST)
├── config.py               # LiteLLM / LLM configuration
├── workflow.py             # CLI workflow runner (non-web)
├── requirements.txt
├── .env.example
├── test_models.py          # Test models
├── Dockerfile              # Dockerfile for building the image
├── docker-compose.yml      # Docker-compose file for running the application
│
├── adk/
│   ├── __init__.py
│   ├── engine.py           # Agent base class (sync + async run)
│   └── mcp_client.py       # Tool schema builder & executor
│
├── agents/
│   ├── discovery_agent.py
│   ├── negotiator_agent.py
│   ├── inventory_agent.py
│   └── order_agent.py
│
├── mcp_servers/
│   ├── catalog_server.py
│   ├── crm_server.py
│   ├── inventory_server.py
│   └── payment_server.py
│
└── static/
    ├── index.html
    ├── style.css
    └── js/
```

---

## 🚀 Quick Start (Local)

### Prerequisites
- Python 3.11+
- A free [Groq API key](https://console.groq.com/)

### Setup

```bash
# 1. Clone the repo
git clone https://github.com/wasxy47/ADK_Negotiating_Agent.git
cd ADK_Negotiating_Agent

# 2. Create & activate virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
copy .env.example .env  # Or simply rename the file and fill it out
# Edit .env and add your GROQ_API_KEY

# 5. Run the server
python app.py
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

---

## 🐳 Docker

### Build & Run (single container)

```bash
# Using docker-compose (recommended)
docker-compose up --build

# Or directly with Docker
docker build -t adk-negotiation-agent .
docker run -p 8000:8000 --env-file .env adk-negotiation-agent
```

> **Note:** Make sure your `.env` file has `GROQ_API_KEY` set before running Docker.

App will be available at [http://localhost:8000](http://localhost:8000).

### Stop

```bash
docker-compose down
```

---

## ⚙️ Configuration

| Variable | Description | Required |
|---|---|---|
| `GROQ_API_KEY` | API key from [console.groq.com](https://console.groq.com/) | ✅ Yes |

To switch LLM models, edit `DEFAULT_MODEL` in `config.py`:
```python
DEFAULT_MODEL = "groq/llama-3.3-70b-versatile"  # Default
# DEFAULT_MODEL = "groq/mixtral-8x7b-32768"     # Alternative
```

---

## 🧪 Testing Checkout (Mock Data)

- **Payment Method:** Cash, Credit, or Bank Transfer
- **Test user:** `user_456` (Bronze tier, first-time buyer — 5% max discount)

---

## 🤝 Contributors

This v2.0 update and storefront redesign was brought to life by:
- **Abdul Wasay** ([@wasxy47](https://github.com/wasxy47))
- **Hassan** ([@hassanzzzj](https://github.com/hassanzzzj))

---

## 📄 License

MIT
