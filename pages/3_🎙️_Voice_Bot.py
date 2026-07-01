"""
🎙️ Voice Bot — Talk to DP_Bot
Record your voice → AI responds → Hear the answer. Full voice loop.
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

# Session state
if "voice_messages" not in st.session_state:
    st.session_state.voice_messages = []
if "current_module" not in st.session_state:
    st.session_state.current_module = 1

st.markdown(
    """<h1 style='background: linear-gradient(135deg, #2563eb, #06b6d4);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    font-weight: 800;'>🎙️ Voice Bot</h1>""",
    unsafe_allow_html=True,
)
st.markdown('<div class="header-line"></div>', unsafe_allow_html=True)
st.caption("Talk to DP_Bot out loud! Record → Transcribe → AI Responds → Listen. 🔊")

# Sidebar
with st.sidebar:
    st.markdown("### 🎛️ Voice Settings")

    modules = get_all_modules()
    module_options = {f"Day {m['day']}: {m['icon']} {m['title']}": m["id"] for m in modules}
    default_idx = st.session_state.current_module - 1
    selected = st.selectbox(
        "📚 Module",
        options=list(module_options.keys()),
        index=min(default_idx, len(module_options) - 1),
        key="voice_module",
    )
    module_id = module_options[selected]
    st.session_state.current_module = module_id

    st.divider()

    if st.button("🗑️ Clear Voice History", use_container_width=True):
        st.session_state.voice_messages = []
        st.rerun()

# How it works
st.markdown(
    """<div style='background: rgba(30,30,70,0.6); border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px; padding: 1rem; margin-bottom: 1rem;'>
    <strong style='color: #e2e8f0;'>How it works:</strong>
    <span style='color: #94a3b8;'> 🎤 Record → 📝 Auto-transcribe (Groq Whisper) → 🤖 AI responds → 🔊 Listen to answer</span>
    </div>""",
    unsafe_allow_html=True,
)

# Display conversation history
chat_container = st.container(height=500, border=False)

with chat_container:
    for msg in st.session_state.voice_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("audio"):
                st.audio(msg["audio"], format="audio/mp3")

# Voice input
st.markdown("### 🎤 Record Your Question")
audio_value = st.audio_input("Tap the mic and ask your question", key="voice_input")

# Also allow text fallback
text_input = st.chat_input("Or type your question here... 💬")

# Process voice input
if audio_value is not None:
    audio_bytes = audio_value.getvalue()

    # Step 1: Transcribe
    with st.spinner("📝 Transcribing your voice..."):
        try:
            files = {"audio": ("recording.wav", audio_bytes, "audio/wav")}
            stt_resp = requests.post(f"{API_URL}/api/stt", files=files, timeout=30)
            transcribed_text = stt_resp.json().get("text", "[Could not transcribe]")
        except Exception as e:
            transcribed_text = f"[Transcription failed: {e}]"

    # Show transcription
    st.session_state.voice_messages.append({"role": "user", "content": f"🎤 *\"{transcribed_text}\"*"})

    # Step 2: Get AI response
    with st.spinner("🤖 DP_Bot is cooking a response..."):
        try:
            chat_resp = requests.post(
                f"{API_URL}/api/chat",
                json={
                    "message": transcribed_text,
                    "module_id": module_id,
                    "model_key": st.session_state.get("model_key", "gemini"),
                },
                timeout=60,
            ).json()
            ai_response = chat_resp.get("response", "Sorry, couldn't get a response.")
        except Exception as e:
            ai_response = f"Connection error: {e}"

    # Step 3: Generate TTS
    tts_audio = None
    with st.spinner("🔊 Generating voice response..."):
        try:
            tts_resp = requests.post(
                f"{API_URL}/api/tts",
                json={"text": ai_response},
                timeout=30,
            )
            if tts_resp.status_code == 200 and tts_resp.headers.get("content-type", "").startswith("audio"):
                tts_audio = tts_resp.content
        except Exception:
            pass

    # Store messages
    msg_data = {"role": "assistant", "content": ai_response}
    if tts_audio:
        msg_data["audio"] = tts_audio
    st.session_state.voice_messages.append(msg_data)
    st.rerun()

# Process text input (fallback)
if text_input:
    st.session_state.voice_messages.append({"role": "user", "content": text_input})

    with st.spinner("🤖 DP_Bot is cooking..."):
        try:
            chat_resp = requests.post(
                f"{API_URL}/api/chat",
                json={
                    "message": text_input,
                    "module_id": module_id,
                    "model_key": st.session_state.get("model_key", "gemini"),
                },
                timeout=60,
            ).json()
            ai_response = chat_resp.get("response", "Sorry, couldn't get a response.")
        except Exception as e:
            ai_response = f"Connection error: {e}"

    # Generate TTS
    tts_audio = None
    try:
        tts_resp = requests.post(
            f"{API_URL}/api/tts",
            json={"text": ai_response},
            timeout=30,
        )
        if tts_resp.status_code == 200 and tts_resp.headers.get("content-type", "").startswith("audio"):
            tts_audio = tts_resp.content
    except Exception:
        pass

    msg_data = {"role": "assistant", "content": ai_response}
    if tts_audio:
        msg_data["audio"] = tts_audio
    st.session_state.voice_messages.append(msg_data)
    st.rerun()
