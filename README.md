# Spidey AI 🕷️🤖

An intelligent, multi-modal AI desktop assistant featuring voice interaction, real-time screen analysis, gesture diagnostics, facial recognition security, desktop HUD, and multi-model AI routing (Gemini, Groq, OpenRouter).

---

## 🚀 Features

- **Multi-Model AI Router**: Seamless routing across Gemini, Groq, and OpenRouter with streaming responses.
- **Interactive Desktop HUD**: Modern web and native GUI HUD displaying assistant status, responses, and audio visualization.
- **Vision & Screen Analysis**: Real-time screen analysis, OCR, visual reasoning, and desktop automation.
- **Face Recognition Security**: Embedded face detection (YuNet) and recognition (SFace) profile matching.
- **Hand Gesture Recognition**: Gesture diagnostics and quick-action controls.
- **Alarm & Productivity Suite**: Smart alarm manager, task tracking, and email rewriter.
- **Voice Engine**: Wake-word listening, push-to-talk, Edge TTS, and Windows voice synthesis.

---

## 🛠️ Getting Started

### 1. Prerequisites
- Python 3.10+
- Git

### 2. Setup Environment
```bash
python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt
```

### 3. Configure API Keys
Copy `.env.example` to `.env` and fill in your API credentials:
```bash
cp .env.example .env
```

```env
GEMINI_API_KEY=your_gemini_key
GROQ_API_KEY=your_groq_key
OPENROUTER_API_KEY=your_openrouter_key
```

### 4. Running the Assistant
```bash
python main.py
```

---

## 📂 Project Structure

- `main.py`: Core application loop, wake-word listener, and event orchestration.
- `ai_router.py`: LLM routing logic for Gemini, Groq, and OpenRouter.
- `screen_analyzer.py`: Vision & screen capture processing.
- `alarm_manager.py`: Alarm and timer management.
- `productivity.py`: Productivity hooks and email assistance.
- `spidey_desktop_hud.py` / `spidey_web/`: HUD frontend and visualization.
- `face_security.py` / `enroll_face.py`: Face security modules with ONNX models.
- `models/`: ONNX models for face detection/recognition and MediaPipe hand landmarker.

---

## 📄 License
MIT License
