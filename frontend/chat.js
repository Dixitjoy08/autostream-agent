// ═══════════════════════════════════════════════════════════════════
//  AutoStream Chat UI — chat.js
//  Handles session management, message sending, typing indicator,
//  lead-status updates, and confetti burst on lead capture.
// ═══════════════════════════════════════════════════════════════════

const API_BASE = window.location.origin; // same host as the FastAPI server

// ── State ────────────────────────────────────────────────────────────────────
let sessionId = null;
let isWaiting  = false;

// ── DOM refs ──────────────────────────────────────────────────────────────────
const feed      = document.getElementById('message-feed');
const input     = document.getElementById('user-input');
const sendBtn   = document.getElementById('send-btn');
const leadPanel = document.getElementById('lead-panel');
const leadName  = document.getElementById('lead-name');
const leadEmail = document.getElementById('lead-email');
const leadPlat  = document.getElementById('lead-platform');
const leadPlan  = document.getElementById('lead-plan');
const sfBadge   = document.getElementById('lead-sf-badge');

// ── Helpers ───────────────────────────────────────────────────────────────────
function scrollBottom() {
  feed.scrollTo({ top: feed.scrollHeight, behavior: 'smooth' });
}

function formatText(text) {
  // Convert **bold** markdown and newlines to HTML
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g,   '<em>$1</em>')
    .replace(/\n/g, '<br>');
}

// ── Append a message bubble ───────────────────────────────────────────────────
function appendMessage(role, text) {
  // Remove welcome card on first message
  const welcome = feed.querySelector('.welcome-card');
  if (welcome) welcome.remove();

  const row = document.createElement('div');
  row.className = `msg-row ${role}`;

  const avatar = document.createElement('div');
  avatar.className = 'msg-avatar';
  avatar.textContent = role === 'agent' ? '🤖' : '👤';

  const bubble = document.createElement('div');
  bubble.className = 'msg-bubble';
  bubble.innerHTML = formatText(text);

  row.appendChild(avatar);
  row.appendChild(bubble);
  feed.appendChild(row);
  scrollBottom();
  return row;
}

// ── Typing indicator ──────────────────────────────────────────────────────────
function showTyping() {
  const row = document.createElement('div');
  row.className = 'msg-row agent typing-row';
  row.id = 'typing-indicator';

  const avatar = document.createElement('div');
  avatar.className = 'msg-avatar';
  avatar.textContent = '🤖';

  const bubble = document.createElement('div');
  bubble.className = 'typing-bubble';
  for (let i = 0; i < 3; i++) {
    const dot = document.createElement('div');
    dot.className = 'typing-dot';
    bubble.appendChild(dot);
  }

  row.appendChild(avatar);
  row.appendChild(bubble);
  feed.appendChild(row);
  scrollBottom();
}

function hideTyping() {
  const el = document.getElementById('typing-indicator');
  if (el) el.remove();
}

// ── Lead capture toast ────────────────────────────────────────────────────────
function showLeadToast() {
  const toast = document.createElement('div');
  toast.className = 'lead-toast';
  toast.innerHTML = '🎉 Lead captured and saved to Salesforce CRM!';
  feed.appendChild(toast);
  scrollBottom();
}

// ── Update sidebar lead panel ─────────────────────────────────────────────────
function updateLeadPanel(data) {
  if (data.user_name)     leadName.textContent  = data.user_name;
  if (data.user_email)    leadEmail.textContent = data.user_email;
  if (data.user_platform) leadPlat.textContent  = data.user_platform;
  if (data.user_plan)     leadPlan.textContent  = data.user_plan;

  const hasAny = data.user_name || data.user_email || data.user_platform;
  if (hasAny) leadPanel.classList.add('visible');

  if (data.lead_captured) sfBadge.classList.remove('hidden');
}

// ── Confetti burst ────────────────────────────────────────────────────────────
function launchConfetti() {
  const canvas  = document.getElementById('confetti-canvas');
  const ctx     = canvas.getContext('2d');
  canvas.width  = window.innerWidth;
  canvas.height = window.innerHeight;

  const colors  = ['#a78bfa','#06b6d4','#10b981','#f59e0b','#f43f5e','#ffffff'];
  const pieces  = Array.from({ length: 120 }, () => ({
    x: Math.random() * canvas.width,
    y: Math.random() * -canvas.height,
    r: Math.random() * 6 + 3,
    d: Math.random() * 80 + 40,
    color: colors[Math.floor(Math.random() * colors.length)],
    tilt: Math.random() * 10 - 5,
    tiltAngle: 0,
    tiltSpeed: Math.random() * 0.1 + 0.05,
  }));

  let frame = 0;
  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    pieces.forEach(p => {
      ctx.beginPath();
      ctx.lineWidth = p.r;
      ctx.strokeStyle = p.color;
      ctx.moveTo(p.x + p.tilt + p.r / 4, p.y);
      ctx.lineTo(p.x + p.tilt, p.y + p.tilt + p.r / 4);
      ctx.stroke();

      p.tiltAngle += p.tiltSpeed;
      p.y += (Math.cos(frame / 20 + p.d) + 1 + p.r / 2) / 2;
      p.tilt = Math.sin(p.tiltAngle) * 15;

      if (p.y > canvas.height) {
        p.x = Math.random() * canvas.width;
        p.y = -10;
      }
    });
    frame++;
    if (frame < 240) requestAnimationFrame(draw);
    else ctx.clearRect(0, 0, canvas.width, canvas.height);
  }
  draw();
}

// ── Send message ──────────────────────────────────────────────────────────────
async function sendMessage(text) {
  if (!text.trim() || isWaiting) return;

  isWaiting = true;
  sendBtn.disabled = true;
  input.value = '';
  input.style.height = 'auto';

  appendMessage('user', text);
  showTyping();

  try {
    const res = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, message: text }),
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    const data = await res.json();
    sessionId = data.session_id;

    hideTyping();
    appendMessage('agent', data.response);
    updateLeadPanel(data);

    if (data.lead_captured) {
      showLeadToast();
      launchConfetti();
    }

  } catch (err) {
    hideTyping();
    appendMessage('agent', '⚠️ Connection error. Please try again in a moment.');
    console.error('Chat error:', err);
  } finally {
    isWaiting = false;
    sendBtn.disabled = input.value.trim().length === 0;
  }
}

// ── New chat ──────────────────────────────────────────────────────────────────
async function newChat() {
  if (sessionId) {
    try { await fetch(`${API_BASE}/session/${sessionId}`, { method: 'DELETE' }); }
    catch (_) {}
  }
  sessionId = null;

  // Reset lead panel
  leadName.textContent  = '—';
  leadEmail.textContent = '—';
  leadPlat.textContent  = '—';
  leadPlan.textContent  = '—';
  leadPanel.classList.remove('visible');
  sfBadge.classList.add('hidden');

  // Rebuild the feed with the welcome card
  feed.innerHTML = `
    <div class="welcome-card">
      <div class="welcome-icon">🎬</div>
      <h2>Welcome to AutoStream</h2>
      <p>I'm your AI assistant. Ask me about pricing, features, or get started with a free trial!</p>
      <div class="quick-chips">
        <button class="chip" data-msg="What are your pricing plans?">💰 Pricing</button>
        <button class="chip" data-msg="What features do you offer?">✨ Features</button>
        <button class="chip" data-msg="I want to try the Pro plan">🚀 Get Started</button>
        <button class="chip" data-msg="Do you offer a free trial?">🎁 Free Trial</button>
      </div>
    </div>`;
  bindChips();
}

// ── Auto-resize textarea ──────────────────────────────────────────────────────
function autoResize() {
  input.style.height = 'auto';
  input.style.height = Math.min(input.scrollHeight, 160) + 'px';
}

// ── Event listeners ───────────────────────────────────────────────────────────
function bindChips() {
  feed.querySelectorAll('.chip').forEach(btn => {
    btn.addEventListener('click', () => sendMessage(btn.dataset.msg));
  });
}

sendBtn.addEventListener('click', () => sendMessage(input.value));

input.addEventListener('input', () => {
  autoResize();
  sendBtn.disabled = input.value.trim().length === 0 || isWaiting;
});

input.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage(input.value);
  }
});

document.getElementById('btn-new-chat').addEventListener('click', newChat);

// ── Init ──────────────────────────────────────────────────────────────────────
bindChips();
