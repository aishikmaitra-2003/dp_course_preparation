"""
🤖 AI Tutor — Chat with DP_Bot
GenZ energy + IShowSpeed vibes. LiteLLM switches between Gemini & Groq.
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
accent_card_bg = "rgba(37,99,235,0.06)" if is_light else "rgba(37,99,235,0.12)"
accent_cyan_bg = "rgba(8,145,178,0.06)" if is_light else "rgba(6,182,212,0.12)"

if is_light:
    st.markdown("""<style>
    [data-testid="stAppViewContainer"] { background: #f8fafc !important; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #f1f5f9 0%, #e2e8f0 100%) !important; border-right: 1px solid rgba(0,0,0,0.08) !important; }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: #1e293b !important; }
    .stMarkdown p, .stCaption p { color: #475569 !important; }
    [data-testid="stChatInput"] textarea { background: #f1f5f9 !important; border: 1px solid rgba(0,0,0,0.08) !important; color: #1e293b !important; }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stMarkdown {
        background: #ffffff !important; border: 1px solid rgba(0,0,0,0.08) !important; color: #1e293b !important;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stMarkdown p,
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stMarkdown li,
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stMarkdown span { color: #1e293b !important; }
    </style>""", unsafe_allow_html=True)

# Session state
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = {}
if "current_module" not in st.session_state:
    st.session_state.current_module = 1
if "model_key" not in st.session_state:
    st.session_state.model_key = "gemini"

# Header
st.markdown(
    """<h1 style='background: linear-gradient(135deg, #2563eb, #06b6d4);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    font-weight: 800;'>🤖 DP_Bot AI Tutor</h1>""",
    unsafe_allow_html=True,
)
st.markdown('<div class="header-line"></div>', unsafe_allow_html=True)

# Sidebar controls
with st.sidebar:
    st.markdown("### 🎛️ Tutor Controls")

    # Module selector
    modules = get_all_modules()
    module_options = {f"Day {m['day']}: {m['icon']} {m['title']}": m["id"] for m in modules}
    default_idx = st.session_state.current_module - 1
    selected_module = st.selectbox(
        "📚 Current Module",
        options=list(module_options.keys()),
        index=min(default_idx, len(module_options) - 1),
        key="module_select",
    )
    module_id = module_options[selected_module]
    st.session_state.current_module = module_id

    st.divider()

    # Model switcher
    st.markdown("### 🔄 AI Model")
    _model_options = ["gemini", "groq", "nvidia_nim"]
    _model_labels = {
        "gemini": "✨ Gemini 2.0 Flash",
        "groq": "🚀 Groq Llama 3.3 70B",
        "nvidia_nim": "🟢 NVIDIA NIM Llama 3.1 70B",
    }
    model_choice = st.radio(
        "Select Model",
        options=_model_options,
        format_func=lambda x: _model_labels[x],
        index=_model_options.index(st.session_state.model_key) if st.session_state.model_key in _model_options else 0,
        key="model_radio",
    )
    st.session_state.model_key = model_choice

    st.divider()

    # Quick prompts
    st.markdown("### ⚡ Quick Prompts")
    quick_prompts = {
        "🎓 Explain this module": f"Give me a complete overview of Day {module_id} topics. Break it down simply.",
        "👶 ELI5 Mode": "Explain the main concepts of this module like I'm 5 years old. Use super simple analogies.",
        "💻 Show me code": "Show me the most important PySpark, T-SQL, or KQL code examples for this module's topics.",
        "🎯 Exam scenarios": "Give me realistic DP-700 exam scenario questions for this module with explanations.",
        "🧠 Memory hacks": "Give me mnemonics, acronyms, or tricks to remember key concepts from this module.",
        "⚡ Speed revision": "Give me a rapid-fire bullet-point revision of ALL key points in this module. Be super concise.",
    }

    for label, prompt in quick_prompts.items():
        if st.button(label, key=f"qp_{label}", use_container_width=True):
            st.session_state.pending_prompt = prompt

    st.divider()

    # Clear chat
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.chat_messages[module_id] = []
        try:
            # We'll just clear session state; DB history stays for quiz context
            pass
        except Exception:
            pass
        st.rerun()

# Module info banner
current_module = get_module(module_id)
if current_module:
    st.markdown(
        f"""<div style='background: linear-gradient(135deg, {accent_card_bg}, {accent_cyan_bg});
        border: 1px solid rgba(37,99,235,0.25); border-radius: 12px; padding: 1rem 1.2rem;
        margin-bottom: 1rem;'>
        <span style='font-size: 1.2rem;'>{current_module['icon']}</span>
        <span style='font-weight: 700; color: {text_primary};'> Day {current_module['day']}:</span>
        <span style='color: {text_secondary};'> {current_module['title']}</span>
        <span style='float: right; color: {text_muted}; font-size: 0.85rem;'>📊 {current_module['weight']} of exam</span>
        </div>""",
        unsafe_allow_html=True,
    )

# Initialize messages for this module
if module_id not in st.session_state.chat_messages:
    # Load from DB
    try:
        resp = requests.get(f"{API_URL}/api/analytics", timeout=3).json()
        # Seed with welcome message
        st.session_state.chat_messages[module_id] = [
            {
                "role": "assistant",
                "content": f"Yo what's good fam! 🔥 I'm **DP_Bot** — your AI tutor for DP-700!\n\n"
                f"We're studying **Day {current_module['day']}: {current_module['title']}** today.\n\n"
                f"This section is {current_module['weight']} of the exam, so we gotta nail it no cap! 💪\n\n"
                f"What do you wanna start with? Hit me with a question or tap one of the ⚡ Quick Prompts on the left!\n\n"
                f"_Let's cook! 🧑‍🍳_",
                "model_used": "DP_Bot 🤖",
            }
        ]
    except Exception:
        st.session_state.chat_messages[module_id] = [
            {
                "role": "assistant",
                "content": f"Hey! 🔥 Let's study **{current_module['title']}** — ask me anything!",
                "model_used": "DP_Bot 🤖",
            }
        ]

# Display chat messages in a scrollable container
chat_container = st.container(height=550, border=False)

with chat_container:
    for msg in st.session_state.chat_messages[module_id]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("model_used") and msg["role"] == "assistant":
                st.caption(f"🔧 {msg['model_used']}")

# Handle pending quick prompt
if "pending_prompt" in st.session_state:
    prompt = st.session_state.pending_prompt
    del st.session_state.pending_prompt

    # Display user message
    st.session_state.chat_messages[module_id].append({"role": "user", "content": prompt})
    with chat_container:
        with st.chat_message("user"):
            st.markdown(prompt)

    # Get AI response
    with chat_container:
        with st.chat_message("assistant"):
            with st.spinner("DP_Bot is cooking... 🧑‍🍳"):
                try:
                    resp = requests.post(
                        f"{API_URL}/api/chat",
                        json={
                            "message": prompt,
                            "module_id": module_id,
                            "model_key": st.session_state.model_key,
                        },
                        timeout=60,
                    ).json()
                    content = resp.get("response", "Hmm, something went wrong fam 😵")
                    model_used = resp.get("model_used", "unknown")
                except Exception as e:
                    content = f"Oof, connection error: {e}\n\nMake sure your API keys are set in ⚙️ Settings!"
                    model_used = "error"
    
            st.markdown(content)
            st.caption(f"🔧 {model_used}")

    st.session_state.chat_messages[module_id].append({
        "role": "assistant", "content": content, "model_used": model_used,
    })
    st.rerun()

# Chat input
if prompt := st.chat_input("Ask DP_Bot anything about DP-700... 💬"):
    # Display user message
    st.session_state.chat_messages[module_id].append({"role": "user", "content": prompt})
    with chat_container:
        with st.chat_message("user"):
            st.markdown(prompt)

    # Get AI response
    with chat_container:
        with st.chat_message("assistant"):
            with st.spinner("DP_Bot is cooking... 🧑‍🍳"):
                try:
                    resp = requests.post(
                        f"{API_URL}/api/chat",
                        json={
                            "message": prompt,
                            "module_id": module_id,
                            "model_key": st.session_state.model_key,
                        },
                        timeout=60,
                    ).json()
                    content = resp.get("response", "Hmm, something went wrong fam 😵")
                    model_used = resp.get("model_used", "unknown")
                except Exception as e:
                    content = f"Oof, connection error: {e}\n\nMake sure your API keys are set in ⚙️ Settings!"
                    model_used = "error"
    
            st.markdown(content)
            st.caption(f"🔧 {model_used}")

    st.session_state.chat_messages[module_id].append({
        "role": "assistant", "content": content, "model_used": model_used,
    })
    st.rerun()
