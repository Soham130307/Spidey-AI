from pathlib import Path

p = Path("main.py")
s = p.read_text(encoding="utf-8")

# ------------------------------------------------------------
# 1. Replace Ollama import with Gemini
# ------------------------------------------------------------

if "import ollama" not in s:
    raise SystemExit("Could not find 'import ollama'")

s = s.replace(
    "import ollama",
    "from google import genai",
    1
)

# ------------------------------------------------------------
# 2. Add Gemini client after MODEL setting
# ------------------------------------------------------------

old = 'MODEL = "llama3.2:3b"'

new = '''GEMINI_MODEL = "gemini-3.8-flash"

gemini_client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)'''

if old not in s:
    raise SystemExit("MODEL line not found")

s = s.replace(old, new, 1)

# ------------------------------------------------------------
# 3. Replace detect_intent Ollama call
# ------------------------------------------------------------

old = '''        response = ollama.chat(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        raw_result = response["message"]["content"].strip()'''

new = '''        response = gemini_client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config={
                "temperature": 0.1,
                "max_output_tokens": 30
            }
        )

        raw_result = response.text.strip()'''

if old not in s:
    raise SystemExit("detect_intent Ollama block not found")

s = s.replace(old, new, 1)

# ------------------------------------------------------------
# 4. Replace NORMAL AI Ollama call
# ------------------------------------------------------------

old_start = '''                response = ollama.chat(
                        model=MODEL,
                        messages=[
                            {
                                "role": "system",
                                "content": (
                                    "You are SPIDEY. "
                                    + (
                                        "Be bold, blunt, sarcastic and confident. "
                                        "Lightly roast the user when appropriate. "
                                        "Stay useful and do not be genuinely hateful."
                                        if MOOD_MODE == "savage"
                                        else
                                        "Be playful, witty and teasing. "
                                        "Lightly roast the user when appropriate. "
                                        "Keep it fun and helpful."
                                        if MOOD_MODE == "roast"
                                        else
                                        "Be helpful, natural, confident and concise."
                                    )
                                )
                            }
                        ] + messages,
                        options={
                            "temperature": 0.3,
                            "num_predict": 140
                        }
                    )

                reply = response[
                        "message"
                    ][
                        "content"
                    ]'''

new_start = '''                if MOOD_MODE == "savage":
                    personality = (
                        "Be bold, blunt, sarcastic and confident. "
                        "Lightly roast the user when appropriate. "
                        "Stay useful and do not be genuinely hateful."
                    )
                elif MOOD_MODE == "roast":
                    personality = (
                        "Be playful, witty and teasing. "
                        "Lightly roast the user when appropriate. "
                        "Keep it fun and helpful."
                    )
                else:
                    personality = (
                        "Be helpful, natural, confident and concise."
                    )

                conversation = []

                for msg in messages:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")

                    if role == "system":
                        conversation.append(
                            "SYSTEM: " + content
                        )
                    elif role == "assistant":
                        conversation.append(
                            "SPIDEY: " + content
                        )
                    else:
                        conversation.append(
                            "USER: " + content
                        )

                gemini_prompt = (
                    "You are SPIDEY, a personal AI assistant.\\n"
                    + personality
                    + "\\n\\nConversation history:\\n"
                    + "\\n".join(conversation)
                    + "\\n\\nRespond naturally to the latest user message."
                )

                response = gemini_client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=gemini_prompt,
                    config={
                        "temperature": 0.3,
                        "max_output_tokens": 140
                    }
                )

                reply = response.text.strip()'''

if old_start not in s:
    raise SystemExit("NORMAL AI Ollama block not found")

s = s.replace(old_start, new_start, 1)

# ------------------------------------------------------------
# 5. Update the debug text
# ------------------------------------------------------------

s = s.replace(
    'DEBUG: SENDING COMMAND TO OLLAMA',
    'DEBUG: SENDING COMMAND TO GEMINI',
    1
)

p.write_text(s, encoding="utf-8")

print("======================================")
print("GEMINI BACKEND PATCH APPLIED")
print("======================================")
print("Backup: main_backup_before_gemini.py")
print("AI backend: Gemini")
print("Model:", "gemini-3.8-flash")
print("Ollama calls replaced: 2")
print("======================================")
