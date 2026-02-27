import { state } from '../state-manager.js';
import { wsClient } from '../ws-client.js';

export function initChat() {
    const form = document.getElementById("chatForm");
    const input = document.getElementById("userInput");
    const history = document.getElementById("chatHistory");
    const agentStatus = document.getElementById("agentStatus");
    const resetBtn = document.getElementById("resetSessionBtn");
    const micBtn = document.getElementById("micBtn");

    // Floating Widget Elements
    const aiWidgetToggle = document.getElementById("aiWidgetToggle");
    const closeChatBtn = document.getElementById("closeChatBtn");
    const floatingChatPanel = document.getElementById("floatingChatPanel");
    const aiWidgetBadge = document.getElementById("aiWidgetBadge");

    let currentBotMessageDiv = null;
    let isChatOpen = false;

    // Toggle logic
    function toggleChat(forceState) {
        if (typeof forceState === "boolean") {
            isChatOpen = forceState;
        } else {
            isChatOpen = !isChatOpen;
        }

        if (isChatOpen) {
            floatingChatPanel.style.opacity = '1';
            floatingChatPanel.style.visibility = 'visible';
            floatingChatPanel.style.transform = 'translateY(0)';
            aiWidgetBadge.style.display = 'none';
            scrollToBottom();
            setTimeout(() => input.focus(), 300);
        } else {
            floatingChatPanel.style.opacity = '0';
            floatingChatPanel.style.visibility = 'hidden';
            floatingChatPanel.style.transform = 'translateY(20px)';
        }
    }

    aiWidgetToggle.addEventListener("click", () => toggleChat());
    closeChatBtn.addEventListener("click", () => toggleChat(false));

    const expandChatBtn = document.getElementById("expandChatBtn");
    let isChatExpanded = false;
    expandChatBtn.addEventListener("click", () => {
        isChatExpanded = !isChatExpanded;
        if (isChatExpanded) {
            floatingChatPanel.classList.add("expanded-chat");
            expandChatBtn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="4 14 10 14 10 20"></polyline><polyline points="20 10 14 10 14 4"></polyline><line x1="14" y1="10" x2="21" y2="3"></line><line x1="3" y1="21" x2="10" y2="14"></line></svg>';
            expandChatBtn.title = "Shrink";
        } else {
            floatingChatPanel.classList.remove("expanded-chat");
            expandChatBtn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 3 21 3 21 9"></polyline><polyline points="9 21 3 21 3 15"></polyline><line x1="21" y1="3" x2="14" y2="10"></line><line x1="3" y1="21" x2="10" y2="14"></line></svg>';
            expandChatBtn.title = "Expand";
        }
        scrollToBottom();
    });

    // Expose openChat globally so catalog buttons can trigger it
    window.openAIWidget = function () {
        toggleChat(true);
    };

    // Send Message
    form.addEventListener("submit", (e) => {
        e.preventDefault();
        const message = input.value.trim();
        if (!message) return;

        appendMessage(message, "user");
        input.value = "";

        // Reset the tracker so the next bot response starts a fresh bubble
        currentBotMessageDiv = null;

        const sent = wsClient.sendMessage(message);
        if (!sent) {
            appendMessage("Connection offline. Please wait...", "system");
        } else {
            showTypingIndicator();
        }
    });

    // Voice Input Feature
    if ('webkitSpeechRecognition' in window) {
        const recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        micBtn.addEventListener("click", () => {
            micBtn.style.color = "#ef4444"; // Red to show recording
            recognition.start();
        });

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            input.value = transcript;
            micBtn.style.color = "#aaa";
            form.dispatchEvent(new Event('submit'));
        };

        recognition.onerror = (event) => {
            console.error(event);
            micBtn.style.color = "#aaa";
        };

        recognition.onend = () => {
            micBtn.style.color = "#aaa";
        };
    } else {
        micBtn.style.display = "none";
    }

    // Reset Session
    resetBtn.addEventListener("click", () => {
        // Clear all UI state immediately
        history.innerHTML = '';
        currentBotMessageDiv = null;
        removeTypingIndicator();
        state.setAgent('Discovery');
        updateAgentColor('Discovery');

        // Show a clean welcome
        appendMessage(
            "Session reset! I'm Zara, your TechVault consultant. How can I help you today?",
            "assistant"
        );

        // Notify backend — it will reply with sync_state confirming the clean session
        wsClient.sendMessage("/reset_session");
    });

    // Listen for WebSockets
    wsClient.on('chat_stream', (data) => {
        removeTypingIndicator();

        let content = data.text;

        // If it's a system message
        if (content.startsWith('*[System:')) {
            appendMessage(content, 'system');
            currentBotMessageDiv = null; // force next message to be a new one
            return;
        }

        // Pop badge if panel is closed
        if (!isChatOpen) {
            aiWidgetBadge.style.display = 'block';
        }

        // Format markdown
        let htmlContent = marked.parse(content);

        if (!currentBotMessageDiv) {
            // Create a new bubble if there isn't one active for this turn
            currentBotMessageDiv = appendMessage(htmlContent, 'assistant', true);
        } else {
            // Append to existing bubble to prevent multi-popups
            currentBotMessageDiv.innerHTML += htmlContent;
            scrollToBottom();
        }
    });

    wsClient.on('agent_transition', (data) => {
        // System message removed
    });

    wsClient.on('tool_call', (data) => {
        if (data.status === 'running') {
            agentStatus.textContent = `Agent: ${state.currentAgent} (Thinking...)`;
            agentStatus.classList.add('pulse');
        } else if (data.status === 'success') {
            agentStatus.textContent = `Agent: ${state.currentAgent}`;
            agentStatus.classList.remove('pulse');
        }
    });

    wsClient.on('sync_state', (payload) => {
        // Clear history and hydrate
        history.innerHTML = '';
        currentBotMessageDiv = null;
        if (payload.messages && payload.messages.length > 0) {
            payload.messages.forEach(msg => {
                if (msg.role === 'user') {
                    appendMessage(msg.content, 'user');
                } else if (msg.role === 'assistant' && msg.content) {
                    // Only show cleaned text
                    let cleaned = msg.content.replace(/\{.*?\}/g, '').trim();
                    if (cleaned) {
                        appendMessage(marked.parse(cleaned), 'assistant', true);
                    }
                }
            });
        } else {
            appendMessage("Hello! Welcome to the Autonomous Retail Store. I'm your Product Discovery agent. How can I help you find the perfect product today?", "assistant");
        }
        updateAgentColor(state.currentAgent);
    });

    wsClient.on('reset_ui', () => {
        history.innerHTML = '<div class="message assistant-message">Transaction ended. Session has been automatically reset. Welcome back!</div>';
        currentBotMessageDiv = null;
        state.setAgent('Discovery');
    });

    state.subscribe('agentChanged', (agentName) => {
        updateAgentColor(agentName);
    });

    // ── Agent identity map ────────────────────────────────────────────────────
    const AGENT_IDENTITY = {
        Discovery: {
            avatar: '/static/avatar_zara.png',
            name: 'Zara',
            role: 'Product Consultant · Discovery',
            border: 'rgba(52,211,153,0.7)',
            glow: 'rgba(52,211,153,0.3)',
            dot: '#34d399',
            status: '#34d399',
        },
        Negotiator: {
            avatar: '/static/avatar_rayan.png',
            name: 'Rayan',
            role: 'Senior Negotiator · Deal Desk',
            border: 'rgba(245,158,11,0.7)',
            glow: 'rgba(245,158,11,0.3)',
            dot: '#f59e0b',
            status: '#f59e0b',
        },
        Inventory: {
            avatar: '/static/avatar_inventory.png',
            name: 'Inventory AI',
            role: 'Stock Verification System',
            border: 'rgba(139,92,246,0.7)',
            glow: 'rgba(139,92,246,0.3)',
            dot: '#8b5cf6',
            status: '#8b5cf6',
        },
        OrderTaking: {
            avatar: '/static/avatar_omar.png',
            name: 'Omar',
            role: 'Checkout Specialist · Orders',
            border: 'rgba(59,130,246,0.7)',
            glow: 'rgba(59,130,246,0.3)',
            dot: '#3b82f6',
            status: '#3b82f6',
        },
    };

    function updateAgentColor(agentName) {
        const identity = AGENT_IDENTITY[agentName] || AGENT_IDENTITY.Discovery;

        const avatarEl = document.getElementById('agentAvatar');
        const displayNameEl = document.getElementById('agentDisplayName');
        const liveDotEl = document.getElementById('agentLiveDot');

        // Animate swap: shrink → swap → pop
        if (avatarEl) {
            avatarEl.style.transform = 'scale(0.75)';
            avatarEl.style.opacity = '0';
            setTimeout(() => {
                avatarEl.src = identity.avatar;
                avatarEl.style.borderColor = identity.border;
                avatarEl.style.boxShadow = `0 0 18px ${identity.glow}`;
                avatarEl.style.transform = 'scale(1)';
                avatarEl.style.opacity = '1';
            }, 200);
        }
        if (displayNameEl) displayNameEl.textContent = identity.name;
        if (liveDotEl) liveDotEl.style.background = identity.dot;

        agentStatus.textContent = identity.role;
        agentStatus.style.color = identity.status;
    }


    function appendMessage(text, role, renderHTML = false) {
        const div = document.createElement("div");
        if (role === 'system') {
            div.className = "message system-message";
            div.textContent = text;
        } else if (role === 'user') {
            div.className = "message user-message";
            div.textContent = text;
        } else {
            div.className = "message assistant-message";
            if (renderHTML) div.innerHTML = text;
            else div.textContent = text;
        }
        history.appendChild(div);
        scrollToBottom();
        return div;
    }

    function showTypingIndicator() {
        const id = "loading_" + Date.now();
        const div = document.createElement("div");
        div.id = id;
        div.className = "loading-dots active-typing";
        div.innerHTML = `<div class="dot"></div><div class="dot"></div><div class="dot"></div>`;
        history.appendChild(div);
        scrollToBottom();
    }

    function removeTypingIndicator() {
        const els = document.querySelectorAll('.active-typing');
        els.forEach(el => el.remove());
    }

    function scrollToBottom() {
        history.scrollTop = history.scrollHeight;
    }
}
