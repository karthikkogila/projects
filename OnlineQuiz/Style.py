# Style.py — All CSS styling for the Online Quiz Application

QUIZ_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Root Variables ─────────────────────────────────────── */
:root {
    --bg:         #0a0a0f;
    --surface:    #12121a;
    --surface2:   #1c1c2a;
    --border:     #2a2a3d;
    --accent:     #7c5cfc;
    --accent2:    #fc5c7d;
    --accent3:    #5cf8b0;
    --text:       #e8e8f0;
    --text-dim:   #7a7a9a;
    --easy:       #5cf8b0;
    --medium:     #fcb05c;
    --hard:       #fc5c7d;
    --radius:     14px;
    --radius-lg:  22px;
    --font-main:  'Syne', sans-serif;
    --font-mono:  'JetBrains Mono', monospace;
}

/* ── Global Reset ───────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--font-main) !important;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 80% 60% at 20% 0%, rgba(124,92,252,.12) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 100%, rgba(252,92,125,.08) 0%, transparent 60%),
        var(--bg) !important;
    min-height: 100vh;
}

[data-testid="stHeader"]  { background: transparent !important; }
section[data-testid="stSidebar"] { display: none !important; }

/* ── Typography ─────────────────────────────────────────── */
h1, h2, h3 {
    font-family: var(--font-main) !important;
    letter-spacing: -0.03em;
    color: var(--text) !important;
}
h1 { font-size: 2.6rem !important; font-weight: 800 !important; }
h2 { font-size: 1.8rem !important; font-weight: 700 !important; }
h3 { font-size: 1.3rem !important; font-weight: 600 !important; }
p, label, span, div { font-family: var(--font-main) !important; color: var(--text) !important; }

/* ── Inputs ─────────────────────────────────────────────── */
[data-testid="stTextInput"] > div > div > input {
    background: var(--surface2) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--text) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.92rem !important;
    padding: 0.6rem 1rem !important;
    transition: border-color .2s;
}
[data-testid="stTextInput"] > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(124,92,252,.18) !important;
    outline: none !important;
}

/* ── Buttons ─────────────────────────────────────────────── */
.stButton > button {
    background: var(--surface2) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--text) !important;
    font-family: var(--font-main) !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.03em !important;
    padding: 0.55rem 1.4rem !important;
    transition: all .2s !important;
    cursor: pointer !important;
}
.stButton > button:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
    box-shadow: 0 0 16px rgba(124,92,252,.25) !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active  { transform: translateY(0) !important; }
.stButton > button:disabled {
    opacity: .4 !important;
    cursor: not-allowed !important;
}

/* ── Timer ───────────────────────────────────────────────── */
.timer-display {
    font-family: var(--font-mono) !important;
    font-size: 2.2rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    text-align: center;
    color: var(--text) !important;
}
.timer-danger { color: var(--hard) !important; }

/* ── Result Screen ───────────────────────────────────────── */
.result-score {
    font-size: 4.5rem;
    font-weight: 800;
    letter-spacing: -0.04em;
    line-height: 1;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-align: center;
}

/* ── Radio buttons ───────────────────────────────────────── */
[data-testid="stRadio"] label {
    background: var(--surface2) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 0.7rem 1.1rem !important;
    display: block !important;
    width: 100% !important;
    margin-bottom: 0.5rem !important;
    cursor: pointer !important;
    transition: all .18s !important;
    font-size: 0.95rem !important;
}
[data-testid="stRadio"] label:hover {
    border-color: var(--accent) !important;
    background: rgba(124,92,252,.1) !important;
}

/* ── Metric ──────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 1rem !important;
}
[data-testid="stMetricValue"] {
    font-family: var(--font-mono) !important;
    color: var(--accent) !important;
}

/* ── Alerts ──────────────────────────────────────────────── */
[data-testid="stAlert"] {
    border-radius: var(--radius) !important;
    border-left-width: 3px !important;
}

/* ── Divider ─────────────────────────────────────────────── */
hr { border-color: var(--border) !important; }

/* ── Scrollbar ───────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }

/* ── Tabs ────────────────────────────────────────────────── */
[data-testid="stTabs"] [data-baseweb="tab"] {
    background: var(--surface2) !important;
    border-radius: 8px 8px 0 0 !important;
    color: var(--text-dim) !important;
    font-family: var(--font-main) !important;
    font-weight: 600 !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom: 2px solid var(--accent) !important;
}
</style>
"""