import { state } from '../state-manager.js';
import { wsClient } from '../ws-client.js';

export function initChat() {
    const form = document.getElementById("chatForm");
    const input = document.getElementById("userInput");
    const history = document.getElementById("chatHistory");
    const agentStatus = document.getElementById("agentStatus");

    // Send Message
    form.addEventListener("submit", (e) => {
        e.preventDefault();
        const message = input.value.trim();
        if (!message) return;

        appendMessage(message, "user");
        input.value = "";

        const sent = wsClient.sendMessage(message);
        if (!sent) {
            appendMessage("Connection offline. Please wait...", "system");
        } else {
            showTypingIndicator();
        }
    });

    // Listen for WebSockets
    wsClient.on('chat_stream', (data) => {
        removeTypingIndicator();
        const lines = data.text.split('\n\n');
        lines.forEach(line => {
            if (line.startsWith('*[System:')) {
                appendMessage(line, 'system');
            } else {
                let formatted = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
                formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
                appendMessage(formatted, 'assistant', true);
            }
        });
    });

    wsClient.on('agent_transition', (data) => {
        appendMessage(`*[System: Transferring you to ${data.to} agent... Reason: ${data.reason}]*`, 'system');
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
        if (payload.messages && payload.messages.length > 0) {
            payload.messages.forEach(msg => {
                if (msg.role === 'user') {
                    appendMessage(msg.content, 'user');
                } else if (msg.role === 'assistant' && msg.content) {
                    // Only show cleaned text
                    let cleaned = msg.content.replace(/\{.*?\}/g, '').trim();
                    if (cleaned) {
                        appendMessage(cleaned, 'assistant');
                    }
                }
            });
        } else {
            appendMessage("Hello! Welcome to the Autonomous Retail Store. I'm your Product Discovery agent. How can I help you find the perfect product today?", "assistant");
        }
        updateAgentColor(state.currentAgent);
    });

    state.subscribe('agentChanged', (agentName) => {
        updateAgentColor(agentName);
    });

    function updateAgentColor(agentName) {
        agentStatus.textContent = "Agent: " + agentName;
        if (agentName === 'Negotiator') agentStatus.style.color = "#f59e0b";
        else if (agentName === 'OrderTaking') agentStatus.style.color = "#3b82f6";
        else if (agentName === 'Inventory') agentStatus.style.color = "#8b5cf6";
        else agentStatus.style.color = "#34d399";
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
