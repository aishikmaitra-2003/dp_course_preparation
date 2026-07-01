"""
DP-700 Exam Prep — Flask API Backend
All AI, DB, and voice endpoints served here.
"""

import json
from flask import Flask, request, jsonify, send_file
import io
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import (
    init_db, save_journal_entry, get_journal_entries, delete_journal_entry,
    save_chat_message, get_chat_history, get_all_chat_history_for_quiz,
    clear_chat_history, save_quiz_result, get_quiz_results,
    update_progress, get_all_progress, get_module_progress,
    save_weakness, get_weaknesses, get_analytics_summary,
)
from ai.llm_engine import chat_completion, generate_quiz_json, analyze_weaknesses, check_api_keys
from ai.prompts import (
    TUTOR_SYSTEM_PROMPT, QUIZ_GENERATOR_PROMPT,
    WEAKNESS_ANALYZER_PROMPT, JOURNAL_SUMMARIZER_PROMPT,
)
from ai.voice import transcribe_audio, text_to_speech
from assets.exam_data import get_module, get_module_context, get_all_modules


def create_app():
    """Create and configure the Flask app."""
    app = Flask(__name__)

    # Initialize database
    init_db()

    # -----------------------------------------------------------------------
    # Health check
    # -----------------------------------------------------------------------
    @app.route("/api/health", methods=["GET"])
    def health():
        keys = check_api_keys()
        return jsonify({"status": "ok", "api_keys": keys})

    # -----------------------------------------------------------------------
    # Chat endpoint
    # -----------------------------------------------------------------------
    @app.route("/api/chat", methods=["POST"])
    def chat():
        data = request.json
        user_message = data.get("message", "")
        module_id = data.get("module_id", 1)
        model_key = data.get("model_key", None)

        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        # Get module context
        module_context = get_module_context(module_id)

        # Build messages with history
        history = get_chat_history(module_id, limit=20)
        messages = [
            {"role": "system", "content": TUTOR_SYSTEM_PROMPT + "\n\n" + module_context}
        ]
        for h in history:
            messages.append({"role": h["role"], "content": h["content"]})
        messages.append({"role": "user", "content": user_message})

        # Save user message
        save_chat_message(module_id, "user", user_message, "")

        # Get AI response
        result = chat_completion(messages, model_key=model_key)

        # Save assistant message
        save_chat_message(module_id, "assistant", result["content"], result["model_used"])

        # Update progress
        update_progress(module_id, status="in_progress", add_time_mins=1)

        return jsonify({
            "response": result["content"],
            "model_used": result["model_used"],
            "model_key": result["model_key"],
        })

    # -----------------------------------------------------------------------
    # Quiz endpoints
    # -----------------------------------------------------------------------
    @app.route("/api/quiz/generate", methods=["POST"])
    def generate_quiz():
        data = request.json
        module_id = data.get("module_id")
        num_questions = data.get("num_questions", 10)
        quiz_type = data.get("quiz_type", "module")
        model_key = data.get("model_key", None)

        # Get module context
        if quiz_type == "final":
            # Final exam: cover all modules
            context_parts = []
            for m in get_all_modules():
                context_parts.append(get_module_context(m["id"]))
            module_context = "\n\n".join(context_parts)
        else:
            module_context = get_module_context(module_id)

        # Get weakness areas
        weaknesses = get_weaknesses(module_id if quiz_type != "final" else None)
        weakness_text = ""
        if weaknesses:
            weakness_text = "\n\n## FOCUS ON THESE WEAK AREAS:\n"
            for w in weaknesses[:5]:
                weakness_text += f"- {w['topic']} (weakness score: {w['weakness_score']})\n"

        # Get chat history context
        chat_context = ""
        if module_id:
            user_msgs = get_all_chat_history_for_quiz(module_id)
            if user_msgs:
                chat_context = "\n\n## STUDENT'S QUESTIONS (focus on areas they struggled with):\n"
                chat_context += "\n".join(user_msgs[-10:])

        prompt = f"""{QUIZ_GENERATOR_PROMPT}

## MODULE CONTEXT:
{module_context}
{weakness_text}
{chat_context}

Generate exactly {num_questions} MCQ questions. Return ONLY a JSON array."""

        questions = generate_quiz_json(prompt, model_key=model_key)

        return jsonify({"questions": questions, "count": len(questions)})

    @app.route("/api/quiz/submit", methods=["POST"])
    def submit_quiz():
        data = request.json
        module_id = data.get("module_id")
        quiz_type = data.get("quiz_type", "module")
        answers = data.get("answers", {})  # {question_index: selected_option}
        questions = data.get("questions", [])

        if not questions:
            return jsonify({"error": "Questions data is required"}), 400

        # Score the quiz
        score = 0
        total = len(questions)
        wrong_topics = []

        for i, q in enumerate(questions):
            user_answer = answers.get(str(i), "")
            if user_answer == q.get("correct", ""):
                score += 1
            else:
                wrong_topics.append(q.get("topic", "unknown"))

        # Save result
        save_quiz_result(module_id, quiz_type, score, total, questions, wrong_topics)

        # Update weaknesses
        for topic in wrong_topics:
            save_weakness(
                module_id or 0, topic, 0.3,
                source=f"quiz_{quiz_type}"
            )

        # Mark module completed if score >= 70%
        if quiz_type == "module" and module_id and total > 0:
            pct = (score / total) * 100
            if pct >= 70:
                update_progress(module_id, status="completed")

        return jsonify({
            "score": score,
            "total": total,
            "percentage": round((score / total) * 100, 1) if total > 0 else 0,
            "wrong_topics": wrong_topics,
        })

    # -----------------------------------------------------------------------
    # Voice endpoints
    # -----------------------------------------------------------------------
    @app.route("/api/stt", methods=["POST"])
    def speech_to_text():
        if "audio" not in request.files:
            return jsonify({"error": "No audio file provided"}), 400

        audio_file = request.files["audio"]
        audio_bytes = audio_file.read()
        text = transcribe_audio(audio_bytes)
        return jsonify({"text": text})

    @app.route("/api/tts", methods=["POST"])
    def tts():
        data = request.json
        text = data.get("text", "")
        if not text:
            return jsonify({"error": "Text is required"}), 400

        audio_bytes = text_to_speech(text)
        if audio_bytes:
            return send_file(
                io.BytesIO(audio_bytes),
                mimetype="audio/mp3",
                as_attachment=False,
                download_name="response.mp3",
            )
        return jsonify({"error": "TTS failed"}), 500

    # -----------------------------------------------------------------------
    # Journal endpoints
    # -----------------------------------------------------------------------
    @app.route("/api/journal", methods=["GET"])
    def list_journal():
        module_id = request.args.get("module_id", type=int)
        entries = get_journal_entries(module_id)
        return jsonify({"entries": entries})

    @app.route("/api/journal", methods=["POST"])
    def create_journal():
        data = request.json
        entry_id = save_journal_entry(
            data.get("module_id", 0),
            data.get("title", "Untitled"),
            data.get("content", ""),
            data.get("entry_id"),
        )
        return jsonify({"id": entry_id, "status": "saved"})

    @app.route("/api/journal/<int:entry_id>", methods=["DELETE"])
    def remove_journal(entry_id):
        delete_journal_entry(entry_id)
        return jsonify({"status": "deleted"})

    @app.route("/api/journal/summarize", methods=["POST"])
    def summarize_journal():
        data = request.json
        content = data.get("content", "")
        model_key = data.get("model_key", None)

        result = chat_completion(
            messages=[
                {"role": "system", "content": JOURNAL_SUMMARIZER_PROMPT},
                {"role": "user", "content": f"Summarize these notes:\n\n{content}"},
            ],
            model_key=model_key,
        )
        return jsonify({"summary": result["content"]})

    # -----------------------------------------------------------------------
    # Progress & Analytics endpoints
    # -----------------------------------------------------------------------
    @app.route("/api/progress", methods=["GET"])
    def progress():
        all_progress = get_all_progress()
        return jsonify({"progress": all_progress})

    @app.route("/api/progress", methods=["PUT"])
    def update_prog():
        data = request.json
        update_progress(
            data.get("module_id"),
            status=data.get("status"),
            add_time_mins=data.get("add_time_mins", 0),
        )
        return jsonify({"status": "updated"})

    @app.route("/api/analytics", methods=["GET"])
    def analytics():
        summary = get_analytics_summary()
        quiz_data = get_quiz_results()
        weakness_data = get_weaknesses()
        progress_data = get_all_progress()
        return jsonify({
            "summary": summary,
            "quizzes": quiz_data,
            "weaknesses": weakness_data,
            "progress": progress_data,
        })

    @app.route("/api/weaknesses", methods=["GET"])
    def weaknesses_endpoint():
        module_id = request.args.get("module_id", type=int)
        data = get_weaknesses(module_id)
        return jsonify({"weaknesses": data})

    return app
