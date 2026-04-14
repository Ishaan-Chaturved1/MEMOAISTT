from groq import Groq
import json
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))

SYSTEM_PROMPT = """
Classify the user's intent from their voice command.

Return ONLY valid JSON with no extra text, no markdown, no explanation:
{
  "intents": [],
  "params": {
    "filename": null,
    "language": null,
    "description": ""
  }
}

Available intents:
- create_file     → user wants to create/save a text file
- write_code      → user wants to generate code
- summarize       → user wants a summary
- general_chat    → anything else

Rules:
- "intents" must be a non-empty list
- "filename" should be extracted from the user's words if mentioned (e.g. "save as notes.txt" → "notes.txt"), otherwise null
- "language" should be extracted if a programming language is mentioned, otherwise null
- "description" should capture the core task in a short phrase
"""


def classify_intent(text: str) -> dict:
    try:
        chat = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ],
            max_tokens=200,
            temperature=0.1
        )

        response = chat.choices[0].message.content.strip()

        # Strip markdown code fences if model wraps in ```json ... ```
        if response.startswith("```"):
            response = response.split("```")[1]
            if response.startswith("json"):
                response = response[4:]
            response = response.strip()

        return json.loads(response)

    except Exception as e:
        print(f"[Intent Error] {e}")
        return _fallback(text)


def _fallback(text: str) -> dict:
    t = text.lower()
    intents = []

    if any(w in t for w in ["create", "make", "write", "save", "file"]):
        intents.append("create_file")

    if any(w in t for w in ["code", "python", "javascript", "function", "script", "program"]):
        # Replace create_file with write_code if code-related
        intents = [i for i in intents if i != "create_file"]
        intents.append("write_code")

    if any(w in t for w in ["summarize", "summary", "summarise"]):
        intents.append("summarize")

    if not intents:
        intents = ["general_chat"]

    return {
        "intents": intents,
        "params": {
            "filename": None,
            "language": "python" if "python" in t else None,
            "description": text
        }
    }