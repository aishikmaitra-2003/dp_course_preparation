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
        "not_started": {"icon": "⬜", "label": "Not Started", "color": "#64748b", "bg": "rgba(100,116,139,0.1)"},
        "in_progress": {"icon": "🟡", "label": "In Progress", "color": "#f59e0b", "bg": "rgba(245,158,11,0.1)"},
        "completed": {"icon": "✅", "label": "Completed", "color": "#10b981", "bg": "rgba(16,185,129,0.1)"},
    }
    cfg = status_cfg.get(status, status_cfg["not_started"])

    with st.expander(f"{m['icon']} **Day {m['day']}** — {m['title']}  |  {cfg['icon']} {cfg['label']}  |  ⏱️ {time_spent}m", expanded=(status == "in_progress")):
        st.markdown(f"**{m['description']}**")
        st.markdown(f"📊 **Exam Weight:** {m['weight']}")

        st.markdown("#### 📖 Topics to Cover:")
        for t in m["topics"]:
            st.markdown(f"- {t}")

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
