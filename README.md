# 🎙️ VoiceAgent — Local AI Voice-Controlled Agent

A fully local, privacy-first AI agent that listens to your voice, understands your intent, and executes actions on your machine — all without sending data to the cloud.

```
Audio Input → Whisper STT → Ollama LLM → Tool Execution → Streamlit UI
```

---

## ✨ Features

| Feature | Details |
|---|---|
| **Speech-to-Text** | HuggingFace Whisper (local, CPU/GPU) |
| **Intent Classification** | Ollama LLM (llama3, mistral, phi3, …) |
| **Supported Intents** | `create_file`, `write_code`, `summarize`, `general_chat` |
| **Compound Commands** | "Write a retry function *and* summarize it" |
| **Human-in-the-Loop** | Confirm before any file/code operation |
| **Graceful Degradation** | Keyword fallback if LLM JSON fails |
| **Session Memory** | History panel in sidebar |
| **Safe Output** | All file ops restricted to `output/` folder |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit UI (app.py)                 │
│  ┌──────────┐   ┌──────────┐   ┌──────────────────────┐ │
│  │  Audio   │   │  Text    │   │   Pipeline Display    │ │
│  │  Upload  │   │ Override │   │  STT→Intent→Action   │ │
│  └────┬─────┘   └────┬─────┘   └──────────────────────┘ │
└───────┼──────────────┼──────────────────────────────────┘
        │              │
        ▼              ▼
┌──────────────────────────┐
│       stt.py             │
│  HuggingFace Whisper     │
│  (openai/whisper-base)   │
│  Runs 100% locally       │
└──────────────────────────┘
        │
        ▼ transcript (str)
┌──────────────────────────┐
│       intent.py          │
│  Ollama REST API         │
│  → Structured JSON       │
│  { intents, params,      │
│    reasoning }           │
└──────────────────────────┘
        │
        ▼ intents + params
┌──────────────────────────────────────────────────┐
│                   tools.py                        │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  │
│  │ write_code │  │ create_file│  │ summarize  │  │
│  │ (Ollama)   │  │ (template) │  │ (Ollama)   │  │
│  └────────────┘  └────────────┘  └────────────┘  │
│  ┌────────────┐                                   │
│  │general_chat│  All file I/O → output/ only      │
│  │ (Ollama)   │                                   │
│  └────────────┘                                   │
└──────────────────────────────────────────────────┘
        │
        ▼
   output/ folder
```

---

## 🚀 Quick Start

### 1. Prerequisites

- **Python 3.10+**
- **Ollama** installed and running
- **ffmpeg** for audio decoding

```bash
# Install ffmpeg (Ubuntu/Debian)
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows — download from https://ffmpeg.org/download.html
```

### 2. Install Ollama & pull a model

```bash
# Install Ollama: https://ollama.com
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model (llama3 recommended)
ollama pull llama3

# Start the server (runs on localhost:11434)
ollama serve
```

### 3. Clone & install Python dependencies

```bash
git clone https://github.com/YOUR_USERNAME/voice-agent.git
cd voice-agent

python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

> **Note on torch**: If you only have CPU, the above installs the default torch.
> For CUDA GPU acceleration: `pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121`

### 4. Run the app

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🎮 Usage Examples

### Example 1 — Write Code
> "Create a Python file with a retry decorator function"

Pipeline:
1. Whisper transcribes the audio
2. Ollama detects: `write_code + create_file`
3. Generates Python code with a `retry` decorator
4. Saves to `output/retry_decorator.py`

### Example 2 — Summarize
> "Summarize this article: AI is transforming healthcare..."

Pipeline:
1. Transcription extracted
2. Intent: `summarize`
3. Ollama produces a bullet-point summary
4. Optionally saved to `output/summary.txt`

### Example 3 — Compound Command
> "Write a JavaScript fetch wrapper and summarize what it does"

Pipeline:
1. Intent: `write_code + summarize`
2. Generates the JS code → `output/fetch_wrapper.js`
3. Summarizes the code → displayed in UI

### Example 4 — General Chat
> "What's the difference between async and threading in Python?"

Pipeline:
1. Intent: `general_chat`
2. Ollama answers conversationally in the UI

---

## 🧩 Project Structure

```
voice-agent/
├── app.py            # Streamlit UI — pipeline orchestration
├── stt.py            # HuggingFace Whisper STT
├── intent.py         # Ollama intent classifier
├── tools.py          # Tool execution (file ops, code gen, summarize, chat)
├── requirements.txt
├── output/           # ← All generated files go here (safe zone)
└── README.md
```

---

## ⚙️ Configuration

All settings are adjustable from the sidebar at runtime:

| Setting | Default | Options |
|---|---|---|
| Ollama Model | `llama3` | llama3.2, mistral, phi3, gemma2 |
| Whisper Model | `whisper-base` | whisper-small, whisper-medium |
| Human-in-the-Loop | `ON` | Toggle off for auto-execute |

---

## 🔧 Hardware Notes & Workarounds

### STT — Whisper (local HuggingFace)
- **`whisper-base`** (~150MB): Works on any modern CPU. ~5–15s per 10s of audio.
- **`whisper-small`** (~250MB): Better accuracy, ~10–25s on CPU.
- **GPU (CUDA)**: Detected automatically — drops latency to <3s.
- If your machine is too slow: switch to **Groq Whisper API** by replacing `stt.py`'s `_pipeline` call with a Groq API request. Document this in your own README copy.

### LLM — Ollama
- **llama3** (8B): ~4–8GB RAM. Works well on most laptops.
- **phi3-mini**: ~2GB RAM. Good for constrained machines.
- Ollama must be running (`ollama serve`) before launching the app.

---

## 🎁 Bonus Features Implemented

- [x] **Compound Commands** — Multiple intents in one utterance
- [x] **Human-in-the-Loop** — Confirmation prompt before file ops
- [x] **Graceful Degradation** — Keyword fallback if LLM JSON parse fails; error cards in UI
- [x] **Session Memory** — Sidebar history panel with last 8 interactions
- [x] **Text Override** — Type commands directly (no mic needed for testing)

---

## 📝 Notes for Article / README

### Model Choices

| Component | Model | Why |
|---|---|---|
| STT | `openai/whisper-base` | Best accuracy/speed tradeoff locally; multilingual |
| LLM | `llama3` (8B via Ollama) | Strong instruction following; fast on CPU/GPU; fully local |

### Challenges Faced
1. **JSON reliability from LLM**: Small models sometimes wrap JSON in markdown fences or add preamble text. Solved with regex extraction + keyword fallback.
2. **Audio format diversity**: Used `librosa` + `soundfile` to handle wav/mp3/m4a/ogg uniformly.
3. **Compound intent ordering**: Write_code implicitly creates a file — needed deduplication logic in `execute_action`.

---

## 📄 License

MIT — use freely, build boldly.
