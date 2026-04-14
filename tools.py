from groq import Groq
from pathlib import Path
import os
import re

client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)


def generate_code(prompt: str, language: str = "Python") -> str:
    chat = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    f"You are a coding assistant. Write clean, working {language} code only. "
                    "No explanations, no markdown fences, just raw code."
                )
            },
            {"role": "user", "content": prompt}
        ],
        max_tokens=1024,
        temperature=0.2
    )
    code = chat.choices[0].message.content.strip()

    # Strip accidental markdown fences
    if code.startswith("```"):
        code = re.sub(r"^```[a-zA-Z]*\n?", "", code)
        code = re.sub(r"```$", "", code).strip()

    return code


def summarize_text(text: str) -> str:
    chat = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "Summarize the following text concisely."},
            {"role": "user", "content": text}
        ],
        max_tokens=300,
        temperature=0.3
    )
    return chat.choices[0].message.content.strip()


def execute_action(intents: list, params: dict, text: str) -> list:
    results = []

    # ── write_code ────────────────────────────────────────────────────────────
    if "write_code" in intents:
        language = params.get("language") or "Python"
        filename = params.get("filename") or "generated.py"

        # Ensure correct extension
        ext_map = {
            "python": ".py", "javascript": ".js", "typescript": ".ts",
            "java": ".java", "cpp": ".cpp", "c": ".c", "bash": ".sh",
        }
        expected_ext = ext_map.get(language.lower(), ".py")
        if not filename.endswith(expected_ext):
            filename = Path(filename).stem + expected_ext

        description = params.get("description") or text
        code = generate_code(f"Write {language} code for: {description}", language)

        path = OUTPUT_DIR / filename
        path.write_text(code, encoding="utf-8")

        results.append({
            "action": "write_code",
            "filename": filename,
            "message": f"✅ Code saved to `output/{filename}`",
            "preview": code[:300] + ("..." if len(code) > 300 else "")
        })

    # ── create_file (only when not write_code) ────────────────────────────────
    elif "create_file" in intents:
        filename = params.get("filename") or "file.txt"
        content = params.get("description") or text

        path = OUTPUT_DIR / filename
        path.write_text(content, encoding="utf-8")

        results.append({
            "action": "create_file",
            "filename": filename,
            "message": f"✅ File saved to `output/{filename}`",
            "preview": content[:300]
        })

    # ── summarize ─────────────────────────────────────────────────────────────
    if "summarize" in intents:
        summary = summarize_text(text)
        results.append({
            "action": "summarize",
            "filename": None,
            "message": "✅ Summary generated",
            "preview": summary
        })

    # ── general_chat ──────────────────────────────────────────────────────────
    if not results or intents == ["general_chat"]:
        results.append({
            "action": "general_chat",
            "filename": None,
            "message": "💬 No file action taken — general conversation detected",
            "preview": text
        })

    return results