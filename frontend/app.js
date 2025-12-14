let platform = "youtube";

function selectPlatform(p, el) {
  // YouTube only now, but we keep it for compatibility
  platform = p || "youtube";

  const title = document.getElementById("platform-title");
  if (title) title.innerText = "YouTube Analysis";

  document.querySelectorAll(".tabs button").forEach(b => b.classList.remove("active"));
  if (el) el.classList.add("active");
}

// ---------- Auth UI (just frontend state) ----------
function syncAuthUI() {
  const isAuthed = localStorage.getItem("weavers_auth") === "1";
  const btn = document.getElementById("authBtn");
  if (!btn) return;

  btn.innerHTML = isAuthed
    ? `<i data-lucide="log-out"></i>`
    : `<i data-lucide="log-in"></i>`;

  btn.title = isAuthed ? "Logout" : "Login";
  lucide.createIcons();
}

function toggleAuth() {
  const isAuthed = localStorage.getItem("weavers_auth") === "1";
  localStorage.setItem("weavers_auth", isAuthed ? "0" : "1");
  syncAuthUI();
}

// ---------- Motion toggle ----------
function toggleTheme() {
  document.body.classList.toggle("reduce-motion");
}

// ---------- Floating icons ----------
function initFloatingIcons() {
  const layer = document.getElementById("float-layer");
  if (!layer) return;

  const icons = ["sparkles", "activity", "youtube", "brain-circuit", "badge-check", "bar-chart-3"];
  const count = 14;

  layer.innerHTML = "";
  for (let i = 0; i < count; i++) {
    const node = document.createElement("div");
    node.className = "float-ico";

    const left = Math.random() * 100;
    const delay = Math.random() * 8;
    const duration = 10 + Math.random() * 18;
    const dx = (Math.random() * 160 - 80).toFixed(0) + "px";

    node.style.left = left + "vw";
    node.style.bottom = (-20 - Math.random() * 60) + "px";
    node.style.animationDelay = `${delay}s`;
    node.style.animationDuration = `${duration}s`;
    node.style.setProperty("--dx", dx);

    const name = icons[Math.floor(Math.random() * icons.length)];
    node.innerHTML = `<i data-lucide="${name}"></i>`;
    layer.appendChild(node);
  }
  lucide.createIcons();
}

// ---------- Helpers ----------
function clamp(n, a, b) { return Math.min(b, Math.max(a, n)); }

function toPercentSmart(x) {
  // Handles both formats:
  // - if backend returns 0..1 => convert to 0..100
  // - if returns 0..100 => keep
  if (x === null || x === undefined || Number.isNaN(x)) return 0;
  const v = Number(x);
  return v <= 1 ? v * 100 : v;
}

function animateNumber(el, from, to, ms = 900, decimals = 1, suffix = "") {
  const start = performance.now();
  const diff = to - from;

  function tick(t) {
    const p = clamp((t - start) / ms, 0, 1);
    // easeOutCubic
    const e = 1 - Math.pow(1 - p, 3);
    const val = from + diff * e;

    el.textContent = `${val.toFixed(decimals)}${suffix}`;
    if (p < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}

function setRing(ringEl, percent) {
  const deg = clamp(percent, 0, 100) * 3.6;
  ringEl.style.background = `conic-gradient(var(--accent2) ${deg}deg, rgba(255,255,255,.08) 0deg)`;
  const inner = ringEl.querySelector("span");
  if (inner) inner.textContent = `${Math.round(percent)}%`;
}

function setBar(barFillEl, percent) {
  barFillEl.style.width = `${clamp(percent, 0, 100)}%`;
}

// ---------- Rendering ----------
function renderLoading() {
  result.innerHTML = `
    <div class="loading">
      <div class="spinner"></div>
      <div>Analyzing…</div>
    </div>
  `;
}

function renderError(message = "Analysis failed") {
  result.innerHTML = `<div class="error">${message}</div>`;
}

function renderVideoResult(data) {
  const viralityPct = toPercentSmart(data.virality_score);
  const recoPct = toPercentSmart(data.recommendation_probability);

  result.innerHTML = `
    <div class="metrics">
      <div class="mcard">
        <div class="mhead">
          <div>
            <div class="mtitle">Virality</div>
            <div class="mvalue"><span id="viralityVal">0.0%</span></div>
            <div class="msub">Normalized score (0–100%)</div>
          </div>
          <div class="ring" id="viralityRing"><span>0%</span></div>
        </div>
        <div class="bar"><div id="viralityBar"></div></div>
      </div>

      <div class="mcard">
        <div class="mhead">
          <div>
            <div class="mtitle">Recommendation</div>
            <div class="mvalue"><span id="recoVal">0.0%</span></div>
            <div class="msub">Probability of being recommended</div>
          </div>
          <div class="ring" id="recoRing"><span>0%</span></div>
        </div>
        <div class="bar"><div id="recoBar"></div></div>
      </div>
    </div>

    <details ${data.video_stats ? "open" : ""}>
      <summary>Raw metrics</summary>
      <pre>${JSON.stringify(data.video_stats || data.input_used || {}, null, 2)}</pre>
    </details>
  `;

  const viralityVal = document.getElementById("viralityVal");
  const recoVal = document.getElementById("recoVal");
  const viralityRing = document.getElementById("viralityRing");
  const recoRing = document.getElementById("recoRing");
  const viralityBar = document.getElementById("viralityBar");
  const recoBar = document.getElementById("recoBar");

  animateNumber(viralityVal, 0, viralityPct, 900, 2, "%");
  animateNumber(recoVal, 0, recoPct, 900, 2, "%");

  setTimeout(() => {
    setRing(viralityRing, viralityPct);
    setRing(recoRing, recoPct);
    setBar(viralityBar, viralityPct);
    setBar(recoBar, recoPct);
  }, 60);
}

function renderCreatorResult(data) {
  const level = (data.creator_level || "average").toLowerCase();

  result.innerHTML = `
    <div class="mcard">
      <div class="mhead">
        <div>
          <div class="mtitle">Creator Level</div>
          <div class="mvalue">${data.creator_level || "Unknown"}</div>
          <div class="msub">Based on your creator-level model</div>
        </div>
        <div class="ring" id="creatorRing"><span>—</span></div>
      </div>

      <details open>
        <summary>Stats used</summary>
        <pre>${JSON.stringify(data.stats_used || {}, null, 2)}</pre>
      </details>
    </div>
  `;

  // small visual ring per level (optional)
  const map = { elite: 92, rising: 70, average: 45, unknown: 25 };
  const pct = map[level] ?? 40;
  const ring = document.getElementById("creatorRing");
  setRing(ring, pct);
}

// ---------- API Calls ----------
async function analyzeVideo() {
  const url = document.getElementById("videoUrl").value.trim();
  let endpoint, payload;

  if (url && url.includes("youtube")) {
    endpoint = "/analyze/video/youtube";
    payload = { url };
  } else {
    endpoint = "/analyze/video/manual";
    payload = {
      views: +views.value || 0,
      likes: +likes.value || 0,
      comments: +comments.value || 0,
      shares: +shares.value || 0,
      saves: +saves.value || 0,
      engagement_rate: +engagement.value || 0,
      trend_label: 1,
      platform: "youtube"
    };
  }

  renderLoading();

  try {
    const res = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      renderError(err.detail || "Analysis failed");
      return;
    }

    const data = await res.json();
    renderVideoResult(data);
  } catch (e) {
    renderError("Network error");
  }
}

async function analyzeCreator() {
  const url = document.getElementById("videoUrl").value.trim();

  if (!url) {
    renderError("Please enter a YouTube channel URL (or a video URL that contains channel info in your backend).");
    return;
  }

  renderLoading();

  try {
    const res = await fetch("/analyze/creator/youtube", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url })
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      renderError(err.detail || "Creator analysis failed");
      return;
    }

    const data = await res.json();
    renderCreatorResult(data);
  } catch (e) {
    renderError("Network error");
  }
}
