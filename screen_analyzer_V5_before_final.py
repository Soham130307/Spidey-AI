import re
import ollama
import screen_ocr
import screen_vision


# ============================================================
# SPIDEY SCREEN ANALYZER V5
# FAST + EVIDENCE FIRST
# ============================================================

REASONING_MODEL = "llama3.2:3b"


# ============================================================
# REAL ERROR PATTERNS
# ============================================================

ERROR_PATTERNS = [
    r"\bTraceback\b",
    r"\bSyntaxError\b",
    r"\bNameError\b",
    r"\bTypeError\b",
    r"\bModuleNotFoundError\b",
    r"\bImportError\b",
    r"\bIndentationError\b",
    r"\bAttributeError\b",
    r"\bKeyError\b",
    r"\bIndexError\b",
    r"\bValueError\b",
    r"\bRuntimeError\b",
    r"\bPermissionError\b",
    r"\bFileNotFoundError\b",
    r"\bConnectionError\b",
    r"\bException\b",
    r"\bFAILED\b",
    r"\bFAILURE\b",
]


# ============================================================
# CLEAN OCR
# ============================================================

def clean_ocr_text(text):
    if not text:
        return ""

    lines = []
    seen = set()

    for raw in text.splitlines():

        line = raw.strip()

        if not line:
            continue

        line = re.sub(r"\s+", " ", line)

        # Ignore obvious noise
        if line.startswith(("http://", "https://", "www.")):
            continue

        key = line.lower()

        if key in seen:
            continue

        seen.add(key)
        lines.append(line)

        if len(lines) >= 100:
            break

    return "\n".join(lines)


# ============================================================
# SIGNAL EXTRACTION
# ============================================================

def extract_signals(text):

    signals = {
        "files": [],
        "apps": [],
        "programming": [],
        "errors": [],
    }

    if not text:
        return signals

    lines = [x.strip() for x in text.splitlines() if x.strip()]

    file_pattern = re.compile(
        r"\b[\w.-]+\.(?:py|js|ts|tsx|jsx|html|css|json|md|txt|"
        r"ps1|bat|cpp|c|java|go|rs|yaml|yml|xml|sql)\b",
        re.IGNORECASE,
    )

    app_keywords = [
        "Visual Studio Code",
        "VS Code",
        "Chrome",
        "Microsoft Edge",
        "Firefox",
        "PowerShell",
        "Command Prompt",
        "Terminal",
        "Spotify",
        "ChatGPT",
        "Discord",
        "File Explorer",
    ]

    programming_keywords = [
        "def ",
        "class ",
        "import ",
        "from ",
        "return ",
        "async ",
        "await ",
        "function ",
        "const ",
        "let ",
        "var ",
        "npm ",
        "pip ",
        "python ",
        "pyautogui",
        "ollama",
        "pygame",
    ]

    for line in lines:

        # ---------------- FILES ----------------

        for match in file_pattern.findall(line):
            if match not in signals["files"]:
                signals["files"].append(match)

        # ---------------- APPS ----------------

        for app in app_keywords:
            if app.lower() in line.lower():
                if app not in signals["apps"]:
                    signals["apps"].append(app)

        # ---------------- PROGRAMMING ----------------

        for keyword in programming_keywords:
            if keyword.lower() in line.lower():
                if line not in signals["programming"]:
                    signals["programming"].append(line)
                break

        # ---------------- REAL ERRORS ----------------

        for pattern in ERROR_PATTERNS:

            if re.search(pattern, line, re.IGNORECASE):

                # Ignore obvious test headings
                if re.search(
                    r"---\s*(ERROR|ERROR TEST|ERROR ANALYSIS)\s*---",
                    line,
                    re.IGNORECASE,
                ):
                    continue

                if line not in signals["errors"]:
                    signals["errors"].append(line)

                break

    return signals


# ============================================================
# FAST ACTIVITY DETECTION
# ============================================================

def fast_activity(text, signals):

    files = signals["files"]
    apps = signals["apps"]
    programming = signals["programming"]

    # Strong programming evidence
    if files and programming:

        filename = files[0]

        if apps:
            return (
                f"You're working on {filename} in "
                f"{apps[0]}, editing code."
            )

        return (
            f"You're working on {filename} in a code editor, "
            f"editing code."
        )

    # App only
    if apps:
        return f"{apps[0]} appears to be the main application on your screen."

    return None


# ============================================================
# FAST ERROR DETECTION
# ============================================================

def fast_error(text, signals):

    errors = signals["errors"]

    if errors:

        # Return the actual evidence directly.
        # No vision hallucination needed.
        return (
            "I found a possible error in the visible text: "
            + errors[0]
        )

    return None


# ============================================================
# LLM REASONING
# ============================================================

def reason(question, text, vision="", signals=None):

    signals = signals or {}

    signal_text = ""

    if signals.get("files"):
        signal_text += (
            "Files: "
            + ", ".join(signals["files"])
            + "\n"
        )

    if signals.get("apps"):
        signal_text += (
            "Applications: "
            + ", ".join(signals["apps"])
            + "\n"
        )

    if signals.get("programming"):
        signal_text += (
            "Programming evidence:\n"
            + "\n".join(signals["programming"][:8])
            + "\n"
        )

    if signals.get("errors"):
        signal_text += (
            "REAL ERROR EVIDENCE:\n"
            + "\n".join(signals["errors"])
            + "\n"
        )

    prompt = f"""
You are SPIDEY's screen analysis engine.

Answer ONLY from the evidence provided.

Rules:
- Never invent information.
- Never claim an error without evidence.
- "ERROR" inside a test heading is NOT an error.
- "Problems" alone is NOT an error.
- "Ln", "Col", "Spaces", "UTF-8", "LF", "CRLF",
  "Python", "venv", and "GoLive" are NOT errors.
- Do not turn normal UI indicators into specific errors.
- If evidence is insufficient, say that clearly.
- Prefer OCR evidence over vague visual guesses.
- No roleplay.
- No Spider-Man jokes.
- Maximum 3 sentences.

QUESTION:
{question}

SIGNALS:
{signal_text}

OCR:
{text[:6000]}

VISION:
{vision[:2000]}
"""

    response = ollama.chat(
        model=REASONING_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        options={
            "temperature": 0
        },
        keep_alive="5m",
    )

    return response["message"]["content"].strip()


# ============================================================
# VISION FALLBACK
# ============================================================

def get_visual(prompt):

    try:
        return screen_vision.analyze_screen(prompt)

    except Exception as e:
        return f"Vision unavailable: {e}"


# ============================================================
# ACTIVITY
# ============================================================

def activity_analysis():

    print("[V5] Fast activity analysis...")

    text = clean_ocr_text(
        screen_ocr.read_screen()
    )

    signals = extract_signals(text)

    # FAST PATH
    result = fast_activity(text, signals)

    if result:
        print("[V5] Fast path used.")
        return result

    # FALLBACK ONLY
    print("[V5] Using vision fallback...")

    vision = get_visual(
        "Identify the main application and the user's "
        "current activity on this computer screen."
    )

    return reason(
        "What am I currently doing on my computer?",
        text,
        vision,
        signals
    )


# ============================================================
# ERROR
# ============================================================

def error_analysis():

    print("[V5] Error analysis...")

    text = clean_ocr_text(
        screen_ocr.read_screen()
    )

    signals = extract_signals(text)

    # FAST PATH
    result = fast_error(text, signals)

    if result:
        print("[V5] Confirmed error text found.")
        return result

    # IMPORTANT:
    # Do NOT let the test heading "--- ERROR ---"
    # become an error.
    #
    # We currently report no confirmed textual error
    # instead of hallucinating one.

    print("[V5] No confirmed error text found.")

    return (
        "I don't see a confirmed error in the visible text."
    )


# ============================================================
# TEXT
# ============================================================

def text_analysis():

    print("[V5] OCR text analysis...")

    text = clean_ocr_text(
        screen_ocr.read_screen()
    )

    if not text:
        return "I couldn't detect any readable text on the screen."

    signals = extract_signals(text)

    return reason(
        "What important readable text is visible on my screen?",
        text,
        "",
        signals
    )


# ============================================================
# GENERAL
# ============================================================

def general_analysis():

    print("[V5] General analysis...")

    text = clean_ocr_text(
        screen_ocr.read_screen()
    )

    signals = extract_signals(text)

    # Try fast activity understanding first
    activity = fast_activity(text, signals)

    if activity:
        return activity

    # Vision only when OCR isn't enough
    print("[V5] Using vision fallback...")

    vision = get_visual(
        "Identify the main application, important interface "
        "elements, and what the user appears to be doing."
    )

    return reason(
        "What is happening on my screen?",
        text,
        vision,
        signals
    )


# ============================================================
# VISUAL QUESTION
# ============================================================

def visual_question(question):

    print("[V5] Visual question...")

    text = clean_ocr_text(
        screen_ocr.read_screen()
    )

    signals = extract_signals(text)

    vision = get_visual(question)

    return reason(
        question,
        text,
        vision,
        signals
    )


# ============================================================
# ROUTER
# ============================================================

def analyze_screen(mode="general", question=None):

    mode = (mode or "general").lower().strip()

    if mode == "activity":
        return activity_analysis()

    if mode == "error":
        return error_analysis()

    if mode == "text":
        return text_analysis()

    if mode == "visual":
        return visual_question(
            question or "What do you see on my screen?"
        )

    return general_analysis()


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("==============================")
    print(" SPIDEY SCREEN ANALYZER V5")
    print("==============================")

    print()
    print("--- ACTIVITY ---")
    print(analyze_screen("activity"))

    print()
    print("--- ERROR ---")
    print(analyze_screen("error"))
