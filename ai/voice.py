"""
DP-700 Exam Prep — Voice Processing
STT: Groq Whisper API  |  TTS: gTTS (Google Text-to-Speech)
"""

import os
import io
import tempfile
from dotenv import load_dotenv

load_dotenv()


def transcribe_audio(audio_bytes: bytes) -> str:
    """
    Transcribe audio bytes to text using Groq Whisper API.
    Falls back to a message if API key is missing.
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        try:
            import streamlit as st
            if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
                api_key = st.secrets["GROQ_API_KEY"]
        except Exception:
            pass

    if not api_key:
        return "[Voice transcription requires a Groq API key. Please set it in ⚙️ Settings.]"

    try:
        from groq import Groq
        client = Groq(api_key=api_key)

        # Write audio bytes to a temp file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        try:
            with open(tmp_path, "rb") as audio_file:
                transcription = client.audio.transcriptions.create(
                    model="whisper-large-v3",
                    file=audio_file,
                    language="en",
                )
            return transcription.text
        finally:
            os.unlink(tmp_path)

    except ImportError:
        # If groq package isn't installed, use litellm's transcription
        try:
            import litellm
            import json

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name
            try:
                response = litellm.transcription(
                    model="groq/whisper-large-v3",
                    file=open(tmp_path, "rb"),
                )
                return response.text
            finally:
                os.unlink(tmp_path)
        except Exception as e:
            return f"[Transcription error: {e}]"
    except Exception as e:
        return f"[Transcription error: {e}]"


def text_to_speech(text: str, lang: str = "en", slow: bool = False) -> bytes:
    """
    Convert text to speech using gTTS (free, no API key needed).
    Returns MP3 audio bytes.
    """
    try:
        from gtts import gTTS

        # Clean text for TTS (remove emojis and special chars that sound weird)
        import re
        clean_text = re.sub(r'[🔥💪🎯⚠️✨🚀😵💀🧠📚📝🤖🎙️🧪📊⚙️🏆❌✅]', '', text)
        clean_text = re.sub(r'[#*`_~\[\]()]', '', clean_text)
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()

        if not clean_text:
            clean_text = "Nothing to say here."

        tts = gTTS(text=clean_text, lang=lang, slow=slow)
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return audio_buffer.read()
    except Exception as e:
        print(f"[TTS] Error: {e}")
        return b""
