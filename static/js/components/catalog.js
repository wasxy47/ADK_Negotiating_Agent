import { state } from '../state-manager.js';
import { wsClient } from '../ws-client.js';

let allProducts = [];

export async function initCatalog() {
    await fetchCatalog();

    // Listen to price updates to reactively update the UI
    state.subscribe('priceUpdated', (priceData) => {
        const card = document.querySelector(`.product-card[data-id="${priceData.product_id}"]`);
        if (card) {
            const priceEl = card.querySelector('.product-price');
            card.classList.add('flash-update');
            setTimeout(() => card.classList.remove('flash-update'), 1000);

            const oldPrice = parseFloat(card.dataset.price);
            const newPrice = priceData.new_price;

            priceEl.innerHTML = `
                <span style="text-decoration: line-through; color: #ef4444; font-size: 0.8em; margin-right: 8px;">Rs. ${oldPrice.toLocaleString()}</span>
                Rs. ${newPrice.toLocaleString()} <span>PKR</span>
                <div style="font-size: 0.7em; color: #10b981; margin-top: 4px;">Discount Applied!</div>
            `;
        }
    });

    // Fullscreen toggle removed in favor of full-width dashboard

    // Global Search Logic
    const searchInput = document.getElementById('storeSearch');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            const filtered = allProducts.filter(p =>
                p.name.toLowerCase().includes(query) ||
                p.category.toLowerCase().includes(query) ||
                p.description.toLowerCase().includes(query)
            );

            // Re-render the grid (and optionally category active states can be reset if desired, but we'll leave them as is or reset to 'All')
            document.querySelectorAll('#categoryFilters button').forEach(b => b.classList.remove('active'));
            const allBtn = Array.from(document.querySelectorAll('#categoryFilters button')).find(b => b.textContent === 'All');
            if (allBtn) allBtn.classList.add('active');

            renderCatalog(filtered);
        });
    }

    // Modal Close
    document.getElementById('closeModalBtn').addEventListener('click', closeModal);
    document.getElementById('productModal').addEventListener('click', (e) => {
        if (e.target.id === 'productModal') closeModal();
    });
}

async function fetchCatalog() {
    try {
        const res = await fetch("/api/catalog");
        const data = await res.json();

        // API returns { products: [...] } — an array, use it directly
        allProducts = Array.isArray(data.products)
            ? data.products
            : Object.values(data.products);

        renderCategoryPills();
        renderCatalog(allProducts);
        initHeroSlideshow(allProducts);
    } catch (e) {
        console.error("Failed to fetch catalog:", e);
    }
}

function renderCategoryPills() {
    const container = document.getElementById('categoryFilters');
    container.innerHTML = '';

    // Extract unique categories
    const categories = ['All', ...new Set(allProducts.map(p => p.category))];

    categories.forEach(cat => {
        const btn = document.createElement('button');
        btn.textContent = cat;
        if (cat === 'All') btn.classList.add('active');

        btn.addEventListener('click', (e) => {
            // Update active state
            container.querySelectorAll('button').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Filter products
            if (cat === 'All') {
                renderCatalog(allProducts);
            } else {
                renderCatalog(allProducts.filter(p => p.category === cat));
            }
        });
        container.appendChild(btn);
    });
}

function renderCatalog(products) {
    const grid = document.getElementById("productGrid");
    grid.innerHTML = "";

    products.forEach(p => {
        const price = parseFloat(p.price);
        const stockStatus = p.stock > 0 ? `<span style="color: #10b981; font-weight: 500;">In Stock (${p.stock})</span>` : `<span style="color: #ef4444; font-weight: 500;">Out of Stock</span>`;

        const card = document.createElement("div");
        card.className = "product-card";
        card.dataset.id = p.id;
        card.dataset.price = price;
        card.style.cursor = "pointer";
        card.innerHTML = `
            <div>
                <img src="${p.image_url}" alt="${p.name}" style="width: 100%; height: 160px; object-fit: cover; border-radius: 8px; margin-bottom: 12px; background: #e5e7eb;" />
                <div class="product-category" style="display: flex; justify-content: space-between;">
                    <span>${p.category}</span>
                    <span>${stockStatus}</span>
                </div>
                <div class="product-title">${p.name}</div>
                <div class="product-desc">${p.description}</div>
            </div>
            <div class="product-price" style="margin-top: auto;">
                Rs. ${price.toLocaleString()} <span>PKR</span>
            </div>
        `;

        card.addEventListener('click', () => openModal(p));
        grid.appendChild(card);
    });
}

function openModal(product) {
    const modal = document.getElementById('productModal');
    const modalBody = document.getElementById('modalBody');
    const price = parseFloat(product.price);

    // Generate feature list
    const featureListHTML = product.key_features
        ? `<ul style="margin-left: 1.5rem; margin-top: 1rem; color: var(--text-secondary); line-height: 1.6;">
            ${product.key_features.map(f => `<li>${f}</li>`).join('')}
           </ul>`
        : '';

    modalBody.innerHTML = `
        <div style="display: flex; gap: 2rem; align-items: flex-start;">
            <img src="${product.image_url}" style="width: 50%; max-height: 400px; object-fit: cover; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1);" />
            <div style="flex: 1;">
                <div class="product-category" style="margin-bottom: 0.25rem;">${product.category}</div>
                <h1 style="font-size: 2rem; margin-bottom: 1rem; background: none; -webkit-text-fill-color: initial; color: white;">${product.name}</h1>
                <div class="product-price" style="font-size: 2rem; margin-bottom: 1rem;">
                    Rs. ${price.toLocaleString()} <span style="font-size: 1rem; margin-left: 8px;">PKR</span>
                </div>
                <p style="font-size: 1.1rem; margin-bottom: 1rem; color: #e2e8f0;">${product.description}</p>
                <div style="margin-top: 1.5rem;">
                    <h3 style="color: white; font-family: 'Outfit', sans-serif;">Key Specifications</h3>
                    ${featureListHTML}
                </div>
                <div style="margin-top: 1.5rem; font-weight: 500; color: ${product.stock > 0 ? '#10b981' : '#ef4444'};">
                    ${product.stock > 0 ? `Currently ${product.stock} units available` : 'Currently unavailable'}
                </div>
            </div>
        </div>
    `;

    // Ensure buttons are clean before adding listeners
    const buyBtn = document.getElementById('modalBuyBtn');
    const negBtn = document.getElementById('modalNegotiateBtn');

    // Replace nodes to clear old listeners
    const newBuyBtn = buyBtn.cloneNode(true);
    const newNegBtn = negBtn.cloneNode(true);
    buyBtn.parentNode.replaceChild(newBuyBtn, buyBtn);
    negBtn.parentNode.replaceChild(newNegBtn, negBtn);

    // Disable if out of stock
    if (product.stock === 0) {
        newBuyBtn.disabled = true;
        newNegBtn.disabled = true;
        newBuyBtn.style.opacity = '0.5';
        newNegBtn.style.opacity = '0.5';
        newBuyBtn.style.cursor = 'not-allowed';
        newNegBtn.style.cursor = 'not-allowed';
    } else {
        newBuyBtn.addEventListener('click', () => {
            closeModal();
            if (window.openAIWidget) window.openAIWidget();

            // Immediately populate the cart widget at full MRP price
            import('../state-manager.js').then(({ state }) => {
                state.updateCart({
                    items: [{
                        id: product.id,
                        name: product.name,
                        qty: 1,
                        agreed_price: product.price,
                        original_price: product.mrp || product.price,
                        savings: product.mrp ? Math.max(0, product.mrp - product.price) : 0
                    }],
                    total: product.price,
                    status: 'reserved'
                });
            });

            // Send a very explicit buy-intent message so Discovery → OrderTaking immediately
            wsClient.sendMessage(
                `I want to buy the ${product.name} (product ID: ${product.id}) right now ` +
                `at the listed price of Rs. ${product.price}. Please proceed to checkout.`
            );
        });

        newNegBtn.addEventListener('click', () => {
            closeModal();
            if (window.openAIWidget) window.openAIWidget();
            // Trigger negotiation flow
            wsClient.sendMessage(
                `I am interested in the ${product.name} (product ID: ${product.id}). ` +
                `The listed price is Rs. ${product.price}. Is there any flexibility on the price?`
            );
        });
    }

    modal.classList.add('active');
}

function closeModal() {
    document.getElementById('productModal').classList.remove('active');
}

// Hero Slideshow Logic
let currentSlide = 0;
let slideInterval;

function initHeroSlideshow(products) {
    const slideshowContainer = document.getElementById('heroSlideshow');
    if (!slideshowContainer) return;

    // Pick top 3 featured products (or completely random)
    const featuredProducts = products.filter(p => p.price > 100000).slice(0, 3);
    if (featuredProducts.length === 0 && products.length > 0) {
        featuredProducts.push(...products.slice(0, 3));
    }

    if (featuredProducts.length === 0) return;

    slideshowContainer.innerHTML = '';

    featuredProducts.forEach((p, index) => {
        const slide = document.createElement('div');
        slide.className = `hero-slide ${index === 0 ? 'active' : ''}`;
        slide.style.background = `linear-gradient(to right, rgba(15, 23, 42, 0.95), rgba(15, 23, 42, 0.4)), url('${p.image_url}') center/cover`;
        slide.dataset.index = index;

        slide.innerHTML = `
            <div style="position: relative; z-index: 2; max-width: 600px; padding: 4rem;">
                <div style="display: inline-block; padding: 0.25rem 0.75rem; background: rgba(139, 92, 246, 0.2); border: 1px solid rgba(139, 92, 246, 0.5); color: #c084fc; border-radius: 99px; font-size: 0.8rem; font-weight: 600; margin-bottom: 1rem; text-transform: uppercase;">Featured</div>
                <h2 style="font-size: 3rem; margin-bottom: 1rem; color: #fff; line-height: 1.1;">${p.name}</h2>
                <p style="font-size: 1.1rem; color: #cbd5e1; margin-bottom: 2rem; line-height: 1.6;">${p.description}</p>
                <div style="display: flex; gap: 1rem; align-items: center;">
                    <button class="btn-gradient"
                        style="padding: 1rem 2rem; border-radius: 99px; border: none; background: linear-gradient(135deg, #8b5cf6, #ec4899); color: white; font-weight: 600; font-size: 1.1rem; cursor: pointer; transition: 0.2s;"
                        onclick="document.querySelector('.product-card[data-id=\\'${p.id}\\']').click()">View Offer</button>
                    <span style="font-family: 'Outfit', sans-serif; font-size: 1.5rem; font-weight: 600; color: #38bdf8;">Rs. ${parseFloat(p.price).toLocaleString()}</span>
                </div>
            </div>
        `;
        slideshowContainer.appendChild(slide);
    });

    // Generate Dots
    const dotsContainer = document.createElement('div');
    dotsContainer.style.position = 'absolute';
    dotsContainer.style.bottom = '1.5rem';
    dotsContainer.style.left = '50%';
    dotsContainer.style.transform = 'translateX(-50%)';
    dotsContainer.style.display = 'flex';
    dotsContainer.style.gap = '0.5rem';
    dotsContainer.style.zIndex = '10';

    featuredProducts.forEach((_, index) => {
        const dot = document.createElement('div');
        dot.className = `slide-dot ${index === 0 ? 'active' : ''}`;
        dot.style.width = '12px';
        dot.style.height = '12px';
        dot.style.borderRadius = '50%';
        dot.style.background = index === 0 ? '#8b5cf6' : 'rgba(255,255,255,0.3)';
        dot.style.cursor = 'pointer';
        dot.style.transition = '0.3s';
        dot.addEventListener('click', () => goToSlide(index));
        dotsContainer.appendChild(dot);
    });
    slideshowContainer.appendChild(dotsContainer);

    // Start auto-advance
    currentSlide = 0;
    if (slideInterval) clearInterval(slideInterval);
    slideInterval = setInterval(nextSlide, 5000);
}

function nextSlide() {
    const slides = document.querySelectorAll('.hero-slide');
    if (slides.length <= 1) return;
    goToSlide((currentSlide + 1) % slides.length);
}

function goToSlide(index) {
    const slides = document.querySelectorAll('.hero-slide');
    const dots = document.querySelectorAll('.slide-dot');

    slides.forEach((sl, i) => {
        sl.classList.toggle('active', i === index);
    });
    dots.forEach((dot, i) => {
        dot.style.background = i === index ? '#8b5cf6' : 'rgba(255,255,255,0.3)';
    });

    currentSlide = index;

    clearInterval(slideInterval);
    slideInterval = setInterval(nextSlide, 5000);
}
