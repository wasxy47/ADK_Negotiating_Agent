import { state } from '../state-manager.js';

export function initCart() {
    const cartContainer = document.getElementById("cartContainer");

    state.subscribe('cartUpdated', (cartData) => {
        if (!cartData.items || cartData.items.length === 0) {
            cartContainer.style.display = 'none';
            return;
        }

        cartContainer.style.display = 'block';
        cartContainer.innerHTML = `
            <div class="cart-header">Current Cart - Total: Rs. ${cartData.total.toLocaleString()}</div>
            <div class="cart-items">
                ${cartData.items.map(item => `
                    <div class="cart-item">
                        <span>Item: ${item.id}</span>
                        <span>Qty: ${item.qty}</span>
                    </div>
                `).join('')}
            </div>
            <div class="cart-status">Status: ${cartData.status}</div>
        `;

        // Flash animation
        cartContainer.classList.add('flash-update');
        setTimeout(() => cartContainer.classList.remove('flash-update'), 1000);
    });
}
