"""
⚙️ Settings — API Keys, Model Config, and Data Management
"""

import streamlit as st
import requests
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.server import start_flask_server, get_api_url
from ai.llm_engine import MODELS, check_api_keys

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
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #f1f5f9 0%, #e2e8f0 100%) !important; }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: #1e293b !important; }
    .stMarkdown p, .stCaption p { color: #475569 !important; }
    .stTextInput input { background: #f1f5f9 !important; border: 1px solid rgba(0,0,0,0.08) !important; color: #1e293b !important; }
    </style>""", unsafe_allow_html=True)

st.markdown(
    """<h1 style='background: linear-gradient(135deg, #2563eb, #06b6d4);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    font-weight: 800;'>⚙️ Settings</h1>""",
    unsafe_allow_html=True,
)
st.markdown('<div class="header-line"></div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# API Keys
# ---------------------------------------------------------------------------
st.markdown("### 🔑 API Keys")
st.markdown(
    f"""<div style='background: rgba(245,158,11,0.1); border: 1px solid rgba(245,158,11,0.3);
    border-radius: 12px; padding: 1rem; margin-bottom: 1rem;'>
    <strong style='color: #f59e0b;'>💡 How to get API keys (both are FREE!):</strong>
    <ul style='color: {text_secondary}; margin-top: 0.5rem;'>
        <li><strong>Gemini</strong>: Go to <a href='https://aistudio.google.com/apikey' target='_blank' style='color: #06b6d4;'>Google AI Studio</a> → Create API Key</li>
        <li><strong>Groq</strong>: Go to <a href='https://console.groq.com/keys' target='_blank' style='color: #06b6d4;'>Groq Console</a> → Create API Key</li>
    </ul></div>""",
    unsafe_allow_html=True,
)

# Check current key status
key_status = check_api_keys()

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"**Gemini API Key** {'✅ Set' if key_status['gemini'] else '❌ Not Set'}")
    gemini_key = st.text_input(
        "Gemini Key",
        type="password",
        placeholder="Enter your Gemini API key...",
        key="gemini_key_input",
        label_visibility="collapsed",
    )
    if st.button("Save Gemini Key", key="save_gemini", use_container_width=True):
        if gemini_key:
            os.environ["GEMINI_API_KEY"] = gemini_key
            st.success("✅ Gemini key saved for this session!")
            st.rerun()

with col2:
    st.markdown(f"**Groq API Key** {'✅ Set' if key_status['groq'] else '❌ Not Set'}")
    groq_key = st.text_input(
        "Groq Key",
        type="password",
        placeholder="Enter your Groq API key...",
        key="groq_key_input",
        label_visibility="collapsed",
    )
    if st.button("Save Groq Key", key="save_groq", use_container_width=True):
        if groq_key:
            os.environ["GROQ_API_KEY"] = groq_key
            st.success("✅ Groq key saved for this session!")
            st.rerun()

st.markdown(
    f"""<div style='color: {text_muted}; font-size: 0.8rem; margin-top: 0.5rem;'>
    <strong>For Streamlit Cloud deployment</strong>, add these keys in
    <code>.streamlit/secrets.toml</code> or via the Streamlit Cloud dashboard under
    "Secrets":<br>
    <code>GEMINI_API_KEY = "your-key"</code><br>
    <code>GROQ_API_KEY = "your-key"</code>
    </div>""",
    unsafe_allow_html=True,
)

st.divider()

# ---------------------------------------------------------------------------
# Model Configuration
# ---------------------------------------------------------------------------
st.markdown("### 🤖 AI Model Configuration")

model_info = {
    "gemini": {
        "name": "Gemini 2.0 Flash",
        "provider": "Google",
        "speed": "Fast",
        "best_for": "Detailed explanations, code examples, comprehensive answers",
        "icon": "✨",
    },
    "groq": {
        "name": "Llama 3.3 70B",
        "provider": "Groq",
        "speed": "Ultra-fast",
        "best_for": "Quick Q&A, quiz generation, rapid-fire revision",
        "icon": "🚀",
    },
}

for key, info in model_info.items():
    status = "✅ Available" if key_status.get(key) else "❌ Key Missing"
    st.markdown(
        f"""<div style='background: {bg_card}; border: 1px solid {border_color};
        border-radius: 12px; padding: 1rem; margin: 0.5rem 0;'>
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <div>
                <span style='font-size: 1.3rem;'>{info['icon']}</span>
                <span style='font-weight: 700; color: {text_primary}; margin-left: 0.5rem;'>{info['name']}</span>
                <span style='color: {text_muted}; margin-left: 0.5rem;'>({info['provider']})</span>
            </div>
            <span style='color: {"#10b981" if key_status.get(key) else "#f43f5e"}; font-size: 0.85rem;'>{status}</span>
        </div>
        <div style='color: {text_secondary}; font-size: 0.85rem; margin-top: 0.3rem;'>
            ⚡ {info['speed']} • 🎯 Best for: {info['best_for']}
        </div></div>""",
        unsafe_allow_html=True,
    )

st.divider()

# ---------------------------------------------------------------------------
# Data Management
# ---------------------------------------------------------------------------
st.markdown("### 💾 Data Management")

st.warning("⚠️ These actions are irreversible!")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🗑️ Reset All Progress", use_container_width=True):
        st.session_state.confirm_reset_progress = True

    if st.session_state.get("confirm_reset_progress"):
        st.error("Are you sure? This will reset ALL module progress.")
        if st.button("Yes, Reset Progress", key="confirm_progress"):
            try:
                # Reset via direct DB access
                from database.db import get_connection
                with get_connection() as conn:
                    conn.execute("DELETE FROM study_progress")
                st.success("Progress reset!")
                del st.session_state.confirm_reset_progress
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

with col2:
    if st.button("🗑️ Reset All Quizzes", use_container_width=True):
        st.session_state.confirm_reset_quizzes = True

    if st.session_state.get("confirm_reset_quizzes"):
        st.error("Are you sure? This will delete ALL quiz results.")
        if st.button("Yes, Reset Quizzes", key="confirm_quizzes"):
            try:
                from database.db import get_connection
                with get_connection() as conn:
                    conn.execute("DELETE FROM quiz_results")
                    conn.execute("DELETE FROM user_weaknesses")
                st.success("Quizzes reset!")
                del st.session_state.confirm_reset_quizzes
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

with col3:
    if st.button("🗑️ Reset Chat History", use_container_width=True):
        st.session_state.confirm_reset_chat = True

    if st.session_state.get("confirm_reset_chat"):
        st.error("Are you sure? This will delete ALL chat history.")
        if st.button("Yes, Reset Chat", key="confirm_chat"):
            try:
                from database.db import get_connection
                with get_connection() as conn:
                    conn.execute("DELETE FROM chat_history")
                st.session_state.chat_messages = {}
                st.success("Chat history reset!")
                del st.session_state.confirm_reset_chat
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

st.divider()

# ---------------------------------------------------------------------------
# Deployment Guide
# ---------------------------------------------------------------------------
st.markdown("### 🚀 Streamlit Cloud Deployment")
st.markdown(
    """
1. **Push to GitHub**: Commit your code to a GitHub repo
2. **Go to** [share.streamlit.io](https://share.streamlit.io)
3. **Deploy**: Select your repo, set main file as `streamlit_app.py`
4. **Add Secrets**: In the Streamlit Cloud dashboard, go to **Settings → Secrets** and add:
   ```toml
   GEMINI_API_KEY = "your-gemini-api-key"
   GROQ_API_KEY = "your-groq-api-key"
   ```
5. **Done!** Your app is live 🎉
"""
)

st.divider()

# App info
st.markdown(
    f"""<div style='text-align: center; color: {text_muted}; font-size: 0.85rem; padding: 1rem;'>
    <strong>FabricPrep v1.1</strong> — DP-700 Exam Prep App<br>
    Built with Streamlit • Flask • LiteLLM • Gemini • Groq<br>
    Made with 💜 for aspiring Fabric Data Engineers
    </div>""",
    unsafe_allow_html=True,
)
