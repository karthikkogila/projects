# Quiz.py — Quiz engine: select, history, leaderboard phases.
# Playing + Result are handled by Play.render() called inline.

import time
import streamlit as st
from Database import fetch_random_questions, get_user_history
from Leaderboard import page_leaderboard
from Config import QUIZ_DURATION, TOTAL_QUESTIONS
import Play

TOPIC_META = {
    "ai":              {"icon": "🤖", "label": "Artificial Intelligence"},
    "python":          {"icon": "🐍", "label": "Python"},
    "java":            {"icon": "☕", "label": "Java"},
    "web_development": {"icon": "🌐", "label": "Web Development"},
    "cpp":             {"icon": "⚙️",  "label": "C++"},
    "ethical_hacking": {"icon": "🛡️",  "label": "Ethical Hacking"},
}


# ── Session helpers ────────────────────────────────────────────────────────────

def _init_quiz_state():
    defaults = {
        "quiz_phase":      "select",
        "quiz_topic":      None,
        "quiz_difficulty": None,
        "quiz_questions":  [],
        "quiz_answers":    {},
        "quiz_start_time": None,
        "quiz_q_index":    0,
        "quiz_submitted":  False,
        "quiz_time_up":    False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def _reset_quiz():
    keys = [
        "quiz_phase", "quiz_topic", "quiz_difficulty", "quiz_questions",
        "quiz_answers", "quiz_start_time", "quiz_q_index",
        "quiz_submitted", "quiz_time_up",
    ]
    for k in keys:
        st.session_state.pop(k, None)
    _init_quiz_state()


def _fmt_time(seconds: int) -> str:
    m, s = divmod(max(seconds, 0), 60)
    return f"{m:02d}:{s:02d}"


# ── Phase: Select ──────────────────────────────────────────────────────────────
# The ENTIRE select page lives inside one st.empty() slot.
# When Start is clicked we call slot.empty() which physically removes every
# widget from the page before st.rerun() fires — no bleed-through possible.

def _phase_select():
    slot = st.empty()           # one DOM slot that owns ALL select-page content

    with slot.container():

        # ── Header ──
        st.markdown("""
            <div style='text-align:center;padding:2rem 0 1.5rem'>
                <div style='font-size:3.5rem;margin-bottom:.5rem'>🧠</div>
                <h1 style='font-size:2.4rem;font-weight:800;margin:0;
                           letter-spacing:-0.03em;color:#e8e8f0'>Online Quiz</h1>
                <p style='color:#7a7a9a;font-family:monospace;margin:.5rem 0 0;font-size:.9rem'>
                    15 questions &nbsp;·&nbsp; 5 minutes &nbsp;·&nbsp; Choose your arena
                </p>
            </div>
        """, unsafe_allow_html=True)

        # ── Step 1: Topic ──
        st.markdown("""
            <div style='display:flex;align-items:center;gap:.6rem;margin-bottom:1rem'>
                <div style='background:#7c5cfc;color:#fff;font-size:.7rem;font-weight:800;
                            width:22px;height:22px;border-radius:50%;display:flex;
                            align-items:center;justify-content:center;flex-shrink:0'>1</div>
                <span style='font-weight:700;font-size:1rem;color:#e8e8f0'>Select Topic</span>
            </div>
        """, unsafe_allow_html=True)

        cols = st.columns(3)
        topic_clicked = False
        for i, (key, meta) in enumerate(TOPIC_META.items()):
            col      = cols[i % 3]
            selected = st.session_state.quiz_topic == key
            border   = "#7c5cfc" if selected else "#2a2a3d"
            bg       = "rgba(124,92,252,.13)" if selected else "#12121a"
            glow     = "box-shadow:0 0 0 3px rgba(124,92,252,.25);" if selected else ""
            col.markdown(f"""
                <div style='background:{bg};border:1.5px solid {border};border-radius:16px;
                            padding:1.1rem .7rem;text-align:center;margin-bottom:.3rem;
                            transition:all .15s;{glow}'>
                    <div style='font-size:1.8rem'>{meta['icon']}</div>
                    <div style='font-weight:700;font-size:.8rem;margin-top:.35rem;
                                color:#e8e8f0;letter-spacing:.03em'>{meta['label']}</div>
                    {'<div style="margin-top:.4rem;font-size:.65rem;color:#7c5cfc;font-weight:700">✓ SELECTED</div>' if selected else ''}
                </div>
            """, unsafe_allow_html=True)
            if col.button("Select" if not selected else "✓ Selected",
                          key=f"tp_{key}", use_container_width=True):
                st.session_state.quiz_topic = key
                topic_clicked = True

        if topic_clicked:
            slot.empty()        # wipe page before rerun
            st.rerun()
            st.stop()

        st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

        # ── Step 2: Difficulty ──
        st.markdown("""
            <div style='display:flex;align-items:center;gap:.6rem;margin-bottom:1rem'>
                <div style='background:#7c5cfc;color:#fff;font-size:.7rem;font-weight:800;
                            width:22px;height:22px;border-radius:50%;display:flex;
                            align-items:center;justify-content:center;flex-shrink:0'>2</div>
                <span style='font-weight:700;font-size:1rem;color:#e8e8f0'>Select Difficulty</span>
            </div>
        """, unsafe_allow_html=True)

        diff_meta = [
            ("Easy",   "🟢", "Beginner friendly",  "#5cf8b0", "92,248,176"),
            ("Medium", "🟡", "Intermediate level", "#fcb05c", "252,176,92"),
            ("Hard",   "🔴", "Expert challenge",   "#fc5c7d", "252,92,125"),
        ]
        dcols = st.columns(3)
        diff_clicked = False
        for col, (diff, emoji, desc, color, rgb) in zip(dcols, diff_meta):
            selected = st.session_state.quiz_difficulty == diff
            border   = color if selected else "#2a2a3d"
            bg       = f"rgba({rgb},.1)" if selected else "#12121a"
            glow     = f"box-shadow:0 0 0 3px rgba({rgb},.2);" if selected else ""
            col.markdown(f"""
                <div style='background:{bg};border:1.5px solid {border};border-radius:16px;
                            padding:1rem .8rem;text-align:center;margin-bottom:.3rem;
                            transition:all .15s;{glow}'>
                    <div style='font-size:1.5rem'>{emoji}</div>
                    <div style='font-weight:800;color:{color};font-size:.9rem;margin-top:.3rem'>{diff}</div>
                    <div style='font-size:.72rem;color:#7a7a9a;margin-top:.2rem'>{desc}</div>
                </div>
            """, unsafe_allow_html=True)
            if col.button("Choose" if not selected else "✓ Chosen",
                          key=f"df_{diff}", use_container_width=True):
                st.session_state.quiz_difficulty = diff
                diff_clicked = True

        if diff_clicked:
            slot.empty()        # wipe page before rerun
            st.rerun()
            st.stop()

        st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

        # ── Step 3: Start ──
        topic    = st.session_state.quiz_topic
        diff_sel = st.session_state.quiz_difficulty
        ready    = bool(topic and diff_sel)

        if not ready:
            missing = []
            if not topic:    missing.append("a topic")
            if not diff_sel: missing.append("a difficulty")
            st.markdown(f"""
                <div style='text-align:center;padding:.6rem;background:#1c1c2a;
                            border-radius:10px;border:1px dashed #2a2a3d;margin-bottom:1rem'>
                    <span style='color:#7a7a9a;font-size:.82rem;font-family:monospace'>
                        Please select {" and ".join(missing)} to continue
                    </span>
                </div>
            """, unsafe_allow_html=True)
        else:
            t_label = TOPIC_META[topic]["label"]
            t_icon  = TOPIC_META[topic]["icon"]
            d_color = {"Easy": "#5cf8b0", "Medium": "#fcb05c", "Hard": "#fc5c7d"}.get(diff_sel, "#aaa")
            st.markdown(f"""
                <div style='text-align:center;padding:.6rem;background:#1c1c2a;
                            border-radius:10px;border:1px solid #2a2a3d;margin-bottom:1rem'>
                    <span style='color:#7a7a9a;font-size:.82rem;font-family:monospace'>
                        {t_icon} {t_label} &nbsp;·&nbsp;
                        <span style='color:{d_color}'>{diff_sel}</span>
                        &nbsp;·&nbsp; {TOTAL_QUESTIONS} questions &nbsp;·&nbsp; 5 min
                    </span>
                </div>
            """, unsafe_allow_html=True)

        if st.button(
            "🚀  Start Quiz" if ready else "Select topic & difficulty to begin",
            use_container_width=True,
            disabled=not ready,
            key="start_quiz_btn",
            type="primary" if ready else "secondary",
        ):
            with st.spinner("Loading questions…"):
                qs = fetch_random_questions(topic, diff_sel, TOTAL_QUESTIONS)

            if len(qs) < TOTAL_QUESTIONS:
                st.error(
                    f"Not enough questions for {TOPIC_META[topic]['label']} / {diff_sel}. "
                    f"Found {len(qs)}, need {TOTAL_QUESTIONS}."
                )
                st.stop()

            # Set quiz state
            st.session_state.quiz_questions  = qs
            st.session_state.quiz_answers    = {}
            st.session_state.quiz_q_index    = 0
            st.session_state.quiz_submitted  = False
            st.session_state.quiz_time_up    = False
            st.session_state.quiz_start_time = time.time()
            st.session_state.quiz_phase      = "playing"

            # ── DESTROY the select page completely before rerun ──
            slot.empty()
            st.rerun()
            st.stop()

        # ── Footer nav ──
        st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
        st.divider()
        col1, col2 = st.columns(2)
        if col1.button("📜  My History", use_container_width=True, key="sel_hist"):
            slot.empty()
            st.session_state.quiz_phase = "history"
            st.rerun()
            st.stop()
        if col2.button("🏆  Leaderboard", use_container_width=True, key="sel_lb"):
            slot.empty()
            st.session_state.quiz_phase = "leaderboard"
            st.rerun()
            st.stop()
        st.divider()
        if st.button("← Logout", use_container_width=True, key="sel_logout"):
            slot.empty()
            _reset_quiz()
            st.session_state.page           = "login"
            st.session_state.logged_in_user = None
            st.rerun()
            st.stop()


# ── Phase: History ─────────────────────────────────────────────────────────────

def _phase_history():
    username = st.session_state.get("logged_in_user", "anonymous")
    st.markdown(
        f"<h2>📜 Quiz History — "
        f"<span style='color:#7c5cfc'>{username}</span></h2>",
        unsafe_allow_html=True,
    )

    rows = get_user_history(username)
    if not rows:
        st.info("No quizzes completed yet. Go play one!")
    else:
        avg  = sum(r["score"] for r in rows) / len(rows)
        best = max(r["score"] for r in rows)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Attempts",      len(rows))
        m2.metric("Best Score",    f"{best}/{TOTAL_QUESTIONS}")
        m3.metric("Avg Score",     f"{avg:.1f}/{TOTAL_QUESTIONS}")
        m4.metric("Topics Played", len({r["topic"] for r in rows}))

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
            <div style='display:grid;grid-template-columns:2fr 1fr 1fr 60px 80px;
                gap:.6rem;padding:.4rem .8rem;font-family:monospace;
                font-size:.72rem;color:#7a7a9a;text-transform:uppercase'>
                <span>Topic</span><span>Difficulty</span>
                <span>Score</span><span>Time</span><span>Date</span>
            </div>
        """, unsafe_allow_html=True)

        diff_colors = {"Easy": "#5cf8b0", "Medium": "#fcb05c", "Hard": "#fc5c7d"}
        for r in rows:
            pct      = r["score"] / r["total"]
            score_c  = "#5cf8b0" if pct >= 0.7 else "#fcb05c" if pct >= 0.5 else "#fc5c7d"
            diff_c   = diff_colors.get(r["difficulty"], "#e8e8f0")
            label    = TOPIC_META.get(r["topic"], {}).get("label", r["topic"])
            icon     = TOPIC_META.get(r["topic"], {}).get("icon", "📚")
            date_str = (r["completed_at"].strftime("%d %b")
                        if hasattr(r["completed_at"], "strftime")
                        else str(r["completed_at"])[:10])
            st.markdown(f"""
                <div style='display:grid;grid-template-columns:2fr 1fr 1fr 60px 80px;
                    gap:.6rem;align-items:center;padding:.75rem .8rem;
                    background:#1c1c2a;border:1px solid #2a2a3d;
                    border-radius:12px;margin-bottom:.4rem'>
                    <span style='font-weight:600;color:#e8e8f0'>{icon} {label}</span>
                    <span style='color:{diff_c};font-family:monospace;font-size:.82rem'>{r['difficulty']}</span>
                    <span style='color:{score_c};font-family:monospace;font-weight:700'>{r['score']}/{r['total']}</span>
                    <span style='font-family:monospace;font-size:.8rem;color:#7a7a9a'>{_fmt_time(r['time_taken_s'])}</span>
                    <span style='font-size:.78rem;color:#7a7a9a;font-family:monospace'>{date_str}</span>
                </div>
            """, unsafe_allow_html=True)

    st.divider()
    c1, c2 = st.columns(2)
    if c1.button("← Back", use_container_width=True, key="hist_back"):
        st.session_state.quiz_phase = "select"
        st.rerun()
        st.stop()
    if c2.button("🏆 Leaderboard", use_container_width=True, key="hist_lb"):
        st.session_state.quiz_phase = "leaderboard"
        st.rerun()
        st.stop()


# ── Public entry-point ─────────────────────────────────────────────────────────

def page_quiz():
    _init_quiz_state()
    phase = st.session_state.quiz_phase

    # Playing and result are completely isolated — nothing from select can appear
    if phase in ("playing", "result"):
        Play.render()
        st.stop()
        return

    if phase == "select":
        _phase_select()
    elif phase == "history":
        _phase_history()
    elif phase == "leaderboard":
        page_leaderboard(back_phase="select")
    else:
        st.warning(f"Unknown phase '{phase}'. Resetting.")
        _reset_quiz()
        st.rerun()
        st.stop()