"""
DP-700 Exam Prep — Voice Processing
STT: Groq Whisper API  |  TTS: Edge-TTS (primary, neural) + gTTS (fallback)
"""

import os
import io
import tempfile
import asyncio
from dotenv import load_dotenv

load_dotenv()


def _get_groq_key() -> str:
    """Get Groq API key from environment or Streamlit secrets."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        try:
            import streamlit as st
            if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
                api_key = st.secrets["GROQ_API_KEY"]
        except Exception:
            pass
    return api_key or ""


def transcribe_audio(audio_bytes: bytes) -> str:
    """
    Transcribe audio bytes to text using Groq Whisper API.
    Falls back to a message if API key is missing.
    """
    api_key = _get_groq_key()

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


def text_to_speech(text: str, lang: str = "en", slow: bool = False) -> tuple:
    """
    Convert text to speech. Tries Edge-TTS first (free, high-quality neural voices),
    falls back to gTTS (robotic but reliable).

    Returns: (audio_bytes, mime_type) tuple.
      - Edge-TTS returns MP3 → ("audio/mp3")
      - gTTS returns MP3 → ("audio/mp3")
    """
    # Try Edge-TTS first (Microsoft neural voices — natural and expressive)
    audio_result = _tts_edge(text)
    if audio_result:
        return audio_result

    # Fallback to gTTS
    audio_result = _tts_gtts(text, lang, slow)
    if audio_result:
        return audio_result

    return (b"", "audio/mp3")


def _tts_edge(text: str) -> tuple:
    """
    Generate speech using Edge-TTS (Microsoft's neural TTS voices).
    Free, no API key needed, high-quality natural voices.
    Returns (audio_bytes, mime_type) or None on failure.
    """
    try:
        import edge_tts
        import re

        # Clean text for TTS — remove markdown and emojis
        clean_text = re.sub(r'[🔥💪🎯⚠️✨🚀😵💀🧠📚📝🤖🎙️🧪📊⚙️🏆❌✅🟢🟡🔴⬜🔄🌊⚡🏠🏗️🔒📈🔗💜🎉😤💡🧑‍🍳👶💻💬🔊🎤🎓🎛️💾📖✏️📌📋📥🗑️📄🔍]', '', text)
        clean_text = re.sub(r'[#*`_~\[\]()]', '', clean_text)
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()

        if not clean_text or len(clean_text) < 3:
            clean_text = "Nothing to say here."

        # Use a chaotic, hyper energetic voice for IShowSpeed persona
        # en-US-RogerNeural: Lively male voice, sped up for maximum hype
        voice = "en-US-RogerNeural"

        async def generate():
            communicate = edge_tts.Communicate(clean_text, voice, rate="+25%", pitch="+15Hz")
            audio_buffer = io.BytesIO()
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_buffer.write(chunk["data"])
            audio_buffer.seek(0)
            return audio_buffer.read()

        # Run the async function — handle existing event loop
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're in an async context (e.g., inside Streamlit/Flask)
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    audio_bytes = pool.submit(
                        lambda: asyncio.run(generate())
                    ).result(timeout=30)
            else:
                audio_bytes = loop.run_until_complete(generate())
        except RuntimeError:
            audio_bytes = asyncio.run(generate())

        if len(audio_bytes) > 100:  # Sanity check
            print(f"[TTS] Edge-TTS generated {len(audio_bytes)} bytes (voice: {voice})")
            return (audio_bytes, "audio/mp3")

        return None

    except ImportError:
        print("[TTS] edge-tts not installed, falling back to gTTS")
        return None
    except Exception as e:
        print(f"[TTS] Edge-TTS failed: {e}, falling back to gTTS")
        return None


def _tts_gtts(text: str, lang: str = "en", slow: bool = False) -> tuple:
    """
    Fallback TTS using gTTS (free, no API key needed).
    Returns (audio_bytes, mime_type) or None on failure.
    """
    try:
        from gtts import gTTS
        import re

        # Clean text for TTS (remove emojis and special chars that sound weird)
        clean_text = re.sub(r'[🔥💪🎯⚠️✨🚀😵💀🧠📚📝🤖🎙️🧪📊⚙️🏆❌✅]', '', text)
        clean_text = re.sub(r'[#*`_~\[\]()]', '', clean_text)
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()

        if not clean_text:
            clean_text = "Nothing to say here."

        tts = gTTS(text=clean_text, lang=lang, slow=slow)
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        audio_bytes = audio_buffer.read()

        if audio_bytes:
            print(f"[TTS] gTTS fallback generated {len(audio_bytes)} bytes")
            return (audio_bytes, "audio/mp3")

        return None
    except Exception as e:
        print(f"[TTS] gTTS also failed: {e}")
        return None
