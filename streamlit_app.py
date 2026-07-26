"""
🚀 DP-700 FabricPrep — AI-Powered Exam Prep App
Main entry point: Dashboard with stats, quick actions, and progress overview.
"""

import streamlit as st
import requests
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------------------
# Page config (must be first Streamlit command)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="FabricPrep — DP-700 Exam Prep",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Load custom CSS
# ---------------------------------------------------------------------------
css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Theme state
# ---------------------------------------------------------------------------
if "theme" not in st.session_state:
    st.session_state.theme = "dark"


def get_theme_colors():
    """Return color variables based on current theme."""
    is_light = st.session_state.theme == "light"
    return {
        "text_primary": "#1e293b" if is_light else "#e2e8f0",
        "text_secondary": "#475569" if is_light else "#94a3b8",
        "text_muted": "#94a3b8" if is_light else "#64748b",
        "bg_card": "rgba(255,255,255,0.85)" if is_light else "rgba(30,30,70,0.6)",
        "border": "rgba(0,0,0,0.08)" if is_light else "rgba(255,255,255,0.1)",
        "bg_page": "#f8fafc" if is_light else "#0f0f23",
        "bg_sidebar": "linear-gradient(180deg, #f1f5f9 0%, #e2e8f0 100%)" if is_light else "linear-gradient(180deg, #12122e 0%, #0f0f23 100%)",
        "border_sidebar": "rgba(0,0,0,0.08)" if is_light else "rgba(255,255,255,0.1)",
        "accent_card_bg": "rgba(37,99,235,0.06)" if is_light else "rgba(37,99,235,0.15)",
        "accent_cyan_bg": "rgba(8,145,178,0.06)" if is_light else "rgba(6,182,212,0.15)",
        "accent_green_bg": "rgba(5,150,105,0.06)" if is_light else "rgba(16,185,129,0.15)",
        "accent_amber_bg": "rgba(217,119,6,0.06)" if is_light else "rgba(245,158,11,0.15)",
        "accent_rose_bg": "rgba(225,29,72,0.06)" if is_light else "rgba(244,63,94,0.15)",
    }


def inject_theme_css():
    """Inject CSS to override Streamlit's base theme based on toggle."""
    is_light = st.session_state.theme == "light"
    if is_light:
        st.markdown("""<style>
        [data-testid="stAppViewContainer"] { background: #f8fafc !important; }
        [data-testid="stSidebar"] { background: linear-gradient(180deg, #f1f5f9 0%, #e2e8f0 100%) !important; border-right: 1px solid rgba(0,0,0,0.08) !important; }
        [data-testid="stSidebar"] .stMarkdown h1,
        [data-testid="stSidebar"] .stMarkdown h3 { color: #1e293b !important; -webkit-text-fill-color: #1e293b !important; background: none !important; }
        [data-testid="stSidebar"] .stMarkdown p,
        [data-testid="stSidebar"] .stCaption p { color: #475569 !important; }
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: #1e293b !important; }
        .stMarkdown p, .stCaption p { color: #475569 !important; }
        [data-testid="stMetric"] { background: rgba(255,255,255,0.85) !important; border: 1px solid rgba(0,0,0,0.08) !important; }
        [data-testid="stMetricLabel"] { color: #475569 !important; }
        [data-testid="stExpander"] { background: rgba(255,255,255,0.85) !important; border: 1px solid rgba(0,0,0,0.08) !important; }
        [data-testid="stChatInput"] textarea { background: #f1f5f9 !important; border: 1px solid rgba(0,0,0,0.08) !important; color: #1e293b !important; }
        .stTextInput input, .stTextArea textarea { background: #f1f5f9 !important; border: 1px solid rgba(0,0,0,0.08) !important; color: #1e293b !important; }
        .stTabs [data-baseweb="tab-list"] { background: #f1f5f9 !important; }
        .stTabs [data-baseweb="tab"] { color: #475569 !important; }
        .stProgress > div { background: #e2e8f0 !important; }
        .stRadio label, .stCheckbox label { color: #1e293b !important; }
        pre { background: #f1f5f9 !important; border: 1px solid rgba(0,0,0,0.08) !important; }
        hr { border-color: rgba(0,0,0,0.08) !important; }
        ::-webkit-scrollbar-track { background: #f1f5f9 !important; }
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stMarkdown {
            background: #ffffff !important; border: 1px solid rgba(0,0,0,0.08) !important; color: #1e293b !important;
        }
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stMarkdown p,
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stMarkdown li,
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stMarkdown span { color: #1e293b !important; }
        </style>""", unsafe_allow_html=True)


inject_theme_css()
t = get_theme_colors()

# ---------------------------------------------------------------------------
# Start Flask backend
# ---------------------------------------------------------------------------
from backend.server import start_flask_server, get_api_url

start_flask_server()
API_URL = get_api_url()

# ---------------------------------------------------------------------------
# Session state initialization
# ---------------------------------------------------------------------------
if "current_module" not in st.session_state:
    st.session_state.current_module = 1
if "model_key" not in st.session_state:
    st.session_state.model_key = "gemini"

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("# 🚀 FabricPrep")
    st.markdown('<div class="header-line"></div>', unsafe_allow_html=True)
    st.caption("DP-700 • Microsoft Fabric Data Engineer")

    st.divider()

    # Theme toggle
    theme_label = "🌙 Dark Mode" if st.session_state.theme == "dark" else "☀️ Light Mode"
    if st.button(theme_label, key="theme_toggle", use_container_width=True):
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
        st.rerun()

    st.divider()

    # API Status
    try:
        health = requests.get(f"{API_URL}/api/health", timeout=3).json()
        keys = health.get("api_keys", {})
        gemini_ok = "✅" if keys.get("gemini") else "❌"
        groq_ok = "✅" if keys.get("groq") else "❌"
        st.caption(f"Gemini: {gemini_ok}  •  Groq: {groq_ok}")
    except Exception:
        st.caption("⚠️ Backend starting...")

    st.divider()
    st.markdown("### 📅 10-Day Plan")
    st.caption("Day 1-2: Ingest Data")
    st.caption("Day 3-4: Transform Data")
    st.caption("Day 5-6: Design Solutions")
    st.caption("Day 7-8: Security & Monitor")
    st.caption("Day 9: CI/CD Review")
    st.caption("Day 10: 🏆 Final Exam")

    st.divider()
    st.markdown(
        f"<p style='text-align:center; color:{t['text_muted']}; font-size:0.75rem;'>"
        "Built with 💜 by FabricPrep AI</p>",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Main Dashboard
# ---------------------------------------------------------------------------
st.markdown(
    f"""
    <h1 style='text-align:center;'>
        <span style='background: linear-gradient(135deg, #2563eb 0%, #06b6d4 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-weight: 800;'>🚀 FabricPrep</span>
    </h1>
    <p style='text-align:center; color:{t["text_secondary"]}; font-size:1.1rem; margin-top:-10px;'>
        Your AI-powered study buddy for the Microsoft DP-700 certification 🔥
    </p>
    """,
    unsafe_allow_html=True,
)
st.markdown('<div class="header-line"></div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Stats row
# ---------------------------------------------------------------------------
try:
    analytics = requests.get(f"{API_URL}/api/analytics", timeout=5).json()
    summary = analytics.get("summary", {})
except Exception:
    summary = {
        "modules_completed": 0, "total_time_mins": 0,
        "avg_quiz_score": 0, "total_quizzes": 0,
        "total_notes": 0, "total_chats": 0,
    }

col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1:
    st.metric("Modules Done", f"{summary['modules_completed']}/10")
with col2:
    hours = summary["total_time_mins"] // 60
    mins = summary["total_time_mins"] % 60
    st.metric("Study Time", f"{hours}h {mins}m")
with col3:
    st.metric("Avg Score", f"{summary['avg_quiz_score']}%")
with col4:
    st.metric("Quizzes Taken", summary["total_quizzes"])
with col5:
    st.metric("Notes Made", summary["total_notes"])
with col6:
    st.metric("AI Chats", summary["total_chats"])

st.markdown("")

# ---------------------------------------------------------------------------
# Quick Actions
# ---------------------------------------------------------------------------
st.markdown("### ⚡ Quick Actions")
qa1, qa2, qa3, qa4 = st.columns(4)

with qa1:
    st.markdown(
        f"""<div style='background: linear-gradient(135deg, {t["accent_card_bg"]}, {t["accent_cyan_bg"]});
        border: 1px solid rgba(37,99,235,0.3); border-radius: 16px; padding: 1.5rem; text-align: center;'>
        <div style='font-size: 2.5rem;'>🤖</div>
        <div style='font-weight: 700; margin-top: 0.5rem; color: {t["text_primary"]};'>AI Tutor</div>
        <div style='color: {t["text_secondary"]}; font-size: 0.85rem;'>Chat with DP_Bot</div>
        </div>""",
        unsafe_allow_html=True,
    )
    if st.button("Start Chatting", key="qa_chat", use_container_width=True):
        st.switch_page("pages/2_🤖_AI_Tutor.py")

with qa2:
    st.markdown(
        f"""<div style='background: linear-gradient(135deg, {t["accent_green_bg"]}, {t["accent_cyan_bg"]});
        border: 1px solid rgba(16,185,129,0.3); border-radius: 16px; padding: 1.5rem; text-align: center;'>
        <div style='font-size: 2.5rem;'>🎙️</div>
        <div style='font-weight: 700; margin-top: 0.5rem; color: {t["text_primary"]};'>Voice Bot</div>
        <div style='color: {t["text_secondary"]}; font-size: 0.85rem;'>Talk & learn out loud</div>
        </div>""",
        unsafe_allow_html=True,
    )
    if st.button("Start Talking", key="qa_voice", use_container_width=True):
        st.switch_page("pages/3_🎙️_Voice_Bot.py")

with qa3:
    st.markdown(
        f"""<div style='background: linear-gradient(135deg, {t["accent_amber_bg"]}, {t["accent_rose_bg"]});
        border: 1px solid rgba(245,158,11,0.3); border-radius: 16px; padding: 1.5rem; text-align: center;'>
        <div style='font-size: 2.5rem;'>🧪</div>
        <div style='font-weight: 700; margin-top: 0.5rem; color: {t["text_primary"]};'>Take Quiz</div>
        <div style='color: {t["text_secondary"]}; font-size: 0.85rem;'>Test your knowledge</div>
        </div>""",
        unsafe_allow_html=True,
    )
    if st.button("Start Quiz", key="qa_quiz", use_container_width=True):
        st.switch_page("pages/5_🧪_Quiz.py")

with qa4:
    st.markdown(
        f"""<div style='background: linear-gradient(135deg, {t["accent_rose_bg"]}, {t["accent_card_bg"]});
        border: 1px solid rgba(244,63,94,0.3); border-radius: 16px; padding: 1.5rem; text-align: center;'>
        <div style='font-size: 2.5rem;'>📝</div>
        <div style='font-weight: 700; margin-top: 0.5rem; color: {t["text_primary"]};'>Journal</div>
        <div style='color: {t["text_secondary"]}; font-size: 0.85rem;'>Make study notes</div>
        </div>""",
        unsafe_allow_html=True,
    )
    if st.button("Open Journal", key="qa_journal", use_container_width=True):
        st.switch_page("pages/4_📝_Journal.py")

st.markdown("")

# ---------------------------------------------------------------------------
# Progress Overview
# ---------------------------------------------------------------------------
st.markdown("### 📊 Module Progress")

from assets.exam_data import get_all_modules

modules = get_all_modules()
try:
    progress_data = analytics.get("progress", [])
except NameError:
    progress_data = []
progress_map = {p["module_id"]: p for p in progress_data}

# Display modules in a 2-column grid
for i in range(0, len(modules), 2):
    cols = st.columns(2)
    for j, col in enumerate(cols):
        idx = i + j
        if idx >= len(modules):
            break
        m = modules[idx]
        prog = progress_map.get(m["id"], {})
        status = prog.get("status", "not_started")
        time_spent = prog.get("time_spent_mins", 0)

        status_icon = {"not_started": "⬜", "in_progress": "🟡", "completed": "✅"}.get(status, "⬜")
        status_label = {"not_started": "Not Started", "in_progress": "In Progress", "completed": "Completed"}.get(status, "Not Started")
        status_color = {"not_started": t["text_muted"], "in_progress": "#f59e0b", "completed": "#10b981"}.get(status, t["text_muted"])

        with col:
            st.markdown(
                f"""<div style='background: {t["bg_card"]}; border: 1px solid {t["border"]};
                border-radius: 16px; padding: 1.2rem; margin-bottom: 0.5rem;
                backdrop-filter: blur(12px);'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <span style='font-size: 1.3rem;'>{m['icon']}</span>
                        <span style='font-weight: 700; color: {t["text_primary"]}; margin-left: 0.5rem;'>Day {m['day']}</span>
                        <span style='color: {t["text_secondary"]}; margin-left: 0.3rem;'>— {m['title']}</span>
                    </div>
                    <div style='display: flex; align-items: center; gap: 8px;'>
                        <span style='color: {status_color}; font-size: 0.8rem; font-weight: 600;'>{status_icon} {status_label}</span>
                        <span style='color: {t["text_muted"]}; font-size: 0.75rem;'>({time_spent}m)</span>
                    </div>
                </div>
                <div style='color: {t["text_muted"]}; font-size: 0.8rem; margin-top: 0.3rem;'>{m['weight']} of exam</div>
                </div>""",
                unsafe_allow_html=True,
            )

st.markdown("")

# ---------------------------------------------------------------------------
# Motivational footer
# ---------------------------------------------------------------------------
st.markdown(
    f"""<div style='text-align: center; padding: 2rem; margin-top: 1rem;
    background: linear-gradient(135deg, {t["accent_card_bg"]}, {t["accent_cyan_bg"]});
    border-radius: 16px; border: 1px solid {t["border"]};'>
    <div style='font-size: 1.5rem; font-weight: 800; color: {t["text_primary"]};'>
        "Bachcho, certification crack karna hai toh LET'S GOOO! 🔥"
    </div>
    <div style='color: {t["text_secondary"]}; margin-top: 0.5rem;'>— DP_Bot AI (your hype tutor)</div>
    </div>""",
    unsafe_allow_html=True,
)
