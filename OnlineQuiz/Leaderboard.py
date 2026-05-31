# Leaderboard.py — Global leaderboard, filterable by topic & difficulty.

import streamlit as st
from Database import get_leaderboard

TOPIC_META = {
    "ai":              {"icon": "🤖", "label": "Artificial Intelligence"},
    "python":          {"icon": "🐍", "label": "Python"},
    "java":            {"icon": "☕", "label": "Java"},
    "web_development": {"icon": "🌐", "label": "Web Development"},
    "cpp":             {"icon": "⚙️",  "label": "C++"},
    "ethical_hacking": {"icon": "🛡️",  "label": "Ethical Hacking"},
}

DIFFICULTIES   = ["Easy", "Medium", "Hard"]
TOTAL_QUESTIONS = 15


def _fmt_time(seconds: int) -> str:
    m, s = divmod(max(seconds, 0), 60)
    return f"{m:02d}:{s:02d}"


def _render_table(rows: list, logged_user: str):
    if not rows:
        st.info("No scores yet for this filter — be the first!")
        return

    # Podium top-3
    podium  = rows[:3]
    medals  = ["🥇", "🥈", "🥉"]
    pcols   = st.columns(len(podium))
    for col, row, medal in zip(pcols, podium, medals):
        label = TOPIC_META.get(row["topic"], {}).get("label", row["topic"])
        col.markdown(
            f"""<div style='background:#12121a;border:1.5px solid #2a2a3d;
                border-radius:18px;padding:1.4rem;text-align:center'>
                <div style='font-size:2rem'>{medal}</div>
                <div style='font-weight:800;font-size:1rem;margin:.3rem 0;color:#e8e8f0'>{row['username']}</div>
                <div style='font-family:monospace;font-size:1.5rem;font-weight:700;color:#7c5cfc'>
                    {row['score']}/{row['total']}</div>
                <div style='font-size:.75rem;color:#7a7a9a;margin-top:.3rem'>
                    {label} · {row['difficulty']}</div>
                <div style='font-size:.72rem;color:#7a7a9a;font-family:monospace'>
                    ⏱ {_fmt_time(row['time_taken_s'])}</div>
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Header row
    st.markdown(
        """<div style='display:grid;grid-template-columns:40px 1fr 1.2fr 1fr 60px 80px 80px;
            gap:.6rem;padding:.4rem .8rem;font-family:monospace;
            font-size:.72rem;color:#7a7a9a;text-transform:uppercase'>
            <span>#</span><span>Player</span><span>Topic</span>
            <span>Difficulty</span><span>Score</span><span>Time</span><span>Date</span>
        </div>""",
        unsafe_allow_html=True,
    )

    rank_colors = {1: "#ffd700", 2: "#c0c0c0", 3: "#cd7f32"}
    diff_colors = {"Easy": "#5cf8b0", "Medium": "#fcb05c", "Hard": "#fc5c7d"}

    for row in rows:
        label    = TOPIC_META.get(row["topic"], {}).get("label", row["topic"])
        icon     = TOPIC_META.get(row["topic"], {}).get("icon", "📚")
        diff_c   = diff_colors.get(row["difficulty"], "#e8e8f0")
        pct      = row["score"] / row["total"]
        score_c  = "#5cf8b0" if pct >= 0.7 else "#fcb05c" if pct >= 0.5 else "#fc5c7d"
        date_str = (row["completed_at"].strftime("%d %b")
                    if hasattr(row["completed_at"], "strftime")
                    else str(row["completed_at"])[:10])
        is_me    = row["username"] == logged_user
        border   = "#7c5cfc" if is_me else "#2a2a3d"
        bg       = "rgba(124,92,252,.08)" if is_me else "#1c1c2a"
        rank_c   = rank_colors.get(row["rank"], "#7a7a9a")

        st.markdown(
            f"""<div style='display:grid;grid-template-columns:40px 1fr 1.2fr 1fr 60px 80px 80px;
                gap:.6rem;align-items:center;padding:.7rem .8rem;
                background:{bg};border:1px solid {border};
                border-radius:12px;margin-bottom:.4rem'>
                <span style='font-family:monospace;font-weight:700;color:{rank_c};text-align:center'>
                    {row['rank']}</span>
                <span style='font-weight:{"800" if is_me else "500"};color:#e8e8f0'>
                    {row['username']}{"  ← you" if is_me else ""}</span>
                <span style='font-size:.82rem;color:#e8e8f0'>{icon} {label}</span>
                <span style='color:{diff_c};font-family:monospace;font-size:.82rem'>{row['difficulty']}</span>
                <span style='color:{score_c};font-family:monospace;font-weight:700;text-align:right'>
                    {row['score']}/{row['total']}</span>
                <span style='font-family:monospace;font-size:.78rem;color:#7a7a9a;text-align:right'>
                    {_fmt_time(row['time_taken_s'])}</span>
                <span style='font-size:.75rem;color:#7a7a9a;font-family:monospace;text-align:right'>
                    {date_str}</span>
            </div>""",
            unsafe_allow_html=True,
        )


def page_leaderboard(back_phase: str = "select"):
    logged_user = st.session_state.get("logged_in_user", "")

    st.markdown("<h2>🏆 Global Leaderboard</h2>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color:#7a7a9a;margin-top:-.6rem'>"
        "Rankings by topic and difficulty.</p>",
        unsafe_allow_html=True,
    )

    all_rows   = get_leaderboard(200)
    topic_keys = list(TOPIC_META.keys())
    t_labels   = [f"{TOPIC_META[k]['icon']} {TOPIC_META[k]['label']}" for k in topic_keys]
    t_tabs     = st.tabs(["🌐 All Topics"] + t_labels)

    for t_idx, t_tab in enumerate(t_tabs):
        with t_tab:
            topic_rows = (
                all_rows if t_idx == 0
                else [r for r in all_rows if r["topic"] == topic_keys[t_idx - 1]]
            )
            d_tabs = st.tabs(["📊 All", "🟢 Easy", "🟡 Medium", "🔴 Hard"])
            for d_idx, d_tab in enumerate(d_tabs):
                with d_tab:
                    if d_idx == 0:
                        display = topic_rows
                    else:
                        chosen  = DIFFICULTIES[d_idx - 1]
                        display = [r for r in topic_rows if r["difficulty"] == chosen]

                    ranked = []
                    for rank_i, r in enumerate(display[:20], start=1):
                        r2 = dict(r)
                        r2["rank"] = rank_i
                        ranked.append(r2)

                    _render_table(ranked, logged_user)

    st.divider()
    c1, c2 = st.columns(2)
    if c1.button("← Back", use_container_width=True, key="lb_back"):
        st.session_state.quiz_phase = back_phase
        st.rerun()
    if c2.button("📜 My History", use_container_width=True, key="lb_history"):
        st.session_state.quiz_phase = "history"
        st.rerun()