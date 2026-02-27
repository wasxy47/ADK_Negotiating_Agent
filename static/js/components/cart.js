import { state } from '../state-manager.js';

// ── Toast Notification ──────────────────────────────────────────────────────
function showToast(message, type = 'success') {
    let container = document.getElementById('toastContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toastContainer';
        container.style.cssText = `
            position:fixed; top:1.5rem; left:50%; transform:translateX(-50%);
            z-index:9999; display:flex; flex-direction:column;
            align-items:center; gap:0.6rem; pointer-events:none;
        `;
        document.body.appendChild(container);
    }
    const colors = {
        success: 'linear-gradient(135deg,#059669,#10b981)',
        deal: 'linear-gradient(135deg,#7c3aed,#db2777)',
        info: 'linear-gradient(135deg,#1d4ed8,#3b82f6)',
    };
    const icons = {
        success: '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>',
        deal: '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>',
        info: '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>',
    };
    const toast = document.createElement('div');
    toast.style.cssText = `
        background:${colors[type] || colors.success}; color:white;
        padding:0.85rem 1.5rem; border-radius:100px;
        font-family:'Inter',sans-serif; font-size:0.9rem; font-weight:600;
        box-shadow:0 8px 30px rgba(0,0,0,0.4);
        transform:translateY(-16px) scale(0.9); opacity:0;
        transition:all 0.35s cubic-bezier(0.175,0.885,0.32,1.275);
        pointer-events:none; white-space:nowrap;
        display:flex; align-items:center; gap:0.6rem;
    `;
    toast.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">${icons[type] || icons.success}</svg>
        <span>${message}</span>
    `;
    container.appendChild(toast);
    requestAnimationFrame(() => requestAnimationFrame(() => {
        toast.style.transform = 'translateY(0) scale(1)';
        toast.style.opacity = '1';
    }));
    setTimeout(() => {
        toast.style.transform = 'translateY(-8px) scale(0.95)';
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 350);
    }, 3800);
}

// ── Drawer helpers ──────────────────────────────────────────────────────────
function openDrawer() {
    const overlay = document.getElementById('cartOverlay');
    const drawer = document.getElementById('cartDrawer');
    overlay.style.display = 'block';
    requestAnimationFrame(() => {
        overlay.style.opacity = '1';
        drawer.style.transform = 'translateX(0)';
    });
}

function closeDrawer() {
    const overlay = document.getElementById('cartOverlay');
    const drawer = document.getElementById('cartDrawer');
    overlay.style.opacity = '0';
    drawer.style.transform = 'translateX(100%)';
    setTimeout(() => { overlay.style.display = 'none'; }, 400);
}

// ── Cart scrollbar style injection ─────────────────────────────────────────
const style = document.createElement('style');
style.textContent = `
    #cartItemsList::-webkit-scrollbar { width: 5px; }
    #cartItemsList::-webkit-scrollbar-track { background: transparent; }
    #cartItemsList::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 10px; }
    #cartCheckoutBtn:hover { transform: translateY(-2px); box-shadow: 0 8px 28px rgba(59,130,246,0.5) !important; }
    #cartCheckoutBtn:active { transform: translateY(0); }
    .cart-line-item { animation: slideInItem 0.3s ease forwards; opacity: 0; }
    @keyframes slideInItem {
        from { opacity:0; transform: translateX(20px); }
        to   { opacity:1; transform: translateX(0); }
    }
`;
document.head.appendChild(style);

// ── Main ───────────────────────────────────────────────────────────────────
export function initCart() {
    const viewCartBtn = document.getElementById('viewCartBtn');
    const cartCountBadge = document.getElementById('cartCountBadge');
    const closeBtn = document.getElementById('closeCartDrawer');
    const overlay = document.getElementById('cartOverlay');
    const checkoutBtn = document.getElementById('cartCheckoutBtn');

    // Open on cart icon click
    viewCartBtn?.addEventListener('click', openDrawer);
    // Close handlers
    closeBtn?.addEventListener('click', closeDrawer);
    overlay?.addEventListener('click', closeDrawer);
    // Checkout button → open chat
    checkoutBtn?.addEventListener('click', () => {
        closeDrawer();
        if (window.openAIWidget) window.openAIWidget();
    });

    // ── React to state updates ────────────────────────────────────────────
    state.subscribe('cartUpdated', (cartData) => {
        const emptyState = document.getElementById('cartEmptyState');
        const itemsList = document.getElementById('cartItemsList');
        const footer = document.getElementById('cartFooter');
        const itemCount = document.getElementById('cartItemCount');
        const totalAmount = document.getElementById('cartTotalAmount');
        const statusPill = document.getElementById('cartStatusPill');
        const savBanner = document.getElementById('cartSavingsBanner');
        const savAmount = document.getElementById('cartTotalSavings');

        const hasItems = cartData.items && cartData.items.length > 0;
        const totalQty = hasItems ? cartData.items.reduce((s, i) => s + (i.qty || 1), 0) : 0;

        // Badge
        cartCountBadge.textContent = totalQty;
        cartCountBadge.style.background = hasItems ? '#10b981' : '#ef4444';

        if (!hasItems) {
            emptyState.style.display = 'flex';
            itemsList.style.display = 'none';
            footer.style.display = 'none';
            return;
        }

        // ── Render items ──────────────────────────────────────────────────
        emptyState.style.display = 'none';
        itemsList.style.display = 'flex';
        footer.style.display = 'flex';
        itemCount.textContent = `${totalQty} item${totalQty !== 1 ? 's' : ''}`;
        totalAmount.textContent = `Rs. ${cartData.total.toLocaleString('en-IN')}`;

        itemsList.innerHTML = cartData.items.map((item, idx) => {
            const hasDiscount = item.original_price && item.agreed_price &&
                item.original_price > item.agreed_price;
            const savings = item.savings ?? Math.max(0, (item.original_price || 0) - (item.agreed_price || 0));
            const price = item.agreed_price ?? item.original_price ?? 0;
            const origPrice = item.original_price ?? price;
            const discPct = hasDiscount ? Math.round((savings / origPrice) * 100) : 0;

            return `
            <div class="cart-line-item" style="
                background: rgba(255,255,255,0.03);
                border: 1px solid rgba(255,255,255,0.07);
                border-radius: 14px; padding: 1rem 1.1rem;
                display: flex; gap: 0.9rem; align-items: flex-start;
                animation-delay: ${idx * 60}ms;
            ">
                <!-- Icon -->
                <div style="
                    width: 48px; height: 48px; border-radius: 10px; flex-shrink: 0;
                    background: linear-gradient(135deg, #1e3a8a, #5b21b6);
                    display: flex; align-items: center; justify-content: center;
                ">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,0.8)" stroke-width="1.8">
                        <rect x="2" y="3" width="20" height="14" rx="2"/>
                        <line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/>
                    </svg>
                </div>

                <!-- Info -->
                <div style="flex:1; min-width:0;">
                    <div style="font-weight:600; color:#f1f5f9; font-size:0.9rem;
                        white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
                        ${item.name || item.id}
                    </div>
                    <div style="color:#64748b; font-size:0.75rem; margin-top:2px;">
                        Qty: ${item.qty || 1}
                    </div>

                    ${hasDiscount ? `
                    <div style="display:flex; align-items:center; gap:0.4rem; margin-top:0.5rem;">
                        <span style="
                            background:rgba(16,185,129,0.15); border:1px solid rgba(16,185,129,0.3);
                            color:#10b981; border-radius:99px; padding:2px 8px;
                            font-size:0.68rem; font-weight:700; letter-spacing:0.03em;
                        ">${discPct}% OFF</span>
                        <span style="color:#64748b; font-size:0.72rem;">
                            You saved Rs. ${savings.toLocaleString('en-IN')}
                        </span>
                    </div>` : ''}
                </div>

                <!-- Price -->
                <div style="text-align:right; flex-shrink:0;">
                    ${hasDiscount ? `
                    <div style="color:#475569; font-size:0.72rem; text-decoration:line-through; margin-bottom:1px;">
                        Rs. ${origPrice.toLocaleString('en-IN')}
                    </div>` : ''}
                    <div style="
                        font-size:1rem; font-weight:700; font-family:'Outfit',sans-serif;
                        background:${hasDiscount
                    ? 'linear-gradient(135deg,#34d399,#10b981)'
                    : 'linear-gradient(135deg,#60a5fa,#818cf8)'};
                        -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                        background-clip:text;
                    ">
                        Rs. ${price.toLocaleString('en-IN')}
                    </div>
                    ${hasDiscount ? `
                    <div style="font-size:0.65rem; color:#10b981; margin-top:2px; font-weight:600;">
                        Negotiated ✓
                    </div>` : `
                    <div style="font-size:0.65rem; color:#6366f1; margin-top:2px; font-weight:600;">
                        Full Price
                    </div>`}
                </div>
            </div>`;
        }).join('');

        // ── Footer: savings banner ────────────────────────────────────────
        const totalSavings = cartData.items.reduce((s, i) => s + (i.savings || 0), 0);
        if (totalSavings > 0) {
            savBanner.style.display = 'flex';
            savAmount.textContent = `Rs. ${totalSavings.toLocaleString('en-IN')}`;
        } else {
            savBanner.style.display = 'none';
        }

        // ── Footer: status pill ───────────────────────────────────────────
        const statusMap = {
            reserved: { bg: 'rgba(16,185,129,0.12)', border: 'rgba(16,185,129,0.3)', color: '#10b981', label: '✓ Reservation Confirmed' },
            pending_inventory: { bg: 'rgba(245,158,11,0.12)', border: 'rgba(245,158,11,0.3)', color: '#f59e0b', label: '⏳ Checking Inventory...' },
            pending_checkout: { bg: 'rgba(59,130,246,0.12)', border: 'rgba(59,130,246,0.3)', color: '#60a5fa', label: '💳 Ready for Checkout' },
        };
        const sc = statusMap[cartData.status] || statusMap['pending_checkout'];
        statusPill.style.cssText = `text-align:center; padding:0.6rem; border-radius:8px;
            font-size:0.8rem; font-weight:600;
            background:${sc.bg}; border:1px solid ${sc.border}; color:${sc.color};`;
        statusPill.textContent = sc.label;

        // ── Toast notification ────────────────────────────────────────────
        if (cartData.status === 'reserved' && cartData.items.length > 0) {
            const item = cartData.items[0];
            const sav = item.savings || 0;
            showToast(
                sav > 0
                    ? `🎉 Deal locked — saved Rs. ${sav.toLocaleString('en-IN')}!`
                    : `🛒 ${item.name || 'Item'} added to cart`,
                sav > 0 ? 'deal' : 'success'
            );
            // Auto-open the drawer so user sees it immediately
            openDrawer();
        }
    });
}
