# Play.py — Playing + Result phases, rendered inline by Quiz.py.
# Must NOT call st.set_page_config() — only App.py does that.
# Every st.rerun() is followed by st.stop() so no stale UI bleeds through.

import time
import streamlit as st
from Database import save_score
from Config import QUIZ_DURATION, TOTAL_QUESTIONS

TOPIC_META = {
    "ai":              {"icon": "🤖", "label": "Artificial Intelligence"},
    "python":          {"icon": "🐍", "label": "Python"},
    "java":            {"icon": "☕", "label": "Java"},
    "web_development": {"icon": "🌐", "label": "Web Development"},
    "cpp":             {"icon": "⚙️",  "label": "C++"},
    "ethical_hacking": {"icon": "🛡️",  "label": "Ethical Hacking"},
}


# ── Helpers ────────────────────────────────────────────────────────────────────

def _fmt_time(seconds: int) -> str:
    m, s = divmod(max(seconds, 0), 60)
    return f"{m:02d}:{s:02d}"


def _elapsed() -> int:
    t = st.session_state.get("quiz_start_time")
    return 0 if t is None else int(time.time() - t)


def _remaining() -> int:
    return max(QUIZ_DURATION - _elapsed(), 0)


def _score() -> int:
    questions = st.session_state.get("quiz_questions", [])
    answers   = st.session_state.get("quiz_answers", {})
    return sum(
        1 for idx, chosen in answers.items()
        if idx < len(questions) and questions[idx]["correct_answer"] == chosen
    )


def _do_submit():
    """Save score and switch to result phase — then rerun+stop."""
    elapsed  = _elapsed()
    score    = _score()
    username = st.session_state.get("logged_in_user", "Guest")
    save_score(
        username     = username,
        topic        = st.session_state.quiz_topic,
        difficulty   = st.session_state.quiz_difficulty,
        score        = score,
        total        = TOTAL_QUESTIONS,
        time_taken_s = min(elapsed, QUIZ_DURATION),
    )
    st.session_state.quiz_submitted = True
    st.session_state.quiz_phase     = "result"
    st.rerun()
    st.stop()


# ── Phase: Playing ─────────────────────────────────────────────────────────────

def _phase_playing():
    questions = st.session_state.get("quiz_questions", [])
    if not questions:
        st.error("⚠️ No questions loaded. Please go back and start a new quiz.")
        if st.button("← Back to Quiz Select", key="play_back_err"):
            st.session_state.quiz_phase = "select"
            st.rerun()
            st.stop()
        st.stop()
        return

    idx       = st.session_state.get("quiz_q_index", 0)
    remaining = _remaining()
    answers   = st.session_state.get("quiz_answers", {})

    # Auto-submit on timeout
    if remaining == 0 and not st.session_state.get("quiz_submitted"):
        st.session_state.quiz_time_up = True
        _do_submit()
        return   # _do_submit already called st.rerun()+st.stop()

    # ── Timer ──
    pct        = remaining / QUIZ_DURATION
    bar_color  = "#5cf8b0" if pct > 0.5 else "#fcb05c" if pct > 0.25 else "#fc5c7d"
    time_color = "#fc5c7d" if pct < 0.2 else "#e8e8f0"

    st.markdown(
        f"""
        <div style='text-align:center;margin-bottom:.8rem'>
            <div style='font-size:2rem;font-weight:800;font-family:monospace;
                        letter-spacing:.1em;color:{time_color}'>
                ⏱ {_fmt_time(remaining)}
            </div>
            <div style='background:#2a2a3d;border-radius:99px;height:8px;
                        margin:.4rem auto;max-width:420px;overflow:hidden'>
                <div style='width:{pct*100:.1f}%;background:{bar_color};
                            height:8px;border-radius:99px;
                            transition:width 1s linear'></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Progress dots ──
    dots = ""
    for i in range(TOTAL_QUESTIONS):
        if i == idx:
            color, size = "#7c5cfc", "14px"
        elif i in answers:
            color, size = "#5cf8b0", "10px"
        else:
            color, size = "#2a2a3d", "10px"
        dots += (
            f"<div style='width:{size};height:{size};border-radius:50%;"
            f"background:{color};transition:all .2s;flex-shrink:0'></div>"
        )
    st.markdown(
        f"<div style='display:flex;gap:6px;justify-content:center;"
        f"flex-wrap:wrap;margin-bottom:1.2rem'>{dots}</div>",
        unsafe_allow_html=True,
    )

    # ── Question card ──
    q          = questions[idx]
    diff       = q.get("difficulty", "")
    diff_color = {"Easy": "#5cf8b0", "Medium": "#fcb05c", "Hard": "#fc5c7d"}.get(diff, "#aaa")

    st.markdown(
        f"""
        <div style='background:#12121a;border:1.5px solid #2a2a3d;
                    border-radius:18px;padding:1.4rem 1.6rem;margin-bottom:1rem'>
            <div style='display:flex;gap:.5rem;align-items:center;margin-bottom:.8rem;flex-wrap:wrap'>
                <span style='background:#1c1c2a;border-radius:8px;padding:.25rem .7rem;
                             font-size:.78rem;font-family:monospace;color:#7a7a9a'>
                    Q {idx + 1} / {TOTAL_QUESTIONS}
                </span>
                <span style='background:#1c1c2a;border-radius:8px;padding:.25rem .7rem;
                             font-size:.78rem;font-family:monospace;color:{diff_color}'>
                    {diff}
                </span>
                <span style='background:#1c1c2a;border-radius:8px;padding:.25rem .7rem;
                             font-size:.78rem;font-family:monospace;color:#7a7a9a'>
                    {len(answers)}/{TOTAL_QUESTIONS} answered
                </span>
            </div>
            <p style='font-size:1.05rem;font-weight:600;margin:0;
                      line-height:1.6;color:#e8e8f0'>
                {q['question']}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Answer options ──
    raw_opts = {
        "A": q.get("option_a", ""),
        "B": q.get("option_b", ""),
        "C": q.get("option_c", ""),
        "D": q.get("option_d", ""),
    }
    options    = {k: v for k, v in raw_opts.items() if v.strip()}
    radio_opts = [f"{k}. {v}" for k, v in options.items()]
    letter_map = {f"{k}. {v}": k for k, v in options.items()}

    cur_chosen = answers.get(idx)
    cur_index  = None
    if cur_chosen:
        candidate = f"{cur_chosen}. {options.get(cur_chosen, '')}"
        if candidate in radio_opts:
            cur_index = radio_opts.index(candidate)

    chosen_label = st.radio(
        "Select your answer:",
        options          = radio_opts,
        index            = cur_index,
        key              = f"radio_q{idx}",
        label_visibility = "collapsed",
    )
    if chosen_label:
        letter = letter_map.get(chosen_label)
        if letter:
            st.session_state.quiz_answers[idx] = letter

    # ── Navigation ──
    st.markdown("<br>", unsafe_allow_html=True)
    nav_l, nav_r = st.columns(2)

    if nav_l.button("← Previous", disabled=(idx == 0),
                    use_container_width=True, key="play_prev"):
        st.session_state.quiz_q_index = idx - 1
        st.rerun()
        st.stop()

    if idx < TOTAL_QUESTIONS - 1:
        if nav_r.button("Next →", use_container_width=True, key="play_next"):
            st.session_state.quiz_q_index = idx + 1
            st.rerun()
            st.stop()
    else:
        answered = len(answers)
        label    = (
            "✅ Submit Quiz"
            if answered == TOTAL_QUESTIONS
            else f"⚠️ Submit ({answered}/{TOTAL_QUESTIONS} answered)"
        )
        if nav_r.button(label, use_container_width=True, key="play_submit"):
            _do_submit()
            return

    # ── Quit button ──
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚪 Quit & Submit", use_container_width=True, key="play_quit"):
        _do_submit()
        return

    # ── Tick the clock ──
    time.sleep(1)
    st.rerun()
    st.stop()


# ── Phase: Result ──────────────────────────────────────────────────────────────

def _phase_result():
    score     = _score()
    total     = TOTAL_QUESTIONS
    elapsed   = _elapsed()
    questions = st.session_state.get("quiz_questions", [])
    answers   = st.session_state.get("quiz_answers", {})

    pct         = score / total if total else 0
    grade_emoji = "🏆" if pct >= 0.9 else "🌟" if pct >= 0.7 else "👍" if pct >= 0.5 else "📖"
    grade_label = (
        "Outstanding!" if pct >= 0.9 else
        "Great job!"   if pct >= 0.7 else
        "Good effort!" if pct >= 0.5 else
        "Keep practising!"
    )

    if st.session_state.get("quiz_time_up"):
        st.warning("⏰ Time's up! Your quiz was auto-submitted.")

    topic     = st.session_state.get("quiz_topic", "")
    topic_lbl = TOPIC_META.get(topic, {}).get("label", topic)
    topic_ico = TOPIC_META.get(topic, {}).get("icon", "📚")
    diff      = st.session_state.get("quiz_difficulty", "")

    st.markdown(
        f"""
        <div style='background:#12121a;border:1.5px solid #2a2a3d;
                    border-radius:22px;padding:2.5rem;text-align:center;margin-bottom:1.5rem'>
            <div style='font-size:3rem;margin-bottom:.5rem'>{grade_emoji}</div>
            <div style='font-size:2.8rem;font-weight:900;font-family:monospace;
                        background:linear-gradient(135deg,#7c5cfc,#fc5c7d);
                        -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                        background-clip:text'>
                {score} / {total}
            </div>
            <div style='font-size:1.1rem;color:#7a7a9a;margin:.4rem 0 1.5rem'>
                {grade_label}
            </div>
            <div style='display:flex;gap:2rem;justify-content:center;flex-wrap:wrap'>
                <div>
                    <div style='font-family:monospace;font-size:1.3rem;
                                font-weight:700;color:#7c5cfc'>{int(pct*100)}%</div>
                    <div style='font-size:.75rem;color:#7a7a9a'>Accuracy</div>
                </div>
                <div>
                    <div style='font-family:monospace;font-size:1.3rem;
                                font-weight:700;color:#5cf8b0'>
                        {_fmt_time(min(elapsed, QUIZ_DURATION))}</div>
                    <div style='font-size:.75rem;color:#7a7a9a'>Time taken</div>
                </div>
                <div>
                    <div style='font-family:monospace;font-size:1.3rem;
                                font-weight:700;color:#fcb05c'>{diff}</div>
                    <div style='font-size:.75rem;color:#7a7a9a'>Difficulty</div>
                </div>
                <div>
                    <div style='font-size:1.3rem'>{topic_ico}</div>
                    <div style='font-size:.75rem;color:#7a7a9a'>{topic_lbl}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Answer review ──
    with st.expander("📋 Review All Answers", expanded=False):
        for i, q in enumerate(questions):
            chosen  = answers.get(i, "—")
            correct = q.get("correct_answer", "")
            ok      = chosen == correct
            border_c = "#5cf8b0" if ok else "#fc5c7d"
            expl     = q.get("explanation", "")
            st.markdown(
                f"""
                <div style='background:#12121a;
                            border:1px solid {border_c}30;
                            border-left:4px solid {border_c};
                            border-radius:12px;padding:1rem 1.2rem;margin-bottom:.7rem'>
                    <div style='font-size:.78rem;color:#7a7a9a;font-family:monospace;
                                margin-bottom:.4rem'>
                        Q{i+1} · {q.get("difficulty","")}
                    </div>
                    <p style='font-weight:600;margin:0 0 .5rem;color:#e8e8f0'>
                        {q["question"]}
                    </p>
                    <div style='font-family:monospace;font-size:.85rem;
                                display:flex;gap:1.2rem;flex-wrap:wrap'>
                        <span style='color:#e8e8f0'>Your answer:
                            <b style='color:{"#5cf8b0" if ok else "#fc5c7d"}'>{chosen}</b>
                        </span>
                        <span style='color:#e8e8f0'>Correct:
                            <b style='color:#5cf8b0'>{correct}</b>
                        </span>
                        <span>{"✅" if ok else "❌"}</span>
                    </div>
                    {"<div style='margin-top:.5rem;font-size:.82rem;color:#7a7a9a'>💡 " + expl + "</div>" if expl else ""}
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ── Actions ──
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)

    if c1.button("🔄 Play Again", use_container_width=True, key="res_again"):
        for k in ["quiz_questions", "quiz_answers", "quiz_start_time",
                  "quiz_q_index", "quiz_submitted", "quiz_time_up",
                  "quiz_topic", "quiz_difficulty"]:
            st.session_state.pop(k, None)
        st.session_state.quiz_phase = "select"
        st.rerun()
        st.stop()

    if c2.button("📜 My History", use_container_width=True, key="res_hist"):
        st.session_state.quiz_phase = "history"
        st.rerun()
        st.stop()

    if c3.button("🏆 Leaderboard", use_container_width=True, key="res_lb"):
        st.session_state.quiz_phase = "leaderboard"
        st.rerun()
        st.stop()


# ── Public entry-point ─────────────────────────────────────────────────────────

def render():
    """
    Called by Quiz.page_quiz() when quiz_phase is 'playing' or 'result'.
    Renders only the active phase and nothing else.
    """
    phase = st.session_state.get("quiz_phase", "playing")
    if phase == "playing":
        _phase_playing()
    elif phase == "result":
        _phase_result()