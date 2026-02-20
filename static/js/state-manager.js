class StateManager {
    constructor() {
        this.sessionId = this.getOrSetSessionId();
        this.cart = { items: [], total: 0, status: "empty" };
        this.priceOverrides = {}; // product_id -> new_price
        this.currentAgent = "Discovery";
        this.listeners = {};
    }

    getOrSetSessionId() {
        let id = localStorage.getItem('adk_session_id');
        if (!id) {
            id = "session_" + Math.random().toString(36).substring(2, 9);
            localStorage.setItem('adk_session_id', id);
        }
        return id;
    }

    subscribe(event, callback) {
        if (!this.listeners[event]) this.listeners[event] = [];
        this.listeners[event].push(callback);
    }

    notify(event, data) {
        if (this.listeners[event]) {
            this.listeners[event].forEach(cb => cb(data));
        }
    }

    updateCart(cartData) {
        this.cart = cartData;
        this.notify('cartUpdated', this.cart);
    }

    updatePrice(priceData) {
        this.priceOverrides[priceData.product_id] = priceData.new_price;
        this.notify('priceUpdated', priceData);
    }

    setAgent(agentName) {
        this.currentAgent = agentName;
        this.notify('agentChanged', this.currentAgent);
    }

    hydrate(syncData) {
        // Hydrate from backend on page load
        if (syncData.current_agent) {
            this.setAgent(syncData.current_agent);
        }
        // Additional hydration if needed (e.g. cart from shared_context)
    }
}

export const state = new StateManager();
