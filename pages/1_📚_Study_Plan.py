"""
📚 Study Plan — 10-Day DP-700 Certification Journey
Track progress, start modules, and see your study roadmap.
"""

import streamlit as st
import requests
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from assets.exam_data import get_all_modules, get_module
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

if is_light:
    st.markdown("""<style>
    [data-testid="stAppViewContainer"] { background: #f8fafc !important; }
    [data-testid="stHeader"] { background: #f8fafc !important; }
    [data-testid="stBottomBlockContainer"], [data-testid="stBottom"] { background: #f8fafc !important; }
    [data-testid="stHeader"] { background: #f8fafc !important; }
    [data-testid="stBottomBlockContainer"], [data-testid="stBottom"] { background: #f8fafc !important; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #f1f5f9 0%, #e2e8f0 100%) !important; border-right: 1px solid rgba(0,0,0,0.08) !important; }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: #1e293b !important; }
    .stMarkdown p, .stCaption p { color: #475569 !important; }
    [data-testid="stExpander"] { background: rgba(255,255,255,0.85) !important; border: 1px solid rgba(0,0,0,0.08) !important; }
    </style>""", unsafe_allow_html=True)

st.markdown(
    """<h1 style='background: linear-gradient(135deg, #2563eb, #06b6d4);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    font-weight: 800;'>📚 10-Day Study Plan</h1>""",
    unsafe_allow_html=True,
)
st.markdown('<div class="header-line"></div>', unsafe_allow_html=True)
st.caption("Your structured roadmap to cracking DP-700. Each day = one focused module. Let's gooo! 🔥")

# Get progress data
try:
    progress_resp = requests.get(f"{API_URL}/api/progress", timeout=5).json()
    progress_data = progress_resp.get("progress", [])
except Exception:
    progress_data = []

progress_map = {p["module_id"]: p for p in progress_data}
modules = get_all_modules()

# Overall progress bar
completed_count = sum(1 for p in progress_data if p.get("status") == "completed")
st.progress(completed_count / len(modules), text=f"Overall Progress: {completed_count}/{len(modules)} modules completed")

st.markdown("")

# Module cards
for m in modules:
    prog = progress_map.get(m["id"], {})
    status = prog.get("status", "not_started")
    time_spent = prog.get("time_spent_mins", 0)

    status_cfg = {
        "not_started": {"icon": "⬜", "label": "Not Started", "color": text_muted, "bg": "rgba(100,116,139,0.1)"},
        "in_progress": {"icon": "🟡", "label": "In Progress", "color": "#f59e0b", "bg": "rgba(245,158,11,0.1)"},
        "completed": {"icon": "✅", "label": "Completed", "color": "#10b981", "bg": "rgba(16,185,129,0.1)"},
    }
    cfg = status_cfg.get(status, status_cfg["not_started"])

    with st.expander(f"{m['icon']} **Day {m['day']}** — {m['title']}  |  {cfg['icon']} {cfg['label']}  |  ⏱️ {time_spent}m", expanded=(status == "in_progress")):
        st.markdown(f"**{m['description']}**")
        st.markdown(f"📊 **Exam Weight:** {m['weight']}")

        st.markdown("#### 📖 Topics to Cover:")
        for t_topic in m["topics"]:
            st.markdown(f"- {t_topic}")

        st.markdown("#### 🧠 Key Concepts:")
        for c in m["key_concepts"]:
            st.markdown(f"- {c}")

        st.markdown("#### 🎯 Exam Tips:")
        for tip in m["exam_tips"]:
            st.info(f"🎯 {tip}")

        st.markdown("")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button(f"🤖 Study with AI", key=f"study_{m['id']}", use_container_width=True):
                st.session_state.current_module = m["id"]
                # Mark as in progress
                try:
                    requests.put(f"{API_URL}/api/progress", json={
                        "module_id": m["id"], "status": "in_progress"
                    }, timeout=3)
                except Exception:
                    pass
                st.switch_page("pages/2_🤖_AI_Tutor.py")

        with col2:
            if st.button(f"🧪 Take Quiz", key=f"quiz_{m['id']}", use_container_width=True):
                st.session_state.current_module = m["id"]
                st.switch_page("pages/5_🧪_Quiz.py")

        with col3:
            if st.button(f"📝 Make Notes", key=f"notes_{m['id']}", use_container_width=True):
                st.session_state.current_module = m["id"]
                st.switch_page("pages/4_📝_Journal.py")

        with col4:
            if status != "completed":
                if st.button(f"✅ Mark Done", key=f"done_{m['id']}", use_container_width=True):
                    try:
                        requests.put(f"{API_URL}/api/progress", json={
                            "module_id": m["id"], "status": "completed"
                        }, timeout=3)
                        st.rerun()
                    except Exception:
                        st.error("Failed to update progress")
            else:
                st.success("Module completed! 🎉")
