from pathlib import Path
import re

p = Path("main.py")
s = p.read_text(encoding="utf-8")

# ============================================================
# 1. IMPORT GEMINI
# ============================================================

if "import ollama" not in s:
    raise SystemExit("ERROR: import ollama not found")

s = s.replace(
    "import ollama",
    "from google import genai",
    1
)

# ============================================================
# 2. REPLACE MODEL SETTING + CREATE GEMINI CLIENT
# ============================================================

old = 'MODEL = "llama3.2:3b"'

new = '''GEMINI_MODEL = "gemini-3.8-flash"

gemini_client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)'''

if old not in s:
    raise SystemExit("ERROR: MODEL line not found")

s = s.replace(old, new, 1)

# ============================================================
# 3. REPLACE ENTIRE detect_intent() FUNCTION
# ============================================================

start = s.find("def detect_intent(command):")
end = s.find("\n\n# ============================================================\n# VOICE OUTPUT", start)

if start == -1 or end == -1:
    raise SystemExit("ERROR: detect_intent boundaries not found")

new_detect_intent = '''def detect_intent(command):

    prompt = f"""
You are SPIDEY's command classifier.

Classify the user's command.

Return ONLY one line in exactly this format:

OPEN_WEBSITE|name
OPEN_APP|name
OPEN_FOLDER|name
NORMAL_CHAT|none

Examples:

open Instagram
OPEN_WEBSITE|instagram

can you open Instagram for me
OPEN_WEBSITE|instagram

take me to GitHub
OPEN_WEBSITE|github

launch Reddit
OPEN_WEBSITE|reddit

open Discord
OPEN_APP|discord

can you launch Discord for me
OPEN_APP|discord

start Discord
OPEN_APP|discord

open calculator
OPEN_APP|calculator

open notepad
OPEN_APP|notepad

start VS Code
OPEN_APP|vscode

open my downloads
OPEN_FOLDER|downloads

what is the capital of India
NORMAL_CHAT|none

tell me a joke
NORMAL_CHAT|none

IMPORTANT:

Discord, Calculator, Notepad and VS Code are applications.

Instagram, YouTube, GitHub, Reddit, Netflix,
Google and Facebook are websites. Spotify is an application.

Return ONLY the classification.
Do not explain.

User command:
{command}
"""

    try:

        print("GEMINI INTENT: CALLING")

        response = gemini_client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config={
                "temperature": 0.1,
                "max_output_tokens": 30
            }
        )

        raw_result = response.text.strip()

        result = next(
            (
                line.strip()
                for line in raw_result.splitlines()
                if line.strip()
            ),
            "NORMAL_CHAT|none"
        )

        result = result.replace("`", "").strip()

        match = re.match(
            r"^(OPEN_WEBSITE|OPEN_APP|OPEN_FOLDER|NORMAL_CHAT)\\|(.+)$",
            result,
            re.IGNORECASE
        )

        if match:

            intent_type = match.group(1).upper()
            name = match.group(2).strip().lower()

            result = f"{intent_type}|{name}"

        else:

            result = "NORMAL_CHAT|none"

        print("INTENT:", result)

        return result

    except Exception as e:

        print("Gemini intent error:", e)

        return "NORMAL_CHAT|none"
'''

s = s[:start] + new_detect_intent + s[end:]

# ============================================================
# 4. REPLACE NORMAL AI SECTION
# ============================================================

normal_start = s.find(
    '            # NORMAL AI'
)

if normal_start == -1:
    raise SystemExit("ERROR: NORMAL AI section not found")

try_start = s.find(
    "            try:",
    normal_start
)

except_start = s.find(
    "            except Exception as e:",
    try_start
)

if try_start == -1 or except_start == -1:
    raise SystemExit("ERROR: NORMAL AI try/except not found")

# Find end of except block before the next major section.
next_section = s.find(
    "\n\n# ============================================================\n# START SPIDEY + HUD",
    except_start
)

if next_section == -1:
    raise SystemExit("ERROR: NORMAL AI ending not found")

new_normal_ai = '''            # NORMAL AI

            print(
                "DEBUG: SENDING COMMAND TO GEMINI"
            )

            update_hud(
                "THINKING",
                "Thinking about your question..."
            )

            speak("I'm thinking...")

            messages.append(
                {
                    "role": "user",
                    "content": user_input
                }
            )

            try:

                if MOOD_MODE == "savage":

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

                    role = msg.get(
                        "role",
                        "user"
                    )

                    content = msg.get(
                        "content",
                        ""
                    )

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
                    + "\\n\\nAnswer the latest user message naturally."
                )

                print(
                    "GEMINI: CALLING NORMAL AI"
                )

                response = gemini_client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=gemini_prompt,
                    config={
                        "temperature": 0.3,
                        "max_output_tokens": 140
                    }
                )

                print(
                    "GEMINI: RESPONSE RECEIVED"
                )

                reply = response.text.strip()

                print(
                    "GEMINI REPLY:",
                    repr(reply)
                )

                messages.append(
                    {
                        "role": "assistant",
                        "content": reply
                    }
                )

                update_hud(
                    "SPEAKING",
                    f"Spidey: {reply}"
                )

                speak(
                    reply
                )

                update_hud(
                    "LISTENING",
                    "Listening for your command..."
                )

            except Exception as e:

                import traceback

                print()
                print("======================================")
                print("SPIDEY GEMINI ERROR")
                print("======================================")
                print(
                    "ERROR TYPE:",
                    type(e).__name__
                )
                print(
                    "ERROR:",
                    repr(e)
                )
                print("--------------------------------------")

                traceback.print_exc()

                print("======================================")
                print()

                speak(
                    "Sorry, I encountered an error while processing your request."
                )

                update_hud(
                    "LISTENING",
                    "Listening for your command..."
                )
'''

s = s[:normal_start] + new_normal_ai + s[next_section:]

# ============================================================
# 5. REMOVE OLD OLLAMA REFERENCES
# ============================================================

if "ollama." in s:
    raise SystemExit(
        "ERROR: Ollama reference still exists after patch"
    )

p.write_text(s, encoding="utf-8")

print()
print("======================================")
print("GEMINI BACKEND PATCHED SUCCESSFULLY")
print("======================================")
print("Backup: main_backup_before_gemini_final.py")
print("Backend: Google Gemini")
print("Model: gemini-3.8-flash")
print("Ollama calls: REMOVED")
print("Intent classifier: GEMINI")
print("Normal AI: GEMINI")
print("======================================")
