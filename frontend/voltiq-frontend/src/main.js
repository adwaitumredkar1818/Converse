import { marked } from 'marked';

// ── marked config ─────────────────────────────────────────────────────────────
// marked v18+ uses a new API — configure via the Marked constructor or use
// marked.use() instead of the deprecated marked.setOptions()
marked.use({ breaks: true, gfm: true });

document.addEventListener('DOMContentLoaded', () => {

    // ── DOM refs ──────────────────────────────────────────────────────────────
    const chatInner      = document.getElementById('chat-inner');
    const chatArea       = document.getElementById('chat-area');
    const chatInput      = document.getElementById('chat-input');
    const sendBtn        = document.getElementById('send-btn');
    const newChatBtn     = document.getElementById('new-chat-btn');
    const hamburger      = document.getElementById('hamburger');
    const sidebar        = document.getElementById('sidebar');
    const sidebarOverlay = document.getElementById('sidebar-overlay');
    const statModel      = document.getElementById('stat-model');
    const statDocs       = document.getElementById('stat-docs');
    const statUpdated    = document.getElementById('stat-updated');

    // Sidebar nav items
    const navChat        = document.getElementById('nav-chat');
    const navStatus      = document.getElementById('nav-status');
    const navSettings    = document.getElementById('nav-settings');

    const API_BASE   = 'http://127.0.0.1:8000';
    const CHAT_URL   = `${API_BASE}/chat`;
    const STATUS_URL = `${API_BASE}/status`;

    // ── Welcome screen HTML ───────────────────────────────────────────────────
    const WELCOME_HTML = `
        <div id="welcome">
            <svg class="welcome-logo" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M32 4L8 14v18c0 15 11 28.5 24 32 13-3.5 24-17 24-32V14L32 4z" fill="#0D1117" stroke="#22C55E" stroke-width="2"/>
                <path d="M32 11L15 19v14c0 11 8.5 21 17 24.5 8.5-3.5 17-13.5 17-24.5V19L32 11z" fill="#172033"/>
                <path d="M32 22v20M23 32l9-10 9 10" stroke="#22C55E" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
                <circle cx="32" cy="39" r="2.5" fill="#38BDF8"/>
            </svg>
            <div class="welcome-title">DarkKnights Energy Intelligence</div>
            <p class="welcome-sub">
                Ask questions about grid telemetry, energy consumption statistics, or policy documents — grounded in real data.
            </p>
            <div class="welcome-chips">
                <div class="chip" data-q="What is the average household energy consumption?">Avg. household consumption</div>
                <div class="chip" data-q="How does temperature affect energy consumption?">Temperature vs. consumption</div>
                <div class="chip" data-q="Compare Standard and Time-of-Use tariffs.">Standard vs. TOU tariffs</div>
                <div class="chip" data-q="What is the average consumption during winter?">Winter consumption</div>
                <div class="chip" data-q="How does consumption differ on bank holidays?">Bank holiday patterns</div>
            </div>
        </div>
    `;

    // ── Helpers ───────────────────────────────────────────────────────────────
    function escapeHTML(str) {
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    function scrollToBottom() {
        chatArea.scrollTo({ top: chatArea.scrollHeight, behavior: 'smooth' });
    }

    function setInputDisabled(disabled) {
        sendBtn.disabled   = disabled;
        chatInput.disabled = disabled;
    }

    // ── Safely parse markdown ─────────────────────────────────────────────────
    // Falls back to plain text if marked throws
    function safeMarkdown(text) {
        try {
            return marked.parse(String(text));
        } catch (e) {
            console.warn('marked.parse failed, falling back to plain text:', e);
            return `<p>${escapeHTML(String(text))}</p>`;
        }
    }

    // ── Welcome screen ────────────────────────────────────────────────────────
    function showWelcome() {
        chatInner.innerHTML = WELCOME_HTML;
        chatInner.querySelectorAll('.chip').forEach(chip => {
            chip.addEventListener('click', () => {
                chatInput.value = chip.dataset.q;
                chatInput.focus();
                handleSend();
            });
        });
    }

    showWelcome();

    // ── Message builders ──────────────────────────────────────────────────────
    function appendUserMessage(text) {
        const el = document.createElement('div');
        el.className = 'msg-row user';
        el.innerHTML = `
            <div class="avatar user">U</div>
            <div class="msg-bubble user">${escapeHTML(text)}</div>
        `;
        chatInner.appendChild(el);
    }

    function appendLoadingMessage() {
        const el = document.createElement('div');
        el.className = 'msg-row loading-row';
        el.innerHTML = `
            <div class="avatar bot">
                <svg width="18" height="18" viewBox="0 0 36 36" fill="none">
                    <path d="M18 3L5 9v8c0 7 5 13.5 13 16 8-2.5 13-9 13-16V9L18 3z" fill="#172033" stroke="#22C55E" stroke-width="1.5"/>
                </svg>
            </div>
            <div class="msg-bubble bot">
                <div class="bot-header">DarkKnights RAG</div>
                <div class="loading-dots">
                    <span></span><span></span><span></span>
                </div>
            </div>
        `;
        chatInner.appendChild(el);
        return el;
    }

    // ── Build bot response bubble ─────────────────────────────────────────────
    // Reads EXACTLY: data.success, data.answer, data.error,
    //                data.latencies_ms, data.sources, data.model
    function buildBotMessage(data) {
        // ── 1. Extract answer ─────────────────────────────────────────────
        const rawAnswer = (data.answer != null && data.answer !== '')
            ? String(data.answer)
            : 'No answer received.';

        // Strip citation markers injected by the LLM (e.g. 【...】)
        const clean = rawAnswer
            .replace(/【[^】]*】/g, '')
            .replace(/\[source:[^\]]*\]/gi, '')
            .replace(/\[Tabular \/ Metrics Context\]/gi, '')
            .replace(/ {2,}/g, ' ')
            .trim();

        // ── 2. Render markdown safely ─────────────────────────────────────
        const rendered = safeMarkdown(clean || rawAnswer);

        // ── 3. Latency badge ──────────────────────────────────────────────
        const latencyMs  = data.latencies_ms?.end_to_end;
        const latencyTag = (latencyMs != null)
            ? `<span class="latency-tag">${Math.round(latencyMs)} ms</span>`
            : '';

        // ── 4. Sources ────────────────────────────────────────────────────
        const sourceItems = [];

        // Tabular source: only include if it is a real value (not "N/A")
        const tabularSource = data.sources?.tabular_source;
        if (tabularSource && tabularSource !== 'N/A') {
            if (tabularSource.includes('household_stats')) {
                sourceItems.push('🏠 Household Energy Stats');
            } else if (tabularSource.includes('consumption_stats')) {
                sourceItems.push('⚡ Consumption Stats');
            } else {
                // Show the actual source label (truncated for UI)
                const label = tabularSource.length > 60
                    ? tabularSource.slice(0, 57) + '…'
                    : tabularSource;
                sourceItems.push('📊 ' + label);
            }
        }

        // Document chunks: deduplicate by file name
        const chunks = data.sources?.retrieved_chunks;
        if (Array.isArray(chunks)) {
            const seen = new Set();
            chunks.forEach(chunk => {
                const fn = chunk.metadata?.file_name;
                if (fn && !seen.has(fn)) {
                    seen.add(fn);
                    sourceItems.push((fn.endsWith('.pdf') ? '📄 ' : '📚 ') + fn);
                }
            });
        }

        // Fallback if no sources found at all
        if (sourceItems.length === 0) {
            sourceItems.push('📚 DarkKnights Knowledge Base');
        }

        // ── 5. Category badge (optional) ──────────────────────────────────
        const category = data.category
            ? `<span class="source-tag" style="color:var(--accent2);border-color:rgba(56,189,248,0.3)">${escapeHTML(data.category)}</span>`
            : '';

        const sourceTags = sourceItems
            .map(s => `<span class="source-tag">${escapeHTML(s)}</span>`)
            .join('');

        // ── 6. Build DOM element ──────────────────────────────────────────
        const el = document.createElement('div');
        el.className = 'msg-row';
        el.innerHTML = `
            <div class="avatar bot">
                <svg width="18" height="18" viewBox="0 0 36 36" fill="none">
                    <path d="M18 3L5 9v8c0 7 5 13.5 13 16 8-2.5 13-9 13-16V9L18 3z" fill="#172033" stroke="#22C55E" stroke-width="1.5"/>
                </svg>
            </div>
            <div class="msg-bubble bot">
                <div class="bot-header">DarkKnights RAG</div>
                <div class="bot-content">${rendered}</div>
                <div class="sources-footer">
                    <span class="sources-label">Sources</span>
                    ${category}
                    ${sourceTags}
                    ${latencyTag}
                </div>
            </div>
        `;
        return el;
    }

    // ── Build error bubble ────────────────────────────────────────────────────
    function buildErrorMessage(msg) {
        const el = document.createElement('div');
        el.className = 'msg-row';
        el.innerHTML = `
            <div class="avatar bot" style="border-color:#EF4444">⚠</div>
            <div class="msg-bubble bot" style="border-color:#EF4444">
                <div class="bot-header" style="color:#EF4444">Connection Error</div>
                <p style="color:#F87171;font-size:13px;">${escapeHTML(msg)}</p>
                <p style="color:#94A3B8;font-size:12px;margin-top:8px;">
                    Make sure the FastAPI backend is running on port <strong>8000</strong>:<br>
                    <code style="font-size:11px;color:#38BDF8">uvicorn api:app --reload --port 8000</code>
                </p>
            </div>
        `;
        return el;
    }

    // ── Send logic ────────────────────────────────────────────────────────────
    async function handleSend() {
        const text = chatInput.value.trim();
        if (!text) return;

        // Remove welcome / status / settings screen if present
        const welcome = chatInner.querySelector('#welcome');
        if (welcome) welcome.remove();

        appendUserMessage(text);
        chatInput.value = '';
        setInputDisabled(true);
        scrollToBottom();

        const loadingEl = appendLoadingMessage();
        scrollToBottom();

        try {
            const res = await fetch(CHAT_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                // Send exactly { "query": "<text>" } — no other fields
                body: JSON.stringify({ query: text })
            });

            if (!res.ok) {
                throw new Error(`Backend returned HTTP ${res.status}`);
            }

            const data = await res.json();
            loadingEl.remove();

            // data.success === true  → render data.answer
            // data.success === false → render data.error
            if (data.success === false) {
                throw new Error(data.error || 'Backend returned success=false');
            }

            // Update model badge in sidebar with the real model name
            if (data.model && statModel) {
                statModel.textContent = String(data.model)
                    .replace('openai/', '')
                    .replace('gpt-4o', 'GPT-4o')
                    .replace('gpt-', 'GPT-');
            }

            chatInner.appendChild(buildBotMessage(data));

        } catch (err) {
            console.error('RAG API Error:', err);
            if (loadingEl.parentNode) loadingEl.remove();
            chatInner.appendChild(buildErrorMessage(err.message));
        } finally {
            setInputDisabled(false);
            chatInput.focus();
            scrollToBottom();
        }
    }

    // ── Event listeners ───────────────────────────────────────────────────────
    sendBtn.addEventListener('click', handleSend);

    chatInput.addEventListener('keydown', e => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    });

    // New chat — clear all messages and return to welcome screen
    newChatBtn.addEventListener('click', () => {
        showWelcome();
        chatInput.value = '';
        chatInput.focus();
        closeSidebar();
        setActiveNav(navChat);
    });

    // ── Sidebar: mobile hamburger ─────────────────────────────────────────────
    function openSidebar() {
        sidebar.classList.add('open');
        sidebarOverlay.classList.add('open');
    }
    function closeSidebar() {
        sidebar.classList.remove('open');
        sidebarOverlay.classList.remove('open');
    }
    hamburger.addEventListener('click', () => {
        sidebar.classList.contains('open') ? closeSidebar() : openSidebar();
    });
    sidebarOverlay.addEventListener('click', closeSidebar);

    // ── Sidebar: nav items ────────────────────────────────────────────────────
    navChat.addEventListener('click', () => {
        setActiveNav(navChat);
        closeSidebar();
    });
    navStatus.addEventListener('click', () => {
        setActiveNav(navStatus);
        fetchAndShowStatus();
        closeSidebar();
    });
    navSettings.addEventListener('click', () => {
        setActiveNav(navSettings);
        showSettingsPlaceholder();
        closeSidebar();
    });

    function setActiveNav(el) {
        [navChat, navStatus, navSettings].forEach(n => n.classList.remove('active'));
        el.classList.add('active');
    }

    // ── Settings placeholder ──────────────────────────────────────────────────
    function showSettingsPlaceholder() {
        chatInner.innerHTML = `
            <div id="welcome">
                <svg class="welcome-logo" viewBox="0 0 64 64" fill="none">
                    <circle cx="32" cy="32" r="8" stroke="#22C55E" stroke-width="2"/>
                    <path d="M32 8v6M32 50v6M8 32h6M50 32h6" stroke="#22C55E" stroke-width="2" stroke-linecap="round"/>
                </svg>
                <div class="welcome-title">Settings</div>
                <p class="welcome-sub" style="color:#64748B;">
                    Settings panel — coming soon.<br>
                    Backend is configured via environment variables and <code>scripts/</code> config files.
                </p>
            </div>
        `;
    }

    // ── Status page ───────────────────────────────────────────────────────────
    function fetchAndShowStatus() {
        chatInner.innerHTML = `
            <div id="welcome">
                <div class="welcome-title">System Status</div>
                <p class="welcome-sub" id="status-content" style="color:var(--muted)">Loading…</p>
            </div>
        `;
        fetch(STATUS_URL)
            .then(r => r.json())
            .then(d => {
                const el = document.getElementById('status-content');
                if (!el) return;
                el.innerHTML = `
                    <span style="color:#22C55E">✓ API Online</span> &nbsp;·&nbsp;
                    ${escapeHTML(String(d.documents))} documents indexed &nbsp;·&nbsp;
                    Last update: ${escapeHTML(String(d.last_update))}
                `;
            })
            .catch(() => {
                const el = document.getElementById('status-content');
                if (el) el.textContent = 'Could not reach backend.';
            });
    }

    // ── Sidebar status (live data from /status) ───────────────────────────────
    async function refreshSidebarStatus() {
        try {
            const res  = await fetch(STATUS_URL);
            const data = await res.json();
            if (statDocs)    statDocs.textContent    = data.documents ?? '—';
            if (statUpdated) statUpdated.textContent = data.last_update ?? '—';
        } catch {
            if (statDocs)    statDocs.textContent    = 'N/A';
            if (statUpdated) statUpdated.textContent = 'N/A';
        }
    }

    refreshSidebarStatus();

});
