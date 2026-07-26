"""
📊 Analytics — Performance Dashboard
Track scores, weaknesses, study time, and exam readiness.
"""

import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from assets.exam_data import get_all_modules
from backend.server import start_flask_server, get_api_url

start_flask_server()
API_URL = get_api_url()

# Load CSS
css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Theme support
if "theme" not in st.session_state:
    st.session_state.theme = "dark"
is_light = st.session_state.theme == "light"
text_primary = "#1e293b" if is_light else "#e2e8f0"
text_secondary = "#475569" if is_light else "#94a3b8"
text_muted = "#94a3b8" if is_light else "#64748b"
bg_card = "rgba(255,255,255,0.85)" if is_light else "rgba(30,30,70,0.6)"
border_color = "rgba(0,0,0,0.08)" if is_light else "rgba(255,255,255,0.1)"
plot_bg = "rgba(255,255,255,0)" if is_light else "rgba(0,0,0,0)"
plot_grid = "rgba(0,0,0,0.05)" if is_light else "rgba(255,255,255,0.05)"
plot_font_color = "#475569" if is_light else "#94a3b8"

if is_light:
    st.markdown("""<style>
    [data-testid="stAppViewContainer"] { background: #f8fafc !important; }
    [data-testid="stHeader"] { background: #f8fafc !important; }
    [data-testid="stBottomBlockContainer"], [data-testid="stBottom"] { background: #f8fafc !important; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #f1f5f9 0%, #e2e8f0 100%) !important; }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: #1e293b !important; }
    .stMarkdown p, .stCaption p { color: #475569 !important; }
    [data-testid="stMetric"] { background: rgba(255,255,255,0.85) !important; border: 1px solid rgba(0,0,0,0.08) !important; }
    [data-testid="stMetricLabel"] { color: #475569 !important; }
    </style>""", unsafe_allow_html=True)

st.markdown(
    """<h1 style='background: linear-gradient(135deg, #2563eb, #06b6d4);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    font-weight: 800;'>📊 Analytics Dashboard</h1>""",
    unsafe_allow_html=True,
)
st.markdown('<div class="header-line"></div>', unsafe_allow_html=True)
st.caption("Track your progress, identify weak spots, and check your exam readiness! 🎯")

# Fetch data
try:
    data = requests.get(f"{API_URL}/api/analytics", timeout=10).json()
    summary = data.get("summary", {})
    quizzes = data.get("quizzes", [])
    weaknesses = data.get("weaknesses", [])
    progress = data.get("progress", [])
except Exception:
    summary = {"modules_completed": 0, "total_time_mins": 0, "avg_quiz_score": 0,
               "total_quizzes": 0, "total_notes": 0, "total_chats": 0}
    quizzes = []
    weaknesses = []
    progress = []

modules = get_all_modules()

# ---------------------------------------------------------------------------
# Top Stats
# ---------------------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("🎯 Modules Completed", f"{summary.get('modules_completed', 0)}/10")
with col2:
    t_time = summary.get("total_time_mins", 0)
    st.metric("⏱️ Total Study Time", f"{t_time // 60}h {t_time % 60}m")
with col3:
    st.metric("📝 Avg Quiz Score", f"{summary.get('avg_quiz_score', 0)}%")
with col4:
    st.metric("🧪 Quizzes Taken", summary.get("total_quizzes", 0))

st.markdown("")

# ---------------------------------------------------------------------------
# Exam Readiness Score
# ---------------------------------------------------------------------------
completed = summary.get("modules_completed", 0)
avg_score = summary.get("avg_quiz_score", 0)
total_quizzes = summary.get("total_quizzes", 0)

# Composite readiness: 40% module completion + 40% quiz scores + 20% quiz count
readiness = min(100, int(
    (completed / 10 * 40) +
    (avg_score / 100 * 40) +
    (min(total_quizzes, 10) / 10 * 20)
))

readiness_color = "#10b981" if readiness >= 70 else "#f59e0b" if readiness >= 40 else "#f43f5e"
readiness_msg = {
    True: "You're ready to crush this exam! 🏆",
}.get(readiness >= 70, "Keep grinding! Review weak areas and take more quizzes. 💪" if readiness >= 40 else "You're just getting started. Follow the study plan! 📚")

st.markdown(
    f"""<div style='text-align: center; padding: 1.5rem;
    background: linear-gradient(135deg, {readiness_color}10, {readiness_color}05);
    border: 1px solid {readiness_color}30; border-radius: 16px; margin-bottom: 1.5rem;'>
    <div style='color: {text_secondary}; font-weight: 600; text-transform: uppercase; font-size: 0.8rem;'>
    Exam Readiness Score</div>
    <div style='font-size: 3.5rem; font-weight: 800; color: {readiness_color};
    margin: 0.5rem 0;'>{readiness}%</div>
    <div style='color: {text_secondary};'>{readiness_msg}</div></div>""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------------
chart1, chart2 = st.columns(2)

with chart1:
    st.markdown("### 📈 Quiz Score History")
    if quizzes:
        scores = []
        labels = []
        for q in reversed(quizzes[:15]):
            pct = round((q["score"] / q["total"]) * 100, 1) if q["total"] > 0 else 0
            scores.append(pct)
            qtype = "🏆" if q.get("quiz_type") == "final" else f"M{q.get('module_id', '?')}"
            labels.append(f"{qtype} ({q.get('timestamp', '')[:10]})")

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(range(len(scores))),
            y=scores,
            mode="lines+markers",
            line=dict(color="#2563eb", width=3),
            marker=dict(size=8, color="#06b6d4"),
            text=labels,
            hovertemplate="%{text}<br>Score: %{y}%<extra></extra>",
        ))
        fig.add_hline(y=70, line_dash="dash", line_color="#10b981", opacity=0.5,
                      annotation_text="Passing: 70%")
        fig.update_layout(
            plot_bgcolor=plot_bg,
            paper_bgcolor=plot_bg,
            font=dict(color=plot_font_color),
            xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
            yaxis=dict(range=[0, 105], gridcolor=plot_grid, zeroline=False),
            margin=dict(l=20, r=20, t=20, b=20),
            height=300,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Take some quizzes to see your score history! 🧪")

with chart2:
    st.markdown("### ⏱️ Time Spent per Module")
    if progress:
        module_names = []
        times = []
        colors = []
        for p in progress:
            mid = p.get("module_id", 0)
            m = next((m for m in modules if m["id"] == mid), None)
            if m:
                module_names.append(f"D{m['day']}")
                times.append(p.get("time_spent_mins", 0))
                status = p.get("status", "not_started")
                colors.append("#10b981" if status == "completed" else "#f59e0b" if status == "in_progress" else "#64748b")

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=module_names,
            y=times,
            marker_color=colors,
            text=[f"{t_val}m" for t_val in times],
            textposition="outside",
        ))
        fig.update_layout(
            plot_bgcolor=plot_bg,
            paper_bgcolor=plot_bg,
            font=dict(color=plot_font_color),
            xaxis=dict(gridcolor=plot_grid),
            yaxis=dict(gridcolor=plot_grid, zeroline=False),
            margin=dict(l=20, r=20, t=20, b=20),
            height=300,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Start studying to track your time! 📚")

# ---------------------------------------------------------------------------
# Module Progress Grid
# ---------------------------------------------------------------------------
st.markdown("### 📋 Module Progress Grid")
progress_map = {p["module_id"]: p for p in progress}

cols_per_row = 5
for row_start in range(0, len(modules), cols_per_row):
    cols = st.columns(cols_per_row)
    for j, col in enumerate(cols):
        idx = row_start + j
        if idx >= len(modules):
            break
        m = modules[idx]
        prog = progress_map.get(m["id"], {})
        status = prog.get("status", "not_started")
        status_color = {"completed": "#10b981", "in_progress": "#f59e0b", "not_started": "#64748b"}.get(status, "#64748b")
        status_icon = {"completed": "✅", "in_progress": "🟡", "not_started": "⬜"}.get(status, "⬜")

        with col:
            st.markdown(
                f"""<div style='text-align: center; padding: 0.8rem;
                background: {bg_card}; border: 1px solid {status_color}30;
                border-radius: 12px;'>
                <div style='font-size: 1.5rem;'>{m['icon']}</div>
                <div style='font-weight: 600; color: {text_primary}; font-size: 0.85rem;'>Day {m['day']}</div>
                <div style='color: {status_color}; font-size: 0.75rem;'>{status_icon} {status.replace('_', ' ').title()}</div>
                </div>""",
                unsafe_allow_html=True,
            )

# ---------------------------------------------------------------------------
# Weakness Heatmap
# ---------------------------------------------------------------------------
st.markdown("")
st.markdown("### 🔥 Weakness Areas")

if weaknesses:
    for w in weaknesses[:10]:
        w_score = w.get("weakness_score", 0.5)
        bar_width = int(w_score * 100)
        bar_color = "#f43f5e" if w_score < 0.4 else "#f59e0b" if w_score < 0.7 else "#10b981"

        st.markdown(
            f"""<div style='background: {bg_card}; border-radius: 8px; padding: 0.6rem 1rem;
            margin: 0.3rem 0; border: 1px solid {border_color};'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <span style='color: {text_primary}; font-weight: 500;'>{w.get('topic', 'Unknown')}</span>
                <span style='color: {bar_color}; font-weight: 700; font-size: 0.85rem;'>
                    {'Weak' if w_score < 0.4 else 'Needs Work' if w_score < 0.7 else 'Strong'}</span>
            </div>
            <div style='background: {border_color}; border-radius: 4px; margin-top: 0.4rem; height: 6px;'>
                <div style='background: {bar_color}; width: {bar_width}%; height: 100%; border-radius: 4px;'></div>
            </div></div>""",
            unsafe_allow_html=True,
        )
else:
    st.info("Take quizzes to identify your weak areas! 🧪")
