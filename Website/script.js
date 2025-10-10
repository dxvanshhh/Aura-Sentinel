/* ============================
   VANTA 3D BACKGROUND (net)
   ============================ */

/*
  This initializes Vanta.NET on the element with id="vanta-bg".
  It creates a moving, connected "mesh" of lines that looks techy.
*/
VANTA.NET({
  el: "#vanta-bg",
  mouseControls: true,
  touchControls: true,
  minHeight: 200.00,
  minWidth: 200.00,
  scale: 1.0,
  scaleMobile: 1.0,
  color: 0x00f3ff,    // cyan
  backgroundColor: 0x070720,
  points: 12,
  maxDistance: 20.00
});

/* ============================
   MOCK LOGIN (front-end)
   ============================ */

/*
  Simple demo login: when user submits login form on login.html,
  we save the user's email in localStorage and redirect to index.html.
  This is NOT secure — front-end only — but good for demo and learning.
*/
const loginForm = document.getElementById("loginForm");
if (loginForm) {
  loginForm.addEventListener("submit", function (ev) {
    ev.preventDefault(); // stop form from reloading the page
    const email = document.getElementById("loginEmail").value.trim();
    // Save user's email to localStorage to "remember" sign-in
    localStorage.setItem("aura_user_email", email);
    // Redirect to main page (index.html)
    window.location.href = "index.html";
  });
}

/* ============================
   ON MAIN PAGE: show signed-in user
   ============================ */
const signedEl = document.getElementById("signedInAs");
if (signedEl) {
  const userEmail = localStorage.getItem("aura_user_email");
  if (userEmail) signedEl.textContent = "Signed in as: " + userEmail;
  else signedEl.textContent = "Not signed in (demo)";
}

/* ============================
   DOWNLOAD BUTTON (demo)
   ============================ */
/*
  The download button is a placeholder. Replace the href in index.html
  or use this JS to set a real link. For demonstration we show a message.
*/
const dl = document.getElementById("downloadBtn");
if (dl) {
  dl.addEventListener("click", function (ev) {
    ev.preventDefault();
    alert("Demo: Replace the download link with your extension store link or file URL.");
    // To make it actually download, set dl.href = "https://link-to-your-extension";
  });
}

/* ============================
   PHISHING DEMO
   ============================ */
function phishingDemo() {
  // simple alert demo — safe and offline
  alert("⚠ Aura Sentinel Demo: This is a simulated phishing link. Do NOT click suspicious links on real sites.");
}

/* ============================
   REVIEWS (client-side only)
   ============================ */
function escapeHtml(text) {
  return text.replace(/[&<>"']/g, function (m) {
    return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[m];
  });
}

function submitReview() {
  const nameEl = document.getElementById("username");
  const textEl = document.getElementById("reviewText");
  const list = document.getElementById("reviewsList");
  if (!nameEl || !textEl || !list) return;
  const name = nameEl.value.trim();
  const text = textEl.value.trim();
  if (!name || !text) {
    alert("Please enter your name and a short review.");
    return;
  }
  const div = document.createElement("div");
  div.className = "review";
  div.innerHTML = `<strong>${escapeHtml(name)}</strong><p>${escapeHtml(text)}</p>`;
  list.insertBefore(div, list.firstChild);
  nameEl.value = ""; textEl.value = "";
}

/* ============================
   CHATBOT (AuraBot) — prewritten
   ============================ */
/*
  toggleChat() shows/hides the chat window.
  sendMessage() reads the user's message, displays it,
  then selects a canned reply (by keyword contains) and displays it.
*/
function toggleChat() {
  const w = document.getElementById("chat-window");
  if (!w) return;
  w.style.display = (w.style.display === "flex") ? "none" : "flex";
  if (w.style.display === "flex") {
    const inp = document.getElementById("userInput");
    if (inp) inp.focus();
  }
}

function appendChatMessage(text, who = "bot") {
  const body = document.getElementById("chat-body");
  if (!body) return;
  const el = document.createElement("div");
  el.className = who === "bot" ? "bot-msg" : "user-msg";
  el.textContent = text;
  body.appendChild(el);
  body.scrollTop = body.scrollHeight;
}

/* Prewritten responses: key => reply */
const botResponses = {
  "what is phishing": "Phishing is a scam where attackers try to trick people into giving sensitive information like passwords or card details.",
  "how does aura sentinel work": "Aura Sentinel analyzes link patterns, domain signals and content heuristics to compute a risk score and show clear warnings.",
  "contact support": "You can reach our customer care at +91 12345 67890 (Mon-Fri 9am-6pm).",
  "customer care": "Customer care: +91 12345 67890 — available Mon-Fri 9am-6pm.",
  "give me a security tip": "Hover over links to check the real URL, enable 2FA, and never share one-time passwords with anyone.",
  "is it free": "The demo/hackathon version is free. Production rollout and pricing can be discussed later."
};

function sendMessage() {
  const inp = document.getElementById("userInput");
  if (!inp) return;
  const raw = inp.value.trim();
  if (!raw) return;
  appendChatMessage(raw, "user");
  inp.value = "";

  const key = raw.toLowerCase();
  // default reply:
  let reply = "🤖 Sorry, I don't understand that yet. Try: 'What is phishing', 'Give me a security tip', or 'Contact support'.";

  // keyword matching (simple)
  for (const k in botResponses) {
    if (key.includes(k)) {
      reply = botResponses[k];
      break;
    }
  }
  // small delay to mimic thinking
  setTimeout(() => appendChatMessage(reply, "bot"), 400);
}

/* initial greeting when main page loads */
window.addEventListener("load", function () {
  setTimeout(() => {
    // if chat is present, show greeting
    if (document.getElementById("chat-body")) {
      appendChatMessage("Hello! I'm AuraBot — ask about phishing, how Aura Sentinel works, or type 'Contact support'.", "bot");
    }
  }, 700);
});

/* ============================
   SCROLL APPEAR ANIMATIONS
   ============================ */
const scrollEls = document.querySelectorAll(".scroll");
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) entry.target.classList.add("visible");
  });
}, { threshold: 0.2 });
scrollEls.forEach(el => observer.observe(el));
