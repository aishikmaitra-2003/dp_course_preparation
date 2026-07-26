"""
🧪 Quiz Engine — Module Quizzes & Final Mock Exam
AI-generated MCQs based on your chat history and weakness areas.
"""

import streamlit as st
import requests
import json
import time
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
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #f1f5f9 0%, #e2e8f0 100%) !important; }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: #1e293b !important; }
    .stMarkdown p, .stCaption p { color: #475569 !important; }
    .stTabs [data-baseweb="tab-list"] { background: #f1f5f9 !important; }
    .stTabs [data-baseweb="tab"] { color: #475569 !important; }
    .stRadio label { color: #1e293b !important; }
    [data-testid="stExpander"] { background: rgba(255,255,255,0.85) !important; border: 1px solid rgba(0,0,0,0.08) !important; }
    </style>""", unsafe_allow_html=True)

if "current_module" not in st.session_state:
    st.session_state.current_module = 1
if "quiz_state" not in st.session_state:
    st.session_state.quiz_state = "setup"  # setup, active, results
if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = []
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}
if "quiz_start_time" not in st.session_state:
    st.session_state.quiz_start_time = None
if "quiz_result" not in st.session_state:
    st.session_state.quiz_result = None

st.markdown(
    """<h1 style='background: linear-gradient(135deg, #2563eb, #06b6d4);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    font-weight: 800;'>🧪 Quiz Engine</h1>""",
    unsafe_allow_html=True,
)
st.markdown('<div class="header-line"></div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# SETUP STATE — Choose quiz type
# ---------------------------------------------------------------------------
if st.session_state.quiz_state == "setup":
    st.caption("Test your knowledge with AI-generated questions based on your study progress! 🧠")

    tab_module, tab_final = st.tabs(["📚 Module Quiz", "🏆 Final Mock Exam"])

    with tab_module:
        st.markdown("### 📚 Module Quiz")
        st.markdown("10 MCQs focused on a specific module. Questions are personalized based on your chat history and weak areas.")

        modules = get_all_modules()
        module_options = {f"Day {m['day']}: {m['icon']} {m['title']}": m["id"] for m in modules if m["id"] <= 9}
        selected = st.selectbox(
            "Select Module",
            options=list(module_options.keys()),
            index=min(max(st.session_state.current_module - 1, 0), len(module_options) - 1),
        )
        module_id = module_options[selected]

        num_q = st.slider("Number of Questions", 5, 20, 10, key="num_q_module")

        # Show previous quiz results for this module
        try:
            quiz_hist = requests.get(f"{API_URL}/api/analytics", timeout=5).json()
            past_quizzes = [
                q for q in quiz_hist.get("quizzes", [])
                if q.get("module_id") == module_id and q.get("quiz_type") == "module"
            ]
            if past_quizzes:
                st.markdown("#### 📊 Past Attempts")
                for pq in past_quizzes[:3]:
                    pct = round((pq["score"] / pq["total"]) * 100, 1) if pq["total"] > 0 else 0
                    color = "#10b981" if pct >= 70 else "#f59e0b" if pct >= 50 else "#f43f5e"
                    st.markdown(
                        f"<span style='color:{color}; font-weight:700;'>{pct}%</span> "
                        f"({pq['score']}/{pq['total']}) — {pq.get('timestamp', '')[:16]}",
                        unsafe_allow_html=True,
                    )
        except Exception:
            pass

        if st.button("🚀 Generate Quiz", use_container_width=True, type="primary", key="gen_module"):
            with st.spinner("🧑‍🍳 DP_Bot is cooking up questions based on your weak spots..."):
                try:
                    resp = requests.post(
                        f"{API_URL}/api/quiz/generate",
                        json={
                            "module_id": module_id,
                            "num_questions": num_q,
                            "quiz_type": "module",
                        },
                        timeout=90,
                    ).json()
                    questions = resp.get("questions", [])
                    if questions:
                        st.session_state.quiz_questions = questions
                        st.session_state.quiz_answers = {}
                        st.session_state.quiz_state = "active"
                        st.session_state.quiz_type = "module"
                        st.session_state.quiz_module_id = module_id
                        st.session_state.quiz_start_time = time.time()
                        st.rerun()
                    else:
                        st.error("Failed to generate questions. Check your API keys in ⚙️ Settings!")
                except Exception as e:
                    st.error(f"Error: {e}")

    with tab_final:
        st.markdown("### 🏆 Final Mock Exam")
        st.markdown(
            f"""<div style='background: linear-gradient(135deg, rgba(245,158,11,0.1), rgba(244,63,94,0.1));
            border: 1px solid rgba(245,158,11,0.3); border-radius: 12px; padding: 1.2rem;'>
            <strong style='color: #f59e0b;'>⚠️ This is the real deal!</strong>
            <p style='color: {text_secondary}; margin-top: 0.5rem;'>
            60 questions covering ALL modules. Timed at 90 minutes.<br>
            This simulates the actual DP-700 exam experience. Take it when you've completed all 9 study modules!
            </p></div>""",
            unsafe_allow_html=True,
        )

        st.markdown("")
        num_q_final = st.slider("Number of Questions", 20, 60, 40, key="num_q_final")

        if st.button("🏆 Start Final Exam", use_container_width=True, type="primary", key="gen_final"):
            with st.spinner("🔥 Generating comprehensive exam from ALL modules..."):
                try:
                    resp = requests.post(
                        f"{API_URL}/api/quiz/generate",
                        json={
                            "module_id": None,
                            "num_questions": num_q_final,
                            "quiz_type": "final",
                        },
                        timeout=120,
                    ).json()
                    questions = resp.get("questions", [])
                    if questions:
                        st.session_state.quiz_questions = questions
                        st.session_state.quiz_answers = {}
                        st.session_state.quiz_state = "active"
                        st.session_state.quiz_type = "final"
                        st.session_state.quiz_module_id = None
                        st.session_state.quiz_start_time = time.time()
                        st.rerun()
                    else:
                        st.error("Failed to generate exam. Check your API keys!")
                except Exception as e:
                    st.error(f"Error: {e}")

# ---------------------------------------------------------------------------
# ACTIVE STATE — Taking the quiz
# ---------------------------------------------------------------------------
elif st.session_state.quiz_state == "active":
    questions = st.session_state.quiz_questions
    quiz_type = st.session_state.get("quiz_type", "module")
    total = len(questions)

    # Timer
    if st.session_state.quiz_start_time:
        elapsed = time.time() - st.session_state.quiz_start_time
        time_limit = 90 * 60 if quiz_type == "final" else 30 * 60
        remaining = max(0, time_limit - elapsed)
        mins, secs = divmod(int(remaining), 60)

        timer_color = "#10b981" if remaining > 300 else "#f59e0b" if remaining > 60 else "#f43f5e"
        st.markdown(
            f"""<div style='text-align: right; padding: 0.5rem;'>
            <span style='color: {timer_color}; font-weight: 700; font-size: 1.2rem;'>
            ⏱️ {mins:02d}:{secs:02d}</span>
            <span style='color: {text_muted};'> remaining</span></div>""",
            unsafe_allow_html=True,
        )

    # Progress
    answered = len(st.session_state.quiz_answers)
    st.progress(answered / total, text=f"Answered: {answered}/{total}")

    st.markdown(f"### {'🏆 Final Mock Exam' if quiz_type == 'final' else '📚 Module Quiz'}")

    # Questions
    for i, q in enumerate(questions):
        difficulty_badge = {
            "easy": ("🟢", "rgba(16,185,129,0.15)", "#10b981"),
            "medium": ("🟡", "rgba(245,158,11,0.15)", "#f59e0b"),
            "hard": ("🔴", "rgba(244,63,94,0.15)", "#f43f5e"),
        }.get(q.get("difficulty", "medium"), ("🟡", "rgba(245,158,11,0.15)", "#f59e0b"))

        st.markdown(
            f"""<div style='background: {bg_card}; border: 1px solid {border_color};
            border-radius: 12px; padding: 1.2rem; margin: 0.8rem 0;'>
            <div style='display: flex; justify-content: space-between;'>
                <span style='font-weight: 700; color: {text_primary};'>Q{i+1}.</span>
                <span style='background: {difficulty_badge[1]}; color: {difficulty_badge[2]};
                padding: 2px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 600;'>
                {difficulty_badge[0]} {q.get('difficulty', 'medium').upper()}</span>
            </div>
            <div style='color: {text_primary}; margin-top: 0.5rem;'>{q.get('question', '')}</div>
            </div>""",
            unsafe_allow_html=True,
        )

        options = q.get("options", [])
        answer = st.radio(
            f"Select answer for Q{i+1}",
            options=options,
            key=f"q_{i}",
            index=None,
            label_visibility="collapsed",
        )
        if answer:
            # Extract letter (e.g., "A" from "A) option text")
            letter = answer.split(")")[0].strip()
            st.session_state.quiz_answers[str(i)] = letter

    st.markdown("")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📤 Submit Quiz", use_container_width=True, type="primary"):
            if len(st.session_state.quiz_answers) < total:
                st.warning(f"You've answered {len(st.session_state.quiz_answers)}/{total}. Unanswered questions will be marked wrong.")

            with st.spinner("Scoring your quiz... 📊"):
                try:
                    resp = requests.post(
                        f"{API_URL}/api/quiz/submit",
                        json={
                            "module_id": st.session_state.get("quiz_module_id"),
                            "quiz_type": quiz_type,
                            "answers": st.session_state.quiz_answers,
                            "questions": questions,
                        },
                        timeout=15,
                    ).json()
                    st.session_state.quiz_result = resp
                    st.session_state.quiz_state = "results"
                    st.rerun()
                except Exception as e:
                    st.error(f"Submission error: {e}")

    with col2:
        if st.button("❌ Cancel Quiz", use_container_width=True):
            st.session_state.quiz_state = "setup"
            st.session_state.quiz_questions = []
            st.session_state.quiz_answers = {}
            st.rerun()

# ---------------------------------------------------------------------------
# RESULTS STATE — Show score and analysis
# ---------------------------------------------------------------------------
elif st.session_state.quiz_state == "results":
    result = st.session_state.quiz_result
    questions = st.session_state.quiz_questions

    score = result.get("score", 0)
    total = result.get("total", 1)
    pct = result.get("percentage", 0)
    wrong_topics = result.get("wrong_topics", [])

    # Score banner
    if pct >= 70:
        grade_color = "#10b981"
        grade_emoji = "🎉"
        grade_msg = "PASSED! You're crushing it fam! No cap, you're certified material! 💪"
    elif pct >= 50:
        grade_color = "#f59e0b"
        grade_emoji = "😤"
        grade_msg = "Almost there bro! Review the weak spots and try again. You got this!"
    else:
        grade_color = "#f43f5e"
        grade_emoji = "📚"
        grade_msg = "Time to grind harder bachcho! Review the topics below and hit the AI Tutor."

    st.markdown(
        f"""<div style='text-align: center; padding: 2rem;
        background: linear-gradient(135deg, {grade_color}15, {grade_color}05);
        border: 2px solid {grade_color}40; border-radius: 20px;'>
        <div style='font-size: 3rem;'>{grade_emoji}</div>
        <div style='font-size: 3rem; font-weight: 800; color: {grade_color};'>{pct}%</div>
        <div style='font-size: 1.2rem; color: {text_primary}; margin-top: 0.5rem;'>{score}/{total} correct</div>
        <div style='color: {text_secondary}; margin-top: 0.5rem;'>{grade_msg}</div>
        </div>""",
        unsafe_allow_html=True,
    )

    st.markdown("")

    # Weakness areas
    if wrong_topics:
        st.markdown("### ⚠️ Areas to Improve")
        topic_counts = {}
        for t_topic in wrong_topics:
            topic_counts[t_topic] = topic_counts.get(t_topic, 0) + 1

        for topic, count in sorted(topic_counts.items(), key=lambda x: -x[1]):
            st.markdown(
                f"""<div style='background: rgba(244,63,94,0.1); border: 1px solid rgba(244,63,94,0.2);
                border-radius: 8px; padding: 0.5rem 1rem; margin: 0.3rem 0;'>
                <span style='color: #f43f5e; font-weight: 600;'>❌ {topic}</span>
                <span style='color: {text_muted}; float: right;'>{count} wrong</span></div>""",
                unsafe_allow_html=True,
            )

    st.markdown("")

    # Answer review
    st.markdown("### 📋 Answer Review")
    for i, q in enumerate(questions):
        user_ans = st.session_state.quiz_answers.get(str(i), "—")
        correct_ans = q.get("correct", "")
        is_correct = user_ans == correct_ans

        icon = "✅" if is_correct else "❌"

        with st.expander(f"{icon} Q{i+1}: {q.get('question', '')[:80]}..."):
            st.markdown(f"**Question:** {q.get('question', '')}")
            st.markdown("")
            for opt in q.get("options", []):
                opt_letter = opt.split(")")[0].strip()
                if opt_letter == correct_ans:
                    st.markdown(f"✅ **{opt}**")
                elif opt_letter == user_ans and not is_correct:
                    st.markdown(f"❌ ~~{opt}~~")
                else:
                    st.markdown(f"  {opt}")
            st.markdown("")
            st.info(f"💡 **Explanation:** {q.get('explanation', 'No explanation available')}")

    st.markdown("")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Take Another Quiz", use_container_width=True, type="primary"):
            st.session_state.quiz_state = "setup"
            st.session_state.quiz_questions = []
            st.session_state.quiz_answers = {}
            st.session_state.quiz_result = None
            st.rerun()
    with col2:
        if st.button("🤖 Study Weak Areas with AI", use_container_width=True):
            if wrong_topics:
                st.session_state.pending_prompt = (
                    f"I just took a quiz and got these topics wrong: {', '.join(set(wrong_topics))}. "
                    f"Help me understand these concepts better!"
                )
            st.switch_page("pages/2_🤖_AI_Tutor.py")
