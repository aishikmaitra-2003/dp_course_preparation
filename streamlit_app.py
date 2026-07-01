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
        "<p style='text-align:center; color:#64748b; font-size:0.75rem;'>"
        "Built with 💜 by FabricPrep AI</p>",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Main Dashboard
# ---------------------------------------------------------------------------
st.markdown(
    """
    <h1 style='text-align:center;'>
        <span style='background: linear-gradient(135deg, #2563eb 0%, #06b6d4 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-weight: 800;'>🚀 FabricPrep</span>
    </h1>
    <p style='text-align:center; color:#94a3b8; font-size:1.1rem; margin-top:-10px;'>
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
        """<div style='background: linear-gradient(135deg, rgba(37,99,235,0.15), rgba(6,182,212,0.15));
        border: 1px solid rgba(37,99,235,0.3); border-radius: 16px; padding: 1.5rem; text-align: center;'>
        <div style='font-size: 2.5rem;'>🤖</div>
        <div style='font-weight: 700; margin-top: 0.5rem; color: #e2e8f0;'>AI Tutor</div>
        <div style='color: #94a3b8; font-size: 0.85rem;'>Chat with DP_Bot</div>
        </div>""",
        unsafe_allow_html=True,
    )
    if st.button("Start Chatting", key="qa_chat", use_container_width=True):
        st.switch_page("pages/2_🤖_AI_Tutor.py")

with qa2:
    st.markdown(
        """<div style='background: linear-gradient(135deg, rgba(16,185,129,0.15), rgba(6,182,212,0.15));
        border: 1px solid rgba(16,185,129,0.3); border-radius: 16px; padding: 1.5rem; text-align: center;'>
        <div style='font-size: 2.5rem;'>🎙️</div>
        <div style='font-weight: 700; margin-top: 0.5rem; color: #e2e8f0;'>Voice Bot</div>
        <div style='color: #94a3b8; font-size: 0.85rem;'>Talk & learn out loud</div>
        </div>""",
        unsafe_allow_html=True,
    )
    if st.button("Start Talking", key="qa_voice", use_container_width=True):
        st.switch_page("pages/3_🎙️_Voice_Bot.py")

with qa3:
    st.markdown(
        """<div style='background: linear-gradient(135deg, rgba(245,158,11,0.15), rgba(244,63,94,0.15));
        border: 1px solid rgba(245,158,11,0.3); border-radius: 16px; padding: 1.5rem; text-align: center;'>
        <div style='font-size: 2.5rem;'>🧪</div>
        <div style='font-weight: 700; margin-top: 0.5rem; color: #e2e8f0;'>Take Quiz</div>
        <div style='color: #94a3b8; font-size: 0.85rem;'>Test your knowledge</div>
        </div>""",
        unsafe_allow_html=True,
    )
    if st.button("Start Quiz", key="qa_quiz", use_container_width=True):
        st.switch_page("pages/5_🧪_Quiz.py")

with qa4:
    st.markdown(
        """<div style='background: linear-gradient(135deg, rgba(244,63,94,0.15), rgba(37,99,235,0.15));
        border: 1px solid rgba(244,63,94,0.3); border-radius: 16px; padding: 1.5rem; text-align: center;'>
        <div style='font-size: 2.5rem;'>📝</div>
        <div style='font-weight: 700; margin-top: 0.5rem; color: #e2e8f0;'>Journal</div>
        <div style='color: #94a3b8; font-size: 0.85rem;'>Make study notes</div>
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
        status_color = {"not_started": "#64748b", "in_progress": "#f59e0b", "completed": "#10b981"}.get(status, "#64748b")

        with col:
            st.markdown(
                f"""<div style='background: rgba(30,30,70,0.6); border: 1px solid rgba(255,255,255,0.1);
                border-radius: 16px; padding: 1.2rem; margin-bottom: 0.5rem;
                backdrop-filter: blur(12px);'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <span style='font-size: 1.3rem;'>{m['icon']}</span>
                        <span style='font-weight: 700; color: #e2e8f0; margin-left: 0.5rem;'>Day {m['day']}</span>
                        <span style='color: #94a3b8; margin-left: 0.3rem;'>— {m['title']}</span>
                    </div>
                    <div style='display: flex; align-items: center; gap: 8px;'>
                        <span style='color: {status_color}; font-size: 0.8rem; font-weight: 600;'>{status_icon} {status_label}</span>
                        <span style='color: #64748b; font-size: 0.75rem;'>({time_spent}m)</span>
                    </div>
                </div>
                <div style='color: #64748b; font-size: 0.8rem; margin-top: 0.3rem;'>{m['weight']} of exam</div>
                </div>""",
                unsafe_allow_html=True,
            )

st.markdown("")

# ---------------------------------------------------------------------------
# Motivational footer
# ---------------------------------------------------------------------------
st.markdown(
    """<div style='text-align: center; padding: 2rem; margin-top: 1rem;
    background: linear-gradient(135deg, rgba(37,99,235,0.08), rgba(6,182,212,0.08));
    border-radius: 16px; border: 1px solid rgba(255,255,255,0.05);'>
    <div style='font-size: 1.5rem; font-weight: 800; color: #e2e8f0;'>
        "Bachcho, certification crack karna hai toh LET'S GOOO! 🔥"
    </div>
    <div style='color: #94a3b8; margin-top: 0.5rem;'>— DP_Bot AI (your hype tutor)</div>
    </div>""",
    unsafe_allow_html=True,
)
