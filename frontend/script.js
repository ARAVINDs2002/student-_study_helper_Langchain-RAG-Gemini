const API_URL = 'http://localhost:8000';
let currentMode = 'gemini';
let sessionId = 'session_' + Math.random().toString(36).substr(2, 9);
let backendOnline = false;

// ─── DOM refs ───────────────────────────────────────────────────
const btnGemini        = document.getElementById('btn-gemini');
const btnRag           = document.getElementById('btn-rag');
const uploadSection    = document.getElementById('upload-section');
const chatHistory      = document.getElementById('chat-history');
const chatInput        = document.getElementById('chat-input');
const btnSend          = document.getElementById('btn-send');
const btnUpload        = document.getElementById('btn-upload');
const fileInput        = document.getElementById('file-input');
const uploadStatus     = document.getElementById('upload-status');
const loadingIndicator = document.getElementById('loading-indicator');
const statusDot        = document.getElementById('status-dot');
const statusLabel      = document.getElementById('status-label');

// ─── Backend Status Polling ─────────────────────────────────────
function setStatus(online) {
    backendOnline = online;
    statusDot.className = 'dot ' + (online ? 'online' : 'offline');
    statusLabel.textContent = online ? 'Online' : 'Offline';
    // Disable input while backend is down
    btnSend.disabled = !online;
    chatInput.disabled = !online;
    chatInput.placeholder = online
        ? 'Type your question here...'
        : 'Backend is offline — please wait...';
}

async function pollBackend() {
    try {
        const res = await fetch(`${API_URL}/health`, { signal: AbortSignal.timeout(2000) });
        if (res.ok) {
            if (!backendOnline) setStatus(true); // first time coming online
        } else {
            setStatus(false);
        }
    } catch {
        setStatus(false);
    }
}

// Initial state: connecting (amber)
statusDot.className = 'dot connecting';
statusLabel.textContent = 'Connecting...';
pollBackend();
setInterval(pollBackend, 3000); // check every 3 seconds

// ─── Mode Toggling ──────────────────────────────────────────────
btnGemini.addEventListener('click', () => {
    currentMode = 'gemini';
    btnGemini.classList.add('active');
    btnRag.classList.remove('active');
    uploadSection.classList.add('hidden');
});

btnRag.addEventListener('click', () => {
    currentMode = 'rag';
    btnRag.classList.add('active');
    btnGemini.classList.remove('active');
    uploadSection.classList.remove('hidden');
});

// ─── Document Upload ────────────────────────────────────────────
btnUpload.addEventListener('click', async () => {
    const file = fileInput.files[0];
    if (!file) { showStatus('Please select a file to upload.', true); return; }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('session_id', sessionId);

    try {
        btnUpload.disabled = true;
        btnUpload.textContent = 'Uploading...';
        showStatus('Processing document context...');

        const response = await fetch(`${API_URL}/upload`, { method: 'POST', body: formData });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || 'Upload failed');
        showStatus('✅ Success! Now start asking questions.');
    } catch (error) {
        showStatus(error.message, true);
    } finally {
        btnUpload.disabled = false;
        btnUpload.textContent = 'Upload File';
    }
});

function showStatus(msg, isError = false) {
    uploadStatus.textContent = msg;
    uploadStatus.className = 'status-msg ' + (isError ? 'status-error' : '');
}

// ─── Chat Logic ─────────────────────────────────────────────────
btnSend.addEventListener('click', sendMessage);
chatInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') sendMessage(); });

function createMessageElement(isUser) {
    const div = document.createElement('div');
    div.className = `message ${isUser ? 'user-message' : 'ai-message'}`;
    return div;
}

function renderAIResponse(data) {
    const container = createMessageElement(false);

    // ── Explanation ──
    const explanationNode = document.createElement('div');
    explanationNode.innerHTML = `<strong>${data.subject || 'Answer'}:</strong> ${data.explanation}`;
    container.appendChild(explanationNode);

    // ── Details block ──
    const detailsNode = document.createElement('div');
    detailsNode.className = 'ai-detail-block';

    // Flowchart (base64 PNG from backend)
    if (data.flowchart_img && typeof data.flowchart_img === 'string' && data.flowchart_img.trim() !== '') {
        const flowSection = document.createElement('div');
        flowSection.innerHTML = `<h4>📊 Step-by-Step Workflow</h4>`;

        const imgWrap = document.createElement('div');
        imgWrap.style.cssText = 'background:#F0F4FF;padding:12px;border-radius:10px;text-align:center;overflow-x:auto;margin-top:8px;';

        const img = document.createElement('img');
        img.src = `data:image/png;base64,${data.flowchart_img}`;
        img.alt = 'Workflow diagram';
        img.style.cssText = 'max-width:100%;height:auto;border-radius:8px;display:block;margin:0 auto;';
        img.onerror = () => { imgWrap.style.display = 'none'; };

        imgWrap.appendChild(img);
        flowSection.appendChild(imgWrap);
        detailsNode.appendChild(flowSection);
    }

    // Images
    if (data.image_urls && data.image_urls.length > 0) {
        const imgHeader = document.createElement('h4');
        imgHeader.textContent = '🖼️ Visual References';
        imgHeader.style.marginTop = '14px';
        detailsNode.appendChild(imgHeader);

        const grid = document.createElement('div');
        grid.className = 'ai-image-grid';

        data.image_urls.forEach(url => {
            const anchor = document.createElement('a');
            anchor.href = `https://www.google.com/search?tbm=isch&q=${encodeURIComponent(data.image_query || '')}`;
            anchor.target = '_blank';
            anchor.title = 'View on Google Images';

            const img = document.createElement('img');
            img.src = url;
            img.alt = data.image_query || 'Visual reference';
            img.onerror = () => { anchor.style.display = 'none'; };

            anchor.appendChild(img);
            grid.appendChild(anchor);
        });
        detailsNode.appendChild(grid);
    }

    if (detailsNode.children.length > 0) {
        container.appendChild(detailsNode);
    }

    chatHistory.appendChild(container);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

async function sendMessage() {
    if (!backendOnline) return;
    const text = chatInput.value.trim();
    if (!text) return;

    const userMsg = createMessageElement(true);
    userMsg.textContent = text;
    chatHistory.appendChild(userMsg);
    chatHistory.scrollTop = chatHistory.scrollHeight;

    chatInput.value = '';
    loadingIndicator.classList.remove('hidden');

    try {
        const response = await fetch(`${API_URL}/ask`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId, question: text, mode: currentMode })
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || 'Failed to get answer');
        renderAIResponse(data);
    } catch (error) {
        const errorMsg = createMessageElement(false);
        errorMsg.textContent = '⚠️ Error: ' + error.message;
        chatHistory.appendChild(errorMsg);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    } finally {
        loadingIndicator.classList.add('hidden');
    }
}
