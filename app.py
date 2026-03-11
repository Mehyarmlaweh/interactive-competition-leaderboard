import streamlit as st
import pandas as pd
from database import (
    init_db, submit_score, get_leaderboard,
    validate_token, register_student, get_submission_history,
    get_total_students, get_total_submissions,
    bulk_register_students, get_all_students, reset_leaderboard
)
from evaluator import evaluate_submission
from streamlit_autorefresh import st_autorefresh

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Computer Vision Competition · Leaderboard",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,500;0,9..40,700;1,9..40,300&display=swap" rel="stylesheet">

<style>
/* ── Reset & Base ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #1e1b4b !important;
    border-right: 1px solid #312e81;
}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] div {
    color: #c7d2fe !important;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #ffffff !important;
}
section[data-testid="stSidebar"] .stRadio label {
    color: #a5b4fc !important;
    font-size: 0.92rem !important;
}
section[data-testid="stSidebar"] hr {
    border-color: #312e81 !important;
}
section[data-testid="stSidebar"] .stButton button {
    background: transparent !important;
    border: 1.5px solid #6366f1 !important;
    color: #a5b4fc !important;
    border-radius: 10px !important;
    font-size: 0.85rem !important;
    transition: all 0.2s !important;
}
section[data-testid="stSidebar"] .stButton button:hover {
    background: #6366f1 !important;
    color: white !important;
}
.sidebar-user-card {
    background: rgba(99,102,241,0.15);
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 14px;
    padding: 0.9rem 1rem;
    margin: 0.5rem 0 1rem;
}
.sidebar-user-name {
    font-size: 1rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 0.35rem;
}
.sidebar-user-token {
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem;
    color: #818cf8;
    background: rgba(99,102,241,0.2);
    padding: 0.2rem 0.5rem;
    border-radius: 6px;
    display: inline-block;
    letter-spacing: 0.05em;
}

/* Main background */
.stApp {
    background: #f0f4ff;
}

/* ── Hero header ── */
.hero {
    text-align: center;
    padding: 2.5rem 0 1.5rem;
}
.hero-eyebrow {
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #6366f1;
    margin-bottom: 0.5rem;
}
.hero-title {
    font-family: 'DM Sans', sans-serif;
    font-size: clamp(2.2rem, 5vw, 3.4rem);
    font-weight: 700;
    color: #0f172a;
    line-height: 1.1;
    margin: 0;
}
.hero-title span {
    color: #6366f1;
}
.hero-sub {
    font-size: 1rem;
    color: #64748b;
    margin-top: 0.6rem;
    font-weight: 300;
}

/* ── Stats bar ── */
.stats-bar {
    display: flex;
    gap: 1rem;
    justify-content: center;
    margin: 1.5rem 0 2rem;
    flex-wrap: wrap;
}
.stat-pill {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 100px;
    padding: 0.45rem 1.2rem;
    font-family: 'Space Mono', monospace;
    font-size: 0.82rem;
    color: #334155;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.stat-pill b { color: #6366f1; }

/* ── Podium ── */
.podium-wrap {
    display: flex;
    align-items: flex-end;
    justify-content: center;
    gap: 1.2rem;
    margin: 0 auto 3rem;
    max-width: 820px;
}
.podium-block {
    flex: 1;
    border-radius: 20px;
    padding: 1.6rem 1rem 1.2rem;
    text-align: center;
    position: relative;
    transition: transform 0.2s;
}
.podium-block:hover { transform: translateY(-4px); }

.podium-1 {
    background: linear-gradient(160deg, #1e1b4b 0%, #312e81 60%, #4338ca 100%);
    color: white;
    box-shadow: 0 20px 60px rgba(99,102,241,0.35);
    padding-top: 2rem;
    min-height: 220px;
}
.podium-2 {
    background: white;
    border: 1.5px solid #e2e8f0;
    color: #0f172a;
    box-shadow: 0 8px 30px rgba(0,0,0,0.07);
    min-height: 180px;
}
.podium-3 {
    background: white;
    border: 1.5px solid #e2e8f0;
    color: #0f172a;
    box-shadow: 0 8px 30px rgba(0,0,0,0.07);
    min-height: 160px;
}
.podium-medal {
    font-size: 2.2rem;
    line-height: 1;
    margin-bottom: 0.4rem;
}
.podium-rank {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    opacity: 0.6;
    margin-bottom: 0.5rem;
}
.podium-name {
    font-size: 1.25rem;
    font-weight: 700;
    line-height: 1.2;
    margin-bottom: 0.5rem;
}
.podium-score {
    font-family: 'Space Mono', monospace;
    font-size: 1.6rem;
    font-weight: 700;
}
.podium-1 .podium-score { color: #a5b4fc; }
.podium-1 .podium-name { color: white; }
.podium-badge {
    display: inline-block;
    background: rgba(255,255,255,0.15);
    border-radius: 100px;
    padding: 0.15rem 0.6rem;
    font-size: 0.7rem;
    font-family: 'Space Mono', monospace;
    margin-top: 0.4rem;
    color: #c7d2fe;
}

/* ── Full ranking table ── */
.rank-table-wrap {
    background: white;
    border-radius: 20px;
    border: 1px solid #e2e8f0;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(0,0,0,0.05);
    margin-top: 0.5rem;
}
.rank-header {
    display: grid;
    grid-template-columns: 60px 1fr 160px 100px 120px;
    padding: 0.9rem 1.5rem;
    background: #f8fafc;
    border-bottom: 1px solid #e2e8f0;
    font-family: 'Space Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #94a3b8;
}
.rank-row {
    display: grid;
    grid-template-columns: 60px 1fr 160px 100px 120px;
    padding: 1rem 1.5rem;
    border-bottom: 1px solid #f1f5f9;
    align-items: center;
    transition: background 0.15s;
}
.rank-row:last-child { border-bottom: none; }
.rank-row:hover { background: #f8faff; }
.rank-row.rank-top1 {
    background: linear-gradient(90deg, #eef2ff 0%, #f8faff 100%);
    border-left: 3px solid #6366f1;
}
.rank-num {
    font-family: 'Space Mono', monospace;
    font-size: 0.85rem;
    font-weight: 700;
    color: #94a3b8;
}
.rank-num.top3 { color: #6366f1; }
.rank-student {
    font-weight: 500;
    color: #0f172a;
    font-size: 0.95rem;
}
.rank-score {
    font-family: 'Space Mono', monospace;
    font-size: 0.9rem;
    font-weight: 700;
    color: #4338ca;
}
.rank-attempts {
    font-family: 'Space Mono', monospace;
    font-size: 0.78rem;
    color: #94a3b8;
}
.rank-time {
    font-size: 0.78rem;
    color: #94a3b8;
}
.delta-badge {
    display: inline-block;
    padding: 0.12rem 0.45rem;
    border-radius: 6px;
    font-family: 'Space Mono', monospace;
    font-size: 0.68rem;
    background: #ecfdf5;
    color: #059669;
    margin-left: 0.4rem;
}
.score-bar-bg {
    background: #f1f5f9;
    border-radius: 4px;
    height: 5px;
    margin-top: 4px;
    overflow: hidden;
    width: 100%;
}
.score-bar-fill {
    height: 5px;
    border-radius: 4px;
    background: linear-gradient(90deg, #6366f1, #818cf8);
}

/* ── Full ranking table ── */
.lb-table-wrap {
    background: white;
    border-radius: 20px;
    border: 1px solid #e2e8f0;
    overflow: hidden;
    box-shadow: 0 4px 24px rgba(99,102,241,0.08);
    margin-top: 0.5rem;
}
.lb-table {
    width: 100%;
    border-collapse: collapse;
}
.lb-table thead tr {
    background: linear-gradient(135deg, #1e1b4b, #4338ca);
}
.lb-table thead th {
    padding: 1rem 1.2rem;
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #a5b4fc;
    font-weight: 400;
}
.lb-table tbody tr {
    border-bottom: 1px solid #f1f5f9;
    transition: background 0.15s;
}
.lb-table tbody tr:hover { background: #f5f3ff !important; }
.lb-table tbody tr:last-child { border-bottom: none; }
.lb-table td { padding: 0.85rem 1.2rem; }
.lb-tr-first { background: linear-gradient(90deg,#eef2ff,#f8f7ff); border-left: 4px solid #6366f1 !important; }
.lb-tr-top { background: #fafafa; }
.lb-rank { text-align: center; font-size: 1.15rem; }
.lb-name { font-size: 0.95rem; color: #0f172a; }
.lb-name-bold { font-weight: 700; }
.lb-name-semi { font-weight: 600; }
.lb-bar-bg { margin-top: 5px; height: 4px; background: #e2e8f0; border-radius: 4px; overflow: hidden; }
.lb-bar-fill { height: 4px; background: linear-gradient(90deg,#6366f1,#a5b4fc); border-radius: 4px; }
.lb-score { font-family: 'Space Mono', monospace; font-size: 0.95rem; font-weight: 700; }
.lb-score-first { color: #4338ca; }
.lb-score-top { color: #6366f1; }
.lb-score-rest { color: #374151; }
.lb-attempts-pill {
    background: #f1f5f9;
    color: #64748b;
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    padding: 0.2rem 0.6rem;
    border-radius: 20px;
    display: inline-block;
}
.lb-time { font-size: 0.8rem; color: #94a3b8; }

/* ── Submit page ── */
.submit-wrap {
    max-width: 700px;
    margin: 0 auto;
    padding: 2rem 0;
}
.token-display {
    font-family: 'Space Mono', monospace;
    font-size: 1.3rem;
    letter-spacing: 0.12em;
    background: #f1f5f9;
    border: 1.5px solid #e2e8f0;
    border-radius: 12px;
    padding: 0.9rem 1.4rem;
    color: #4338ca;
    text-align: center;
    margin: 0.5rem 0 1rem;
}
.info-card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 1.3rem 1.5rem;
    margin-bottom: 1.2rem;
}
.info-card h4 {
    margin: 0 0 0.7rem;
    font-size: 0.9rem;
    font-weight: 600;
    color: #475569;
    font-family: 'Space Mono', monospace;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* ── Section title ── */
.section-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #0f172a;
    font-family: 'Space Mono', monospace;
    letter-spacing: 0.02em;
    margin: 2rem 0 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.section-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #e2e8f0;
    margin-left: 0.5rem;
}

/* History chart area */
.history-row {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    padding: 0.5rem 0;
    border-bottom: 1px solid #f1f5f9;
    font-size: 0.85rem;
}
.history-attempt {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    color: #94a3b8;
    min-width: 30px;
}
.history-score {
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    color: #4338ca;
    min-width: 90px;
}
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
if "authenticated_token" not in st.session_state:
    st.session_state.authenticated_token = None
if "authenticated_name" not in st.session_state:
    st.session_state.authenticated_name = None

# ── Sidebar navigation ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🏆 Computer Vision Competition")
    st.markdown("---")
    page = st.radio(
        "Navigate",
        ["🏅 Leaderboard", "📤 Submit", "🔑 Admin"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    if st.session_state.authenticated_token:
        st.markdown(f"""
        <div class="sidebar-user-card">
            <div style="font-size:0.68rem;letter-spacing:0.12em;text-transform:uppercase;color:#818cf8;margin-bottom:0.4rem;">Signed in as</div>
            <div class="sidebar-user-name">{st.session_state.authenticated_name}</div>
            <div class="sidebar-user-token">{st.session_state.authenticated_token}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("↩ Sign out", use_container_width=True):
            st.session_state.authenticated_token = None
            st.session_state.authenticated_name = None
            st.rerun()
    else:
        st.markdown("""
        <div style="background:rgba(99,102,241,0.08);border:1px dashed rgba(99,102,241,0.3);border-radius:12px;padding:0.8rem 1rem;margin:0.5rem 0;">
            <div style="font-size:0.78rem;color:#818cf8;">Not signed in</div>
            <div style="font-size:0.72rem;color:#6366f1;margin-top:0.2rem;">Go to Submit to authenticate</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div style="font-size:0.68rem;color:#4338ca;letter-spacing:0.05em;">⟳ Leaderboard refreshes every 2 s</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: LEADERBOARD
# ══════════════════════════════════════════════════════════════════════════════
if page == "🏅 Leaderboard":
    st_autorefresh(interval=2000, key="lb_refresh")

    total_students = get_total_students()
    total_submissions = get_total_submissions()
    df = get_leaderboard()

    # Hero
    st.markdown("""
    <div class="hero">
        <div class="hero-eyebrow">Live · ROC-AUC</div>
        <div class="hero-title">Computer Vision Competition<br><span>Leaderboard</span></div>
        <div class="hero-sub">Best score per student · auto-refreshes every 2 s</div>
    </div>
    """, unsafe_allow_html=True)

    # Stats bar
    n_submitted = len(df)
    best_score = f"{df['score'].iloc[0]:.6f}" if len(df) > 0 else "—"
    st.markdown(f"""
    <div class="stats-bar">
        <div class="stat-pill">👥 <b>{total_students}</b> students registered</div>
        <div class="stat-pill">📤 <b>{total_submissions}</b> total submissions</div>
        <div class="stat-pill">🎯 <b>{n_submitted}</b> students on board</div>
        <div class="stat-pill">🏆 Best: <b>{best_score}</b></div>
    </div>
    """, unsafe_allow_html=True)

    if len(df) == 0:
        st.info("No submissions yet. Be the first to submit!")
        st.stop()

    # ── Podium (top 3) ──────────────────────────────────────────────────────
    top3 = df.head(3)
    best = df['score'].iloc[0] if len(df) > 0 else 1.0

    def podium_html(row, css_class, medal, rank_label):
        return f"""
        <div class="podium-block {css_class}">
            <div class="podium-medal">{medal}</div>
            <div class="podium-rank">{rank_label}</div>
            <div class="podium-name">{row['name']}</div>
            <div class="podium-score">{row['score']:.6f}</div>
        </div>"""

    # Build podium HTML: 2nd | 1st | 3rd
    podium_parts = []
    if len(top3) >= 2:
        podium_parts.append(podium_html(top3.iloc[1], "podium-block podium-2", "🥈", "2nd Place"))
    if len(top3) >= 1:
        podium_parts.append(podium_html(top3.iloc[0], "podium-block podium-1", "🥇", "1st Place"))
    if len(top3) >= 3:
        podium_parts.append(podium_html(top3.iloc[2], "podium-block podium-3", "🥉", "3rd Place"))

    st.markdown(
        f'<div class="podium-wrap">{"".join(podium_parts)}</div>',
        unsafe_allow_html=True
    )

    # ── Full ranking table ──────────────────────────────────────────────────
    st.markdown('<div class="section-title">Full Ranking</div>', unsafe_allow_html=True)

    medals = {1: "🥇", 2: "🥈", 3: "🥉"}
    best = df['score'].iloc[0] if len(df) > 0 else 1.0
    score_min = max(df['score'].min() - 0.02, 0.0) if len(df) > 0 else 0.5

    rows_html = ""
    for i, row in df.reset_index(drop=True).iterrows():
        rank = i + 1
        medal = medals.get(rank, f"#{rank}")
        last_sub = str(row['last_submission'])[:16] if pd.notnull(row['last_submission']) else "—"
        bar_pct = int(((row['score'] - score_min) / max(best - score_min, 0.001)) * 100)
        bar_pct = max(10, min(bar_pct, 100))

        if rank == 1:
            tr_class = "lb-tr-first"
            score_class = "lb-score lb-score-first"
            name_class = "lb-name lb-name-bold"
        elif rank <= 3:
            tr_class = "lb-tr-top"
            score_class = "lb-score lb-score-top"
            name_class = "lb-name lb-name-semi"
        else:
            tr_class = ""
            score_class = "lb-score lb-score-rest"
            name_class = "lb-name"

        rows_html += f"""
        <tr class="{tr_class}">
            <td class="lb-rank">{medal}</td>
            <td>
                <div class="{name_class}">{row['name']}</div>
                <div class="lb-bar-bg"><div class="lb-bar-fill" style="width:{bar_pct}%"></div></div>
            </td>
            <td><span class="{score_class}">{row['score']:.6f}</span></td>
            <td style="text-align:center"><span class="lb-attempts-pill">{int(row['attempts'])}×</span></td>
            <td><span class="lb-time">{last_sub}</span></td>
        </tr>"""

    st.markdown(f"""
    <div class="lb-table-wrap">
        <table class="lb-table">
            <thead>
                <tr>
                    <th style="text-align:center;width:60px;">Rank</th>
                    <th style="text-align:left;">Student</th>
                    <th style="text-align:left;">ROC-AUC</th>
                    <th style="text-align:center;">Attempts</th>
                    <th style="text-align:left;">Last Submit</th>
                </tr>
            </thead>
            <tbody>{rows_html}</tbody>
        </table>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: SUBMIT
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📤 Submit":

    st.markdown("""
    <div class="hero">
        <div class="hero-eyebrow">Step 1 — Authenticate · Step 2 — Upload</div>
        <div class="hero-title">Submit <span>Predictions</span></div>
    </div>
    """, unsafe_allow_html=True)

    # ── Token authentication ────────────────────────────────────────────────
    if not st.session_state.authenticated_token:
        st.markdown('<div class="submit-wrap">', unsafe_allow_html=True)
        st.markdown('<div class="info-card"><h4>🔑 Enter your token</h4>', unsafe_allow_html=True)
        st.markdown("Your instructor gave you a unique token. Enter it below to authenticate.", unsafe_allow_html=True)

        col_t, col_b = st.columns([3, 1])
        with col_t:
            token_input = st.text_input(
                "Token",
                placeholder="e.g. ABC123XYZ789",
                label_visibility="collapsed"
            ).strip().upper()
        with col_b:
            verify_btn = st.button("Verify →", use_container_width=True, type="primary")

        if verify_btn or token_input:
            student = validate_token(token_input)
            if student:
                st.session_state.authenticated_token = student["token"]
                st.session_state.authenticated_name = student["display_name"]
                st.success(f"✅ Welcome, **{student['display_name']}**!")
                st.rerun()
            elif token_input:
                st.error("❌ Invalid token. Please check with your instructor.")

        st.markdown('</div></div>', unsafe_allow_html=True)
        st.stop()

    # ── Authenticated ───────────────────────────────────────────────────────
    name = st.session_state.authenticated_name
    token = st.session_state.authenticated_token

    st.markdown(f"""
    <div class="submit-wrap">
        <div class="info-card">
            <h4>✅ Authenticated</h4>
            <div style="display:flex;align-items:center;gap:1rem;">
                <span style="font-size:1.05rem;font-weight:600;color:#0f172a;">{name}</span>
                <span style="font-family:'Space Mono',monospace;font-size:0.8rem;color:#6366f1;background:#eef2ff;padding:0.2rem 0.6rem;border-radius:8px;">{token}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Submission history
    history = get_submission_history(token)
    if len(history) > 0:
        best_so_far = history['score'].max()
        st.markdown(f"""
        <div class="info-card">
            <h4>📊 Your submissions ({len(history)} total)</h4>
            <div style="margin-bottom:0.5rem;color:#475569;font-size:0.88rem;">Best score: <b style="color:#4338ca;font-family:'Space Mono',monospace">{best_so_far:.6f}</b></div>
        """, unsafe_allow_html=True)

        for _, hrow in history.iterrows():
            is_best = hrow['score'] == best_so_far
            best_label = '<span style="background:#ecfdf5;color:#059669;font-size:0.68rem;padding:0.1rem 0.4rem;border-radius:6px;margin-left:0.4rem;font-family:Space Mono,monospace">BEST</span>' if is_best else ''
            st.markdown(f"""
            <div class="history-row">
                <span class="history-attempt">#{int(hrow['attempt'])}</span>
                <span class="history-score">{hrow['score']:.6f}</span>
                {best_label}
                <span style="color:#94a3b8;font-size:0.75rem;margin-left:auto">{str(hrow['submitted_at'])[:16]}</span>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Upload
    st.markdown('<div class="section-title">Upload your predictions</div>', unsafe_allow_html=True)

    col_upload, col_fmt = st.columns([1.4, 1])

    with col_upload:
        uploaded_file = st.file_uploader(
            "CSV file with columns: id, prediction",
            type=["csv"],
            label_visibility="visible"
        )

        if uploaded_file:
            if st.button("🚀 Submit predictions", type="primary", use_container_width=True):
                with st.spinner("Evaluating…"):
                    try:
                        score = evaluate_submission(uploaded_file)
                        submit_score(token, score)
                        prev_best = get_submission_history(token)['score'].max()
                        improvement = score >= prev_best
                        if improvement and len(get_submission_history(token)) > 1:
                            st.balloons()
                        st.success(f"✅ Submitted! ROC-AUC = **{score:.6f}**")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ {e}")

    with col_fmt:
        st.markdown('<div class="info-card"><h4>Format guide</h4>', unsafe_allow_html=True)
        st.code("id,prediction\n1,0.91\n2,0.14\n3,0.72\n4,0.33\n5,0.85")
        st.markdown('<p style="font-size:0.8rem;color:#64748b;margin-top:0.5rem;">Use <b>probabilities</b> between 0 and 1, not hard labels.</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: ADMIN
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔑 Admin":

    st.markdown("""
    <div class="hero">
        <div class="hero-eyebrow">Instructor only</div>
        <div class="hero-title">Admin <span>Panel</span></div>
    </div>
    """, unsafe_allow_html=True)

    ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "admin123")

    if "admin_auth" not in st.session_state:
        st.session_state.admin_auth = False

    if not st.session_state.admin_auth:
        pwd = st.text_input("Admin password", type="password")
        if st.button("Login", type="primary"):
            if pwd == ADMIN_PASSWORD:
                st.session_state.admin_auth = True
                st.rerun()
            else:
                st.error("Wrong password.")
        st.stop()

    # ── Registered students ─────────────────────────────────────────────────
    st.markdown('<div class="section-title">Registered Students</div>', unsafe_allow_html=True)
    students_df = get_all_students()
    if len(students_df) > 0:
        st.dataframe(students_df, use_container_width=True)
        csv_export = students_df.to_csv(index=False)
        st.download_button(
            "⬇️ Download token list (CSV)",
            csv_export,
            "student_tokens.csv",
            "text/csv"
        )
    else:
        st.info("No students registered yet.")

    # ── Register new students ───────────────────────────────────────────────
    st.markdown('<div class="section-title">Register Students</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Single student", "Bulk (paste list)"])

    with tab1:
        col_n, col_b = st.columns([3, 1])
        with col_n:
            single_name = st.text_input("Student name", key="single_name")
        with col_b:
            if st.button("Register", type="primary", use_container_width=True, key="reg_single"):
                if single_name.strip():
                    tok = register_student(single_name.strip())
                    st.success(f"Registered **{single_name}** → token: `{tok}`")
                    st.rerun()

    with tab2:
        bulk_text = st.text_area(
            "One name per line",
            placeholder="Alice\nBob\nCharlie\n...",
            height=150
        )
        if st.button("Register all", type="primary", key="reg_bulk"):
            names = [n.strip() for n in bulk_text.splitlines() if n.strip()]
            if names:
                results = bulk_register_students(names)
                result_df = pd.DataFrame(results)
                st.success(f"Registered {len(results)} students!")
                st.dataframe(result_df, use_container_width=True)
                st.download_button(
                    "⬇️ Download tokens",
                    result_df.to_csv(index=False),
                    "new_tokens.csv",
                    "text/csv"
                )
                st.rerun()

    # ── Danger zone ─────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">⚠️ Danger Zone</div>', unsafe_allow_html=True)
    with st.expander("Reset all submissions"):
        st.warning("This will delete ALL submission scores. Student tokens will remain valid.")
        if st.button("🗑️ Reset leaderboard", type="secondary"):
            reset_leaderboard()
            st.success("Leaderboard cleared.")
            st.rerun()