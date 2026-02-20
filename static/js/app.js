import { wsClient } from './ws-client.js';
import { initChat } from './components/chat.js';
import { initCatalog } from './components/catalog.js';
import { initCart } from './components/cart.js';

document.addEventListener("DOMContentLoaded", () => {
    // Initialize components
    initChat();
    initCatalog();
    initCart();

    // Connect WebSocket
    wsClient.connect();
});
