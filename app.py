import streamlit as st
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from stt import transcribe_audio
from intent import classify_intent
from tools import execute_action

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Voice AI Agent",
    page_icon="🎙️",
    layout="wide"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

* { font-family: 'IBM Plex Sans', sans-serif; }

.history-card {
    background: #0f0f0f;
    border: 1px solid #2a2a2a;
    border-left: 3px solid #00ff88;
    border-radius: 4px;
    padding: 14px 18px;
    margin-bottom: 12px;
}
.history-card .timestamp {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    color: #555;
    margin-bottom: 6px;
}
.history-card .transcript {
    font-size: 15px;
    color: #e0e0e0;
    margin-bottom: 8px;
    line-height: 1.5;
}
.history-card .intent-badge {
    display: inline-block;
    background: #1a1a2e;
    color: #00ff88;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    padding: 2px 8px;
    border-radius: 2px;
    margin-right: 6px;
    margin-bottom: 6px;
    border: 1px solid #00ff8855;
}
.history-card .action-line {
    font-size: 13px;
    color: #888;
    margin-top: 6px;
    font-family: 'IBM Plex Mono', monospace;
}
.history-card .action-line span { color: #00ccff; }

.empty-state {
    text-align: center;
    padding: 60px 20px;
    color: #444;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 13px;
    border: 1px dashed #222;
    border-radius: 4px;
}
.stat-box {
    background: #0f0f0f;
    border: 1px solid #1e1e1e;
    border-radius: 4px;
    padding: 16px;
    text-align: center;
}
.stat-box .num {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 28px;
    font-weight: 600;
    color: #00ff88;
}
.stat-box .label {
    font-size: 12px;
    color: #555;
    margin-top: 4px;
    text-transform: uppercase;
    letter-spacing: 1px;
}
</style>
""", unsafe_allow_html=True)

# ── Session state init ────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []  # list of run dicts


def add_to_history(transcript, intent_data, results):
    st.session_state.history.append({
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "date":      datetime.now().strftime("%b %d, %Y"),
        "transcript": transcript,
        "intents":   intent_data.get("intents", []),
        "params":    intent_data.get("params", {}),
        "results":   results,
    })


# ── Layout ────────────────────────────────────────────────────────────────────
st.markdown("## 🎙️ Voice AI Agent")
st.caption("Upload audio → transcribe → detect intent → execute action")
st.divider()

left, right = st.columns([1.1, 1], gap="large")

# ════════════════════════════════════════════════════════
# LEFT — Upload + Run
# ════════════════════════════════════════════════════════
with left:
    st.markdown("### Upload Audio")
    uploaded_file = st.file_uploader(
        "WAV, MP3, M4A, OGG, FLAC",
        type=["wav", "mp3", "m4a", "ogg", "flac"],
        label_visibility="collapsed"
    )

    if uploaded_file:
        st.audio(uploaded_file)

        if st.button("▶ Run Agent", use_container_width=True, type="primary"):
            audio_path = "temp_audio.mp3"
            with open(audio_path, "wb") as f:
                f.write(uploaded_file.read())

            with st.spinner("Processing..."):

                # Step 1 — STT
                with st.status("🔊 Transcribing audio..."):
                    text = transcribe_audio(audio_path)

                if not text or "[STT ERROR]" in text:
                    st.error(f"Transcription failed: {text}")
                    st.stop()

                st.subheader("📝 Transcript")
                st.info(text)

                # Step 2 — Intent
                with st.status("🧠 Detecting intent..."):
                    intent_data = classify_intent(text)

                st.subheader("🧠 Intent")
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Intents:**", ", ".join(intent_data.get("intents", [])))
                with col2:
                    params = intent_data.get("params", {})
                    st.write("**File:**",  params.get("filename") or "—")
                    st.write("**Lang:**",  params.get("language") or "—")

                # Step 3 — Execute
                with st.status("⚙️ Executing actions..."):
                    results = execute_action(
                        intent_data.get("intents", []),
                        intent_data.get("params", {}),
                        text
                    )

                st.subheader("⚙️ Results")
                for res in results:
                    with st.expander(f"{res['action']} — {res['message']}", expanded=True):
                        if res.get("preview"):
                            lang = "python" if res["action"] == "write_code" else "text"
                            st.code(res["preview"], language=lang)
                        if res.get("filename"):
                            file_path = OUTPUT_DIR / res["filename"]
                            if file_path.exists():
                                st.download_button(
                                    label=f"⬇️ Download {res['filename']}",
                                    data=file_path.read_bytes(),
                                    file_name=res["filename"],
                                )

                # ✅ Save run to history
                add_to_history(text, intent_data, results)
                st.toast("Added to history!", icon="✅")

# ════════════════════════════════════════════════════════
# RIGHT — Session History
# ════════════════════════════════════════════════════════
with right:
    history = st.session_state.history

    # Stats
    total     = len(history)
    n_code    = sum(1 for h in history if "write_code"  in h["intents"])
    n_file    = sum(1 for h in history if "create_file" in h["intents"])
    n_summary = sum(1 for h in history if "summarize"   in h["intents"])

    st.markdown("### Session History")

    s1, s2, s3, s4 = st.columns(4)
    for col, num, label in [
        (s1, total,     "Total"),
        (s2, n_code,    "Code"),
        (s3, n_file,    "Files"),
        (s4, n_summary, "Summaries"),
    ]:
        with col:
            st.markdown(f"""
            <div class="stat-box">
                <div class="num">{num}</div>
                <div class="label">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if history:
        if st.button("🗑 Clear History", use_container_width=True):
            st.session_state.history = []
            st.rerun()

    st.markdown("---")

    # Cards — newest first
    if not history:
        st.markdown("""
        <div class="empty-state">
            no history yet<br><br>
            run your first voice command →
        </div>""", unsafe_allow_html=True)
    else:
        for entry in reversed(history):
            intent_badges = "".join(
                f'<span class="intent-badge">{i}</span>'
                for i in entry["intents"]
            )
            action_lines = "".join(
                f'<div class="action-line">↳ <span>{r["action"]}</span> — {r["message"]}</div>'
                for r in entry["results"]
            )
            fname = entry["params"].get("filename") or ""
            fname_html = (
                f' &nbsp;·&nbsp; <span style="color:#555;font-family:monospace;font-size:11px">{fname}</span>'
                if fname else ""
            )
            preview = entry["transcript"]
            short   = preview[:120] + ("..." if len(preview) > 120 else "")

            st.markdown(f"""
            <div class="history-card">
                <div class="timestamp">{entry["date"]} &nbsp;·&nbsp; {entry["timestamp"]}{fname_html}</div>
                <div class="transcript">"{short}"</div>
                {intent_badges}
                {action_lines}
            </div>""", unsafe_allow_html=True)

