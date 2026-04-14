# Voice AI Agent

## Overview

This project is a voice-controlled AI agent that converts spoken commands into executable actions such as generating code, creating files, and summarizing text.

It integrates speech-to-text, intent detection, and tool execution into a single pipeline with a simple web interface.

---

## Architecture

Audio Input → Speech-to-Text → Intent Detection → Tool Execution → Output

---

## Components

* Speech-to-Text: AssemblyAI API
* Language Model: Groq API (llama-3.1-8b-instant)
* Frontend: Streamlit
* Backend Logic: Python-based agent with modular tools

---

## Features

* Voice input through audio upload
* Multi-intent detection (compound commands)
* Code generation and file creation
* Text summarization
* Human-in-the-loop confirmation before file operations
* Graceful error handling
* Session memory with history tracking
* File download support

---

## Example Flow

User Input:
"Create a Python file with a retry function"

System Execution:

1. Audio is transcribed using AssemblyAI
2. Intent is detected as `write_code` and `create_file`
3. Python code is generated using Groq
4. File is created in the `output/` directory
5. UI displays transcript, intent, and execution result

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone <your-repository-link>
cd memoAISTT
```

---

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 3. Configure API Keys

Update the following files:

In `stt.py`:

```python
aai.settings.api_key = "YOUR_ASSEMBLYAI_API_KEY"
```

In `intent.py` and `tools.py`:

```python
from groq import Groq
client = Groq(api_key="YOUR_GROQ_API_KEY")
```

---

### 4. Run the application

```bash
streamlit run app.py
```

Then open the local URL in your browser.

---

## Project Structure

```
memoAISTT/
├── app.py
├── stt.py
├── intent.py
├── tools.py
├── requirements.txt
├── README.md
└── output/
```

---

## Speech-to-Text and Model Choices

### Initial Approach (Local Models)

The initial design used local models:

* HuggingFace Whisper for speech-to-text
* Ollama for intent detection and code generation

However, several issues were encountered:

* FFmpeg setup problems on Windows
* High memory usage and instability
* Slow inference on CPU-only systems
* Frequent crashes during integration

---

### Final Approach (API-based Models)

Based on developer discussions (including Reddit) and practical constraints, the system was migrated to API-based solutions.

#### AssemblyAI (Speech-to-Text)

* Fast and accurate transcription
* Free tier available
* No dependency on local hardware
* Eliminates setup complexity

#### Groq API (Language Model)

* Very fast inference
* No hardware requirements
* Stable and reliable responses
* Suitable for real-time applications

---

### Reasoning

This approach was chosen to:

* Ensure smooth execution on standard machines
* Avoid environment and dependency issues
* Improve speed and responsiveness
* Focus on agent functionality rather than infrastructure

While local models offer more control, API-based solutions are often preferred in production due to their scalability and reliability.

---

## Hardware Notes

* The system runs on CPU-only machines without requiring GPU support
* No need for FFmpeg or CUDA setup
* Suitable for laptops with limited resources

---

## Challenges Faced

* Setting up local STT (Whisper) with FFmpeg on Windows
* Managing memory constraints with local LLMs
* Handling inconsistent JSON responses from LLMs
* Debugging silent failures in Streamlit
* Managing model deprecations in Groq

---

## Bonus Features Implemented

* Compound command handling (multiple intents in one input)
* Human-in-the-loop confirmation for file operations
* Graceful fallback when intent detection fails
* Session memory for tracking interactions

---

## Future Improvements

* Real-time microphone input
* Persistent memory across sessions
* Streaming responses
* Enhanced UI and visualization
* Support for additional tools and actions

---

## Conclusion

This project demonstrates how speech processing, language models, and tool execution can be combined to build an intelligent agent system.

It highlights practical tradeoffs between local and API-based models, and focuses on delivering a stable and responsive user experience.

---
