import { state } from './state-manager.js';

class WSClient {
    constructor() {
        this.ws = null;
        this.eventHandlers = {};
    }

    connect() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const url = `${protocol}//${window.location.host}/ws/chat/${state.sessionId}`;

        this.ws = new WebSocket(url);

        this.ws.onopen = () => {
            console.log('Connected to ADK Multi-Agent Backend');
            this.trigger('connected', null);
        };

        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.routeEvent(data);
            } catch (e) {
                console.error("Error parsing WS message", e);
            }
        };

        this.ws.onclose = () => {
            console.log('Disconnected. Reconnecting in 3s...');
            setTimeout(() => this.connect(), 3000);
        };
    }

    routeEvent(data) {
        const { type, payload, agent } = data;

        switch (type) {
            case 'sync_state':
                state.hydrate(payload);
                this.trigger('sync_state', payload);
                break;
            case 'chat_stream':
                this.trigger('chat_stream', { text: payload, agent });
                break;
            case 'agent_transition':
                state.setAgent(payload.to);
                this.trigger('agent_transition', payload);
                break;
            case 'price_update':
                state.updatePrice(payload);
                break;
            case 'cart_update':
                state.updateCart(payload);
                break;
            case 'tool_call':
                this.trigger('tool_call', payload);
                break;
            case 'reset_ui':
                this.trigger('reset_ui', payload);
                break;
            default:
                console.warn('Unknown event type:', type);
        }
    }

    on(event, callback) {
        if (!this.eventHandlers[event]) this.eventHandlers[event] = [];
        this.eventHandlers[event].push(callback);
    }

    trigger(event, data) {
        if (this.eventHandlers[event]) {
            this.eventHandlers[event].forEach(cb => cb(data));
        }
    }

    sendMessage(text) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({ message: text }));
            return true;
        }
        return false;
    }
}

export const wsClient = new WSClient();
