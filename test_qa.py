import os
import sys

# Fix Windows console encoding for emoji output
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai.llm_engine import chat_completion, generate_quiz_json, check_api_keys
from ai.voice import transcribe_audio, text_to_speech
from database.db import init_db, save_journal_entry, get_analytics_summary
import json

def run_qa():
    print("=== DP-700 QA START ===")
    
    # 1. API Keys
    keys = check_api_keys()
    print(f"API Keys Status: Gemini={keys['gemini']}, Groq={keys['groq']}")
    if not keys['gemini'] and not keys['groq']:
        print("ERROR: No API keys set. QA will fail.")
        return

    # 2. Database
    init_db()
    print("Database initialized.")

    # 3. LLM Engine - Chat
    print("Testing Chat Completion...")
    messages = [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": "Say 'hello world' and nothing else."}]
    
    res_gemini = chat_completion(messages, model_key="gemini", temperature=0)
    print(f"Gemini response ({res_gemini['model_used']}): {res_gemini['content']}")
    
    res_groq = chat_completion(messages, model_key="groq", temperature=0)
    print(f"Groq response ({res_groq['model_used']}): {res_groq['content']}")
    
    # 4. LLM Engine - Quiz
    print("Testing Quiz Generation...")
    prompt = "Create 2 multiple choice questions about data engineering in JSON format. The array must contain exactly 2 objects."
    quiz = generate_quiz_json(prompt, model_key="gemini")
    print(f"Generated {len(quiz)} quiz questions.")
    
    # 5. Voice TTS
    print("Testing TTS...")
    tts_result = text_to_speech("Hello from Fabric Prep")
    if isinstance(tts_result, tuple):
        audio_bytes, mime_type = tts_result
        print(f"TTS generated {len(audio_bytes) if audio_bytes else 0} bytes of audio ({mime_type}).")
    else:
        print(f"TTS generated {len(tts_result) if tts_result else 0} bytes of audio.")
    
    # STT requires an audio file, skipping STT direct test as it needs a WAV file.
    
    # 6. DB operations
    print("Testing Database operations...")
    save_journal_entry(1, "QA Note", "Testing the journal functionality.")
    summary = get_analytics_summary()
    print(f"Analytics Summary: {summary}")
    
    print("=== DP-700 QA COMPLETE ===")

if __name__ == "__main__":
    run_qa()
