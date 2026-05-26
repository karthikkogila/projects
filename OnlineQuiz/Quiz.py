# Quiz.py — Quiz engine page (imported and called from App.py)

import time
import streamlit as st
from Database import (
    fetch_random_questions,
    save_score,
    get_user_history,
    get_leaderboard,
)

QUIZ_DURATION   = 5 * 60   # 300 seconds
TOTAL_QUESTIONS = 15

TOPIC_META = {
    "ai":               {"icon": "🤖", "label": "Artificial Intelligence"},
    "python":           {"icon": "🐍", "label": "Python"},
    "java":             {"icon": "☕", "label": "Java"},
    "web_development":  {"icon": "🌐", "label": "Web Development"},
    "cpp":              {"icon": "⚙️",  "label": "C++"},
    "ethical_hacking":  {"icon": "🛡️",  "label": "Ethical Hacking"},
}

DIFF_COLORS = {"Easy": "easy", "Medium": "medium", "Hard": "hard"}


# ── Session helpers ────────────────────────────────────────────────────────────

def _init_quiz_state():
    defaults = {
        "quiz_phase":       "select",   # select | playing | result | history | leaderboard
        "quiz_topic":       None,
        "quiz_difficulty":  None,
        "quiz_questions":   [],         # list[dict] – 15 questions
        "quiz_answers":     {},         # {idx: 'A'|'B'|'C'|'D'}
        "quiz_start_time":  None,       # float – time.time()
        "quiz_q_index":     0,          # current question (0-based)
        "quiz_submitted":   False,      # True once user clicks Submit
        "quiz_time_up":     False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def _reset_quiz():
    """Wipe temporary quiz state so user can start fresh."""
    keys = [
        "quiz_phase","quiz_topic","quiz_difficulty","quiz_questions",
        "quiz_answers","quiz_start_time","quiz_q_index",
        "quiz_submitted","quiz_time_up",
    ]
    for k in keys:
        if k in st.session_state:
            del st.session_state[k]
    _init_quiz_state()


def _fmt_time(seconds: int) -> str:
    m, s = divmod(max(seconds, 0), 60)
    return f"{m:02d}:{s:02d}"


def _elapsed() -> int:
    if st.session_state.quiz_start_time is None:
        return 0
    return int(time.time() - st.session_state.quiz_start_time)


def _remaining() -> int:
    return max(QUIZ_DURATION - _elapsed(), 0)


def _score() -> int:
    correct = 0
    for idx, chosen in st.session_state.quiz_answers.items():
        q = st.session_state.quiz_questions[idx]
        if chosen == q["correct_answer"]:
            correct += 1
    return correct


# ── Phase: Select topic & difficulty ──────────────────────────────────────────

def _phase_select():
    st.markdown(
        "<h1 style='text-align:center;margin-bottom:0'>🧠 Online Quiz</h1>"
        "<p style='text-align:center;color:var(--text-dim);margin-top:.3rem;font-family:var(--font-mono)'>"
        "15 questions · 5 minutes · Choose your arena</p>",
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Topic selection ──
    st.markdown("### 📚 Select Topic")
    cols = st.columns(3)
    for i, (key, meta) in enumerate(TOPIC_META.items()):
        col = cols[i % 3]
        selected = st.session_state.quiz_topic == key
        border = "var(--accent)" if selected else "var(--border)"
        bg     = "rgba(124,92,252,.12)" if selected else "var(--surface)"
        col.markdown(
            f"""<div style='background:{bg};border:1.5px solid {border};
                border-radius:18px;padding:1.2rem 0.8rem;text-align:center;
                margin-bottom:0.4rem;transition:all .2s'>
                <div style='font-size:1.9rem'>{meta['icon']}</div>
                <div style='font-weight:700;font-size:.85rem;letter-spacing:.04em;margin-top:.3rem'>
                    {meta['label']}</div>
            </div>""",
            unsafe_allow_html=True,
        )
        if col.button(
            "✓ Selected" if selected else "Select",
            key=f"tp_{key}",
            use_container_width=True,
        ):
            st.session_state.quiz_topic = key
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Difficulty selection ──
    st.markdown("### 🎯 Select Difficulty")
    diff_cols = st.columns(3)
    diffs = [
        ("Easy",   "🟢", "Beginner-friendly",  "var(--easy)"),
        ("Medium", "🟡", "Intermediate level", "var(--medium)"),
        ("Hard",   "🔴", "Expert challenge",   "var(--hard)"),
    ]
    for col, (diff, emoji, desc, color) in zip(diff_cols, diffs):
        selected = st.session_state.quiz_difficulty == diff
        border   = color if selected else "var(--border)"
        bg       = f"rgba({_hex_to_rgb(color)},.1)" if selected else "var(--surface)"
        col.markdown(
            f"""<div style='background:{bg};border:1.5px solid {border};
                border-radius:14px;padding:1rem;text-align:center;margin-bottom:.4rem'>
                <div style='font-size:1.5rem'>{emoji}</div>
                <div style='font-weight:700;color:{color};font-size:.9rem'>{diff}</div>
                <div style='font-size:.75rem;color:var(--text-dim);margin-top:.2rem'>{desc}</div>
            </div>""",
            unsafe_allow_html=True,
        )
        if col.button(
            "✓ Chosen" if selected else "Choose",
            key=f"df_{diff}",
            use_container_width=True,
        ):
            st.session_state.quiz_difficulty = diff
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Start button ──
    start_ready = st.session_state.quiz_topic and st.session_state.quiz_difficulty
    if st.button(
        "🚀  Start Quiz" if start_ready else "Select topic & difficulty to begin",
        use_container_width=True,
        disabled=not start_ready,
    ):
        qs = fetch_random_questions(
            st.session_state.quiz_topic,
            st.session_state.quiz_difficulty,
            TOTAL_QUESTIONS,
        )
        if len(qs) < TOTAL_QUESTIONS:
            st.error(
                f"Not enough questions in the database for "
                f"{st.session_state.quiz_topic} / {st.session_state.quiz_difficulty}. "
                f"Found {len(qs)}, need {TOTAL_QUESTIONS}."
            )
        else:
            st.session_state.quiz_questions  = qs
            st.session_state.quiz_answers    = {}
            st.session_state.quiz_q_index    = 0
            st.session_state.quiz_submitted  = False
            st.session_state.quiz_time_up    = False
            st.session_state.quiz_start_time = time.time()
            st.session_state.quiz_phase      = "playing"
            st.rerun()

    st.divider()
    col1, col2 = st.columns(2)
    if col1.button("📜 My History", use_container_width=True):
        st.session_state.quiz_phase = "history"
        st.rerun()
    if col2.button("🏆 Leaderboard", use_container_width=True):
        st.session_state.quiz_phase = "leaderboard"
        st.rerun()

    st.divider()
    if st.button("← Logout", use_container_width=True):
        username = st.session_state.get("logged_in_user")
        _reset_quiz()
        st.session_state.page            = "login"
        st.session_state.logged_in_user  = None
        st.rerun()


def _hex_to_rgb(css_var: str) -> str:
    """Return '124,92,252' etc. for known vars – fallback gracefully."""
    m = {
        "var(--easy)":   "92,248,176",
        "var(--medium)": "252,176,92",
        "var(--hard)":   "252,92,125",
        "var(--accent)": "124,92,252",
    }
    return m.get(css_var, "124,92,252")


# ── Phase: Playing ─────────────────────────────────────────────────────────────

def _phase_playing():
    st.session_state.page = "quiz"  # Ensure we're on the quiz page
    questions = st.session_state.quiz_questions
    idx       = st.session_state.quiz_q_index
    remaining = _remaining()

    # Auto-submit when time is up
    if remaining == 0 and not st.session_state.quiz_submitted:
        st.session_state.quiz_submitted = True
        st.session_state.quiz_time_up   = True
        _do_submit()
        return

    # ── Timer display ──
    pct         = remaining / QUIZ_DURATION
    bar_color   = (
        "var(--easy)"   if pct > 0.5 else
        "var(--medium)" if pct > 0.25 else
        "var(--hard)"
    )
    time_class  = "timer-danger" if pct < 0.2 else ""

    st.markdown(
        f"""<div style='text-align:center'>
            <div class='timer-display {time_class}'>{_fmt_time(remaining)}</div>
            <div class='timer-bar-container'>
                <div class='timer-bar'
                     style='width:{pct*100:.1f}%;background:{bar_color}'></div>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )

    # ── Progress dots ──
    dots_html = "<div class='progress-dots'>"
    for i in range(TOTAL_QUESTIONS):
        cls = "p-dot"
        if i == idx:
            cls += " current"
        elif i in st.session_state.quiz_answers:
            cls += " answered"
        dots_html += f"<div class='{cls}'></div>"
    dots_html += "</div>"
    st.markdown(dots_html, unsafe_allow_html=True)

    # ── Question card ──
    q         = questions[idx]
    diff      = q["difficulty"]
    diff_cls  = DIFF_COLORS.get(diff, "")

    st.markdown(
        f"""<div class='quiz-card'>
            <div class='q-meta'>
                <span class='q-badge'>Q {idx+1} / {TOTAL_QUESTIONS}</span>
                <span class='q-badge diff-{diff_cls.lower()}'>{diff}</span>
            </div>
            <p style='font-size:1.05rem;font-weight:600;margin:0;line-height:1.5'>{q['question']}</p>
        </div>""",
        unsafe_allow_html=True,
    )

    # ── Options as radio buttons ──
    options = {
        "A": q["option_a"], "B": q["option_b"],
        "C": q["option_c"], "D": q["option_d"],
    }

    # Build a label dict for the radio
    radio_labels = {f"**{letter}.** {text}": letter for letter, text in options.items()}
    current_label = None
    currently_chosen = st.session_state.quiz_answers.get(idx)
    if currently_chosen:
        current_label = f"**{currently_chosen}.** {options[currently_chosen]}"

    chosen_label = st.radio(
        "Select your answer:",
        options=list(radio_labels.keys()),
        index=(list(radio_labels.keys()).index(current_label) if current_label else None),
        key=f"radio_{idx}",
        label_visibility="collapsed",
    )

    # Update session state when radio selection changes
    chosen_letter = radio_labels.get(chosen_label)
    st.session_state.quiz_answers[idx] = chosen_letter

    # ── Navigation ──
    nav_l, nav_m, nav_r = st.columns([1, 2, 1])

    if nav_l.button("← Prev", disabled=(idx == 0), use_container_width=True):
        st.session_state.quiz_q_index = idx - 1
        st.rerun()

    answered = len(st.session_state.quiz_answers)
    nav_m.markdown(
        f"<p style='text-align:center;color:var(--text-dim);font-family:var(--font-mono);font-size:.82rem;margin-top:.6rem'>"
        f"{answered}/{TOTAL_QUESTIONS} answered</p>",
        unsafe_allow_html=True,
    )

    if idx < TOTAL_QUESTIONS - 1:
        if nav_r.button("Next →", use_container_width=True):
            st.session_state.quiz_q_index = idx + 1
            st.rerun()
    else:
        if nav_r.button("✅ Submit", use_container_width=True):
            _do_submit()
            return

    # Auto-refresh every second to keep timer live
    time.sleep(1)
    st.rerun()


def _do_submit():
    """Calculate score, persist it, move to result phase."""
    elapsed  = _elapsed()
    score    = _score()
    username = st.session_state.get("logged_in_user", "anonymous")

    save_score(
        username=username,
        topic=st.session_state.quiz_topic,
        difficulty=st.session_state.quiz_difficulty,
        score=score,
        total=TOTAL_QUESTIONS,
        time_taken_s=min(elapsed, QUIZ_DURATION),
    )

    st.session_state.quiz_phase = "result"
    st.rerun()


# ── Phase: Result ──────────────────────────────────────────────────────────────

def _phase_result():
    score     = _score()
    total     = TOTAL_QUESTIONS
    elapsed   = _elapsed()
    questions = st.session_state.quiz_questions

    pct = score / total
    grade_emoji = "🏆" if pct >= 0.9 else "🌟" if pct >= 0.7 else "👍" if pct >= 0.5 else "📖"
    grade_label = (
        "Outstanding!" if pct >= 0.9 else
        "Great job!"   if pct >= 0.7 else
        "Good effort!" if pct >= 0.5 else
        "Keep practising!"
    )

    if st.session_state.quiz_time_up:
        st.warning("⏰ Time's up! Your quiz was auto-submitted.")

    st.markdown(
        f"""<div class='quiz-card' style='text-align:center;padding:2.5rem'>
            <div style='font-size:3rem;margin-bottom:.5rem'>{grade_emoji}</div>
            <div class='result-score'>{score} / {total}</div>
            <div class='result-label'>{grade_label}</div>
            <div style='margin-top:1.2rem;display:flex;gap:1.5rem;justify-content:center;flex-wrap:wrap'>
                <div style='text-align:center'>
                    <div style='font-family:var(--font-mono);font-size:1.3rem;font-weight:700;
                                color:var(--accent)'>{int(pct*100)}%</div>
                    <div style='font-size:.75rem;color:var(--text-dim)'>Accuracy</div>
                </div>
                <div style='text-align:center'>
                    <div style='font-family:var(--font-mono);font-size:1.3rem;font-weight:700;
                                color:var(--accent3)'>{_fmt_time(min(elapsed,QUIZ_DURATION))}</div>
                    <div style='font-size:.75rem;color:var(--text-dim)'>Time taken</div>
                </div>
                <div style='text-align:center'>
                    <div style='font-family:var(--font-mono);font-size:1.3rem;font-weight:700;
                                color:var(--medium)'>{st.session_state.quiz_difficulty}</div>
                    <div style='font-size:.75rem;color:var(--text-dim)'>Difficulty</div>
                </div>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )

    # ── Answer review ──
    with st.expander("📋 Review Answers", expanded=False):
        for i, q in enumerate(questions):
            chosen  = st.session_state.quiz_answers.get(i, "—")
            correct = q["correct_answer"]
            icon    = "✅" if chosen == correct else "❌"
            st.markdown(
                f"""<div class='quiz-card' style='padding:1.2rem;margin-bottom:.8rem'>
                    <div style='font-size:.8rem;color:var(--text-dim);font-family:var(--font-mono);
                                margin-bottom:.4rem'>Q{i+1} · {q['difficulty']}</div>
                    <p style='font-weight:600;margin:0 0 .6rem'>{q['question']}</p>
                    <div style='display:flex;gap:1rem;flex-wrap:wrap;font-family:var(--font-mono);
                                font-size:.85rem'>
                        <span>Your answer: <b style='color:{"var(--easy)" if chosen==correct else "var(--hard)"}'>{chosen}</b></span>
                        <span>Correct: <b style='color:var(--easy)'>{correct}</b></span>
                        <span>{icon}</span>
                    </div>
                    <div style='margin-top:.5rem;font-size:.82rem;color:var(--text-dim)'>
                        💡 {q.get('explanation','')}</div>
                </div>""",
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    if c1.button("🔄 Play Again",    use_container_width=True):
        _reset_quiz()
        st.rerun()
    if c2.button("📜 My History",    use_container_width=True):
        st.session_state.quiz_phase = "history"
        st.rerun()
    if c3.button("🏆 Leaderboard",   use_container_width=True):
        st.session_state.quiz_phase = "leaderboard"
        st.rerun()


# ── Phase: History ─────────────────────────────────────────────────────────────

def _phase_history():
    username = st.session_state.get("logged_in_user", "anonymous")
    st.markdown(f"<h2>📜 Quiz History — <span style='color:var(--accent)'>{username}</span></h2>",
                unsafe_allow_html=True)

    rows = get_user_history(username)
    if not rows:
        st.info("You haven't completed any quizzes yet. Go play one!")
    else:
        # Summary metrics
        m1, m2, m3, m4 = st.columns(4)
        avg_score = sum(r["score"] for r in rows) / len(rows)
        best      = max(r["score"] for r in rows)
        m1.metric("Attempts",   len(rows))
        m2.metric("Best Score", f"{best}/{TOTAL_QUESTIONS}")
        m3.metric("Avg Score",  f"{avg_score:.1f}/{TOTAL_QUESTIONS}")
        m4.metric("Topics played", len({r["topic"] for r in rows}))

        st.markdown("<br>", unsafe_allow_html=True)

        # Table header
        st.markdown(
            """<div style='display:grid;grid-template-columns:2fr 1fr 1fr 60px 80px;
                gap:.6rem;padding:.4rem .8rem;font-family:var(--font-mono);
                font-size:.75rem;color:var(--text-dim);text-transform:uppercase'>
                <span>Topic</span><span>Difficulty</span>
                <span>Score</span><span>Time</span><span>Date</span>
            </div>""",
            unsafe_allow_html=True,
        )
        for r in rows:
            pct       = r["score"] / r["total"]
            score_col = "var(--easy)" if pct >= 0.7 else "var(--medium)" if pct >= 0.5 else "var(--hard)"
            diff_c    = {"Easy":"var(--easy)","Medium":"var(--medium)","Hard":"var(--hard)"}.get(r["difficulty"],"var(--text)")
            label     = TOPIC_META.get(r["topic"], {}).get("label", r["topic"])
            icon      = TOPIC_META.get(r["topic"], {}).get("icon", "📚")
            date_str  = r["completed_at"].strftime("%d %b") if hasattr(r["completed_at"],"strftime") else str(r["completed_at"])[:10]
            st.markdown(
                f"""<div style='display:grid;grid-template-columns:2fr 1fr 1fr 60px 80px;
                    gap:.6rem;align-items:center;padding:.75rem .8rem;
                    background:var(--surface2);border:1px solid var(--border);
                    border-radius:12px;margin-bottom:.4rem'>
                    <span style='font-weight:600'>{icon} {label}</span>
                    <span style='color:{diff_c};font-family:var(--font-mono);font-size:.82rem'>{r['difficulty']}</span>
                    <span style='color:{score_col};font-family:var(--font-mono);font-weight:700'>{r['score']}/{r['total']}</span>
                    <span style='font-family:var(--font-mono);font-size:.8rem;color:var(--text-dim)'>{_fmt_time(r['time_taken_s'])}</span>
                    <span style='font-size:.78rem;color:var(--text-dim);font-family:var(--font-mono)'>{date_str}</span>
                </div>""",
                unsafe_allow_html=True,
            )

    st.divider()
    c1, c2 = st.columns(2)
    if c1.button("← Back",          use_container_width=True):
        st.session_state.quiz_phase = "select"
        st.rerun()
    if c2.button("🏆 Leaderboard",   use_container_width=True):
        st.session_state.quiz_phase = "leaderboard"
        st.rerun()


# ── Phase: Leaderboard ─────────────────────────────────────────────────────────

def _phase_leaderboard():
    st.markdown("<h2>🏆 Global Leaderboard</h2>", unsafe_allow_html=True)

    rows = get_leaderboard(20)
    if not rows:
        st.info("No scores yet — be the first to complete a quiz!")
    else:
        # Podium top-3
        podium = rows[:3]
        pcols  = st.columns(len(podium))
        medals = ["🥇","🥈","🥉"]
        for col, row, medal in zip(pcols, podium, medals):
            pct = row["score"] / row["total"]
            col.markdown(
                f"""<div style='background:var(--surface);border:1.5px solid var(--border);
                    border-radius:18px;padding:1.4rem;text-align:center'>
                    <div style='font-size:2rem'>{medal}</div>
                    <div style='font-weight:800;font-size:1rem;margin:.3rem 0'>{row['username']}</div>
                    <div style='font-family:var(--font-mono);font-size:1.5rem;font-weight:700;
                                color:var(--accent)'>{row['score']}/{row['total']}</div>
                    <div style='font-size:.75rem;color:var(--text-dim);margin-top:.3rem'>
                        {TOPIC_META.get(row['topic'],{}).get('label',row['topic'])} · {row['difficulty']}</div>
                    <div style='font-size:.72rem;color:var(--text-dim);font-family:var(--font-mono)'>
                        ⏱ {_fmt_time(row['time_taken_s'])}</div>
                </div>""",
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # Full table header
        st.markdown(
            """<div style='display:grid;grid-template-columns:40px 1fr 1.2fr 1fr 60px 80px 80px;
                gap:.6rem;padding:.4rem .8rem;font-family:var(--font-mono);
                font-size:.72rem;color:var(--text-dim);text-transform:uppercase'>
                <span>#</span><span>Player</span><span>Topic</span>
                <span>Difficulty</span><span>Score</span><span>Time</span><span>Date</span>
            </div>""",
            unsafe_allow_html=True,
        )
        logged_user = st.session_state.get("logged_in_user","")
        for row in rows:
            label     = TOPIC_META.get(row["topic"],{}).get("label", row["topic"])
            icon      = TOPIC_META.get(row["topic"],{}).get("icon","📚")
            diff_c    = {"Easy":"var(--easy)","Medium":"var(--medium)","Hard":"var(--hard)"}.get(row["difficulty"],"var(--text)")
            pct       = row["score"] / row["total"]
            score_col = "var(--easy)" if pct >= 0.7 else "var(--medium)" if pct >= 0.5 else "var(--hard)"
            date_str  = row["completed_at"].strftime("%d %b") if hasattr(row["completed_at"],"strftime") else str(row["completed_at"])[:10]
            is_me     = row["username"] == logged_user
            border    = "var(--accent)" if is_me else "var(--border)"
            bg        = "rgba(124,92,252,.08)" if is_me else "var(--surface2)"
            rank_colors = {1:"#ffd700",2:"#c0c0c0",3:"#cd7f32"}
            rank_col  = rank_colors.get(row["rank"],"var(--text-dim)")
            st.markdown(
                f"""<div style='display:grid;grid-template-columns:40px 1fr 1.2fr 1fr 60px 80px 80px;
                    gap:.6rem;align-items:center;padding:.7rem .8rem;
                    background:{bg};border:1px solid {border};
                    border-radius:12px;margin-bottom:.4rem'>
                    <span style='font-family:var(--font-mono);font-weight:700;color:{rank_col};text-align:center'>{row['rank']}</span>
                    <span style='font-weight:{"800" if is_me else "500"}'>{row['username']}{"  ← you" if is_me else ""}</span>
                    <span style='font-size:.82rem'>{icon} {label}</span>
                    <span style='color:{diff_c};font-family:var(--font-mono);font-size:.82rem'>{row['difficulty']}</span>
                    <span style='color:{score_col};font-family:var(--font-mono);font-weight:700;text-align:right'>{row['score']}/{row['total']}</span>
                    <span style='font-family:var(--font-mono);font-size:.78rem;color:var(--text-dim);text-align:right'>{_fmt_time(row['time_taken_s'])}</span>
                    <span style='font-size:.75rem;color:var(--text-dim);font-family:var(--font-mono);text-align:right'>{date_str}</span>
                </div>""",
                unsafe_allow_html=True,
            )

    st.divider()
    c1, c2 = st.columns(2)
    if c1.button("← Back",        use_container_width=True):
        st.session_state.quiz_phase = "select"
        st.rerun()
    if c2.button("📜 My History",  use_container_width=True):
        st.session_state.quiz_phase = "history"
        st.rerun()


# ── Public entry-point ─────────────────────────────────────────────────────────

def page_quiz():
    """Called from App.py when st.session_state.page == 'quiz'."""
    _init_quiz_state()

    phase = st.session_state.quiz_phase
    {
        "select":      _phase_select,
        "playing":     _phase_playing,
        "result":      _phase_result,
        "history":     _phase_history,
        "leaderboard": _phase_leaderboard,
    }[phase]()