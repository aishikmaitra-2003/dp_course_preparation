# 🚀 FabricPrep — DP-700 Exam Prep App

**AI-powered study buddy for the Microsoft DP-700: Implementing Data Engineering Solutions Using Microsoft Fabric certification.**

Crack the exam in 10 days with a GenZ-energy AI tutor, voice bot, smart journal, and adaptive quizzes!

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 **AI Tutor** | Chat with DP_Bot — powered by Gemini & Groq via LiteLLM |
| 🎙️ **Voice Bot** | Speak your questions, hear AI answers (Groq Whisper + gTTS) |
| 📝 **Journal** | Markdown notes per module with AI summarization |
| 🧪 **Quiz Engine** | AI-generated MCQs targeting your weak areas |
| 📚 **Study Plan** | 10-day structured plan mapped to exam syllabus |
| 📊 **Analytics** | Score trends, weakness heatmap, exam readiness score |
| 🏆 **Final Mock Exam** | Full-length timed practice exam |

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Backend**: Flask (runs as background thread)
- **AI Layer**: LiteLLM (Gemini + Groq)
- **Voice**: Groq Whisper (STT) + gTTS (TTS)
- **Database**: SQLite
- **Charts**: Plotly
- **Deployment**: Streamlit Cloud

## 🚀 Quick Start

```bash
# 1. Clone and enter the project
cd DP700

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up API keys (copy .env.example to .env and fill in)
cp .env.example .env

# 4. Run the app
streamlit run streamlit_app.py
```

## 🔑 API Keys (Both FREE!)

| Provider | Get Key | Used For |
|----------|---------|----------|
| **Gemini** | [Google AI Studio](https://aistudio.google.com/apikey) | AI Tutor, Quiz Generation |
| **Groq** | [Groq Console](https://console.groq.com/keys) | Fast AI + Voice Transcription |

## ☁️ Deploy to Streamlit Cloud

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Deploy with `streamlit_app.py` as main file
4. Add secrets in dashboard:
   ```toml
   GEMINI_API_KEY = "your-key"
   GROQ_API_KEY = "your-key"
   ```

## 📁 Project Structure

```
DP700/
├── streamlit_app.py          # Main entry
├── pages/                    # Streamlit pages
│   ├── 1_📚_Study_Plan.py
│   ├── 2_🤖_AI_Tutor.py
│   ├── 3_🎙️_Voice_Bot.py
│   ├── 4_📝_Journal.py
│   ├── 5_🧪_Quiz.py
│   ├── 6_📊_Analytics.py
│   └── 7_⚙️_Settings.py
├── ai/                       # AI layer
│   ├── llm_engine.py         # LiteLLM wrapper
│   ├── prompts.py            # System prompts
│   └── voice.py              # STT/TTS
├── backend/                  # Flask API
│   ├── app.py                # Endpoints
│   └── server.py             # Thread launcher
├── database/
│   └── db.py                 # SQLite manager
├── assets/
│   ├── style.css             # Dark theme CSS
│   └── exam_data.py          # DP-700 syllabus
└── requirements.txt
```

---

**Built with 💜 for aspiring Fabric Data Engineers**
