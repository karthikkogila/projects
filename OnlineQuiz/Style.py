# styles.py — All CSS styling for the Online Quiz Application

QUIZ_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Root Variables ─────────────────────────────────────────── */
:root {
    --bg:          #0a0a0f;
    --surface:     #12121a;
    --surface2:    #1c1c2a;
    --border:      #2a2a3d;
    --accent:      #7c5cfc;
    --accent2:     #fc5c7d;
    --accent3:     #5cf8b0;
    --text:        #e8e8f0;
    --text-dim:    #7a7a9a;
    --easy:        #5cf8b0;
    --medium:      #fcb05c;
    --hard:        #fc5c7d;
    --radius:      14px;
    --radius-lg:   22px;
    --font-main:   'Syne', sans-serif;
    --font-mono:   'JetBrains Mono', monospace;
}

/* ── Global Reset ───────────────────────────────────────────── */
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

[data-testid="stHeader"] { background: transparent !important; }

section[data-testid="stSidebar"] { display: none !important; }

/* ── Typography ─────────────────────────────────────────────── */
h1, h2, h3 {
    font-family: var(--font-main) !important;
    letter-spacing: -0.03em;
    color: var(--text) !important;
}
h1 { font-size: 2.6rem !important; font-weight: 800 !important; }
h2 { font-size: 1.8rem !important; font-weight: 700 !important; }
h3 { font-size: 1.3rem !important; font-weight: 600 !important; }

p, label, span, div {
    font-family: var(--font-main) !important;
    color: var(--text) !important;
}

/* ── Streamlit Overrides ────────────────────────────────────── */
[data-testid="stTextInput"] > div > div > input,
[data-testid="stSelectbox"] > div > div {
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

/* ── Buttons ─────────────────────────────────────────────────── */
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
.stButton > button:active { transform: translateY(0) !important; }

/* Primary (full-width) button accent */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--accent), #a064fc) !important;
    border-color: transparent !important;
    color: #fff !important;
}
.stButton > button[kind="primary"]:hover {
    color: #fff !important;
    box-shadow: 0 4px 24px rgba(124,92,252,.45) !important;
}

/* ── Cards ───────────────────────────────────────────────────── */
.quiz-card {
    background: var(--surface);
    border: 1.5px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 2rem;
    margin-bottom: 1.2rem;
    position: relative;
    overflow: hidden;
}
.quiz-card::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(124,92,252,.06) 0%, transparent 60%);
    pointer-events: none;
}

/* ── Timer ───────────────────────────────────────────────────── */
.timer-bar-container {
    background: var(--surface2);
    border-radius: 999px;
    height: 8px;
    overflow: hidden;
    margin: 0.6rem 0 1.4rem;
    border: 1px solid var(--border);
}
.timer-bar {
    height: 100%;
    border-radius: 999px;
    transition: width .9s linear, background .5s;
}

.timer-display {
    font-family: var(--font-mono) !important;
    font-size: 2.2rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    text-align: center;
    color: var(--text) !important;
}
.timer-danger { color: var(--hard) !important; }

/* ── Question Number ─────────────────────────────────────────── */
.q-meta {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    margin-bottom: 1rem;
}
.q-badge {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0.2rem 0.7rem;
    font-family: var(--font-mono);
    font-size: 0.78rem;
    color: var(--text-dim) !important;
}
.diff-easy  { border-color: var(--easy)  !important; color: var(--easy)  !important; }
.diff-medium{ border-color: var(--medium)!important; color: var(--medium)!important; }
.diff-hard  { border-color: var(--hard)  !important; color: var(--hard)  !important; }

/* ── Option Buttons ──────────────────────────────────────────── */
.option-btn {
    display: block;
    width: 100%;
    background: var(--surface2);
    border: 1.5px solid var(--border);
    border-radius: var(--radius);
    color: var(--text);
    font-family: var(--font-main);
    font-size: 0.95rem;
    font-weight: 500;
    text-align: left;
    padding: 0.85rem 1.2rem;
    margin-bottom: 0.6rem;
    cursor: pointer;
    transition: all .18s;
}
.option-btn:hover {
    border-color: var(--accent);
    background: rgba(124,92,252,.1);
    transform: translateX(4px);
}
.option-selected { border-color: var(--accent) !important; background: rgba(124,92,252,.18) !important; }
.option-correct  { border-color: var(--easy)   !important; background: rgba(92,248,176,.12) !important; color: var(--easy)  !important; }
.option-wrong    { border-color: var(--hard)    !important; background: rgba(252,92,125,.12) !important; color: var(--hard)  !important; }

/* ── Progress dots ───────────────────────────────────────────── */
.progress-dots {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    margin: 1rem 0;
    justify-content: center;
}
.p-dot {
    width: 10px; height: 10px;
    border-radius: 50%;
    background: var(--border);
    transition: background .2s;
}
.p-dot.answered  { background: var(--accent); }
.p-dot.correct   { background: var(--easy); }
.p-dot.wrong     { background: var(--hard); }
.p-dot.current   { background: var(--text); box-shadow: 0 0 8px rgba(232,232,240,.5); }

/* ── Result Screen ───────────────────────────────────────────── */
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
.result-label {
    text-align: center;
    color: var(--text-dim) !important;
    font-size: 0.9rem;
    margin-top: 0.3rem;
    font-family: var(--font-mono) !important;
}

/* ── Leaderboard ─────────────────────────────────────────────── */
.lb-row {
    display: grid;
    grid-template-columns: 40px 1fr 80px 100px 80px;
    align-items: center;
    gap: 0.8rem;
    padding: 0.8rem 1rem;
    border-radius: var(--radius);
    border: 1px solid var(--border);
    background: var(--surface2);
    margin-bottom: 0.5rem;
    transition: border-color .18s;
}
.lb-row:hover { border-color: var(--accent); }
.lb-rank {
    font-family: var(--font-mono);
    font-weight: 700;
    font-size: 1rem;
    color: var(--text-dim) !important;
    text-align: center;
}
.rank-1 { color: #ffd700 !important; }
.rank-2 { color: #c0c0c0 !important; }
.rank-3 { color: #cd7f32 !important; }
.lb-score {
    font-family: var(--font-mono);
    font-weight: 700;
    color: var(--accent) !important;
    text-align: right;
}
.lb-topic {
    font-size: 0.78rem;
    padding: 0.15rem 0.5rem;
    border-radius: 6px;
    border: 1px solid var(--border);
    color: var(--text-dim) !important;
    font-family: var(--font-mono) !important;
    text-align: center;
}
.lb-time {
    font-size: 0.78rem;
    color: var(--text-dim) !important;
    font-family: var(--font-mono) !important;
    text-align: right;
}

/* ── Topic Cards (mode selection) ───────────────────────────── */
.topic-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin: 1.2rem 0;
}
.topic-card {
    background: var(--surface);
    border: 1.5px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.4rem 1rem;
    text-align: center;
    cursor: pointer;
    transition: all .22s;
    position: relative;
    overflow: hidden;
}
.topic-card:hover {
    border-color: var(--accent);
    transform: translateY(-3px);
    box-shadow: 0 8px 30px rgba(124,92,252,.2);
}
.topic-card.selected {
    border-color: var(--accent);
    background: rgba(124,92,252,.12);
}
.topic-icon { font-size: 2rem; margin-bottom: 0.4rem; }
.topic-name {
    font-weight: 700;
    font-size: 0.88rem;
    color: var(--text) !important;
    letter-spacing: 0.04em;
}

/* ── Divider ─────────────────────────────────────────────────── */
hr { border-color: var(--border) !important; }

/* ── Alerts & Messages ───────────────────────────────────────── */
[data-testid="stAlert"] {
    border-radius: var(--radius) !important;
    border-left-width: 3px !important;
}

/* ── Scrollbar ───────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }

/* ── Radio buttons ───────────────────────────────────────────── */
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
[data-testid="stRadio"] [data-testid="stMarkdownContainer"] { padding: 0 !important; }

/* ── Selectbox ───────────────────────────────────────────────── */
[data-testid="stSelectbox"] svg { fill: var(--text-dim) !important; }

/* ── Metric ──────────────────────────────────────────────────── */
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

</style>
"""