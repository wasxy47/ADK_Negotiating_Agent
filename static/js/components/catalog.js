import { state } from '../state-manager.js';
import { wsClient } from '../ws-client.js';

export async function initCatalog() {
    await fetchCatalog();

    // Listen to price updates to reactively update the UI
    state.subscribe('priceUpdated', (priceData) => {
        const card = document.querySelector(`.product-card[data-id="${priceData.product_id}"]`);
        if (card) {
            const priceEl = card.querySelector('.product-price');
            // Animate
            card.classList.add('flash-update');
            setTimeout(() => card.classList.remove('flash-update'), 1000);

            // Update DOM with strikethrough logic
            const oldPrice = parseFloat(card.dataset.price);
            const newPrice = priceData.new_price;

            priceEl.innerHTML = `
                <span style="text-decoration: line-through; color: #ef4444; font-size: 0.8em; margin-right: 8px;">Rs. ${oldPrice.toLocaleString()}</span>
                Rs. ${newPrice.toLocaleString()} <span>PKR</span>
                <div style="font-size: 0.7em; color: #10b981; margin-top: 4px;">Discount Applied!</div>
            `;
        }
    });

}

async function fetchCatalog() {
    try {
        const res = await fetch("/api/catalog");
        const data = await res.json();
        const grid = document.getElementById("productGrid");
        grid.innerHTML = "";

        Object.keys(data.products).forEach(pid => {
            const p = data.products[pid];
            const pId = p.id || pid;
            const price = parseFloat(p.price);

            const card = document.createElement("div");
            card.className = "product-card";
            card.dataset.id = pId;
            card.dataset.price = price;
            card.innerHTML = `
                <div>
                    <div class="product-category">${p.category}</div>
                    <div class="product-title">${p.name}</div>
                    <div class="product-desc">${p.description}</div>
                </div>
                <div class="product-price">
                    Rs. ${price.toLocaleString()} <span>PKR</span>
                </div>
            `;
            grid.appendChild(card);
        });
    } catch (e) {
        console.error("Failed to fetch catalog:", e);
    }
}
