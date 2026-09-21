import re
import ollama
import screen_ocr
import screen_vision


# ============================================================
# SPIDEY SCREEN ANALYZER V5
# FINAL PRACTICAL VERSION
#
# Architecture:
# OCR -> deterministic fast path -> vision fallback -> reasoning
#
# Goal:
# Maximum useful screen understanding without unnecessarily
# running slow CPU vision models.
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
# APP PRIORITY
# ============================================================

APP_PRIORITY = [
    "Visual Studio Code",
    "VS Code",
    "Google Chrome",
    "Microsoft Edge",
    "Firefox",
    "Spotify",
    "Discord",
    "ChatGPT",
    "PowerShell",
    "Command Prompt",
    "Terminal",
    "File Explorer",
]


# ============================================================
# FILE TYPES
# ============================================================

FILE_PATTERN = re.compile(
    r"\b[\w.-]+\.(?:"
    r"py|js|ts|tsx|jsx|html|css|json|md|txt|"
    r"ps1|bat|cpp|c|h|java|go|rs|yaml|yml|xml|sql|"
    r"php|rb|swift|kt|dart"
    r")\b",
    re.IGNORECASE,
)


# ============================================================
# PROGRAMMING SIGNALS
# ============================================================

PROGRAMMING_KEYWORDS = [
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
    "if ",
    "else:",
    "elif ",
    "for ",
    "while ",
    "try:",
    "except ",
    "print(",
    "npm ",
    "pip ",
    "python ",
    "pyautogui",
    "ollama",
    "pygame",
]


# ============================================================
# OCR CLEANING
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

        # Remove URLs
        if line.startswith(
            ("http://", "https://", "www.")
        ):
            continue

        key = line.lower()

        if key in seen:
            continue

        seen.add(key)
        lines.append(line)

        if len(lines) >= 120:
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

    lines = [
        x.strip()
        for x in text.splitlines()
        if x.strip()
    ]

    for line in lines:

        # ----------------------------------------------------
        # FILES
        # ----------------------------------------------------

        for match in FILE_PATTERN.findall(line):

            if match not in signals["files"]:
                signals["files"].append(match)

        # ----------------------------------------------------
        # APPS
        # ----------------------------------------------------

        for app in APP_PRIORITY:

            if app.lower() in line.lower():

                if app not in signals["apps"]:
                    signals["apps"].append(app)

        # ----------------------------------------------------
        # PROGRAMMING
        # ----------------------------------------------------

        lower_line = line.lower()

        for keyword in PROGRAMMING_KEYWORDS:

            if keyword.lower() in lower_line:

                if line not in signals["programming"]:
                    signals["programming"].append(line)

                break

        # ----------------------------------------------------
        # ERRORS
        # ----------------------------------------------------

        for pattern in ERROR_PATTERNS:

            if not re.search(
                pattern,
                line,
                re.IGNORECASE
            ):
                continue

            # Ignore our own test headings.
            if re.fullmatch(
                r"[-=\s]*(error|error test|error analysis)[-=\s]*",
                line,
                re.IGNORECASE,
            ):
                continue

            # Ignore status-bar metadata.
            if re.search(
                r"^\s*(Ln|Col|Spaces|Tab Size|UTF-?8|"
                r"LF|CRLF|Python|venv|GoLive)\b",
                line,
                re.IGNORECASE,
            ):
                continue

            if line not in signals["errors"]:
                signals["errors"].append(line)

            break

    return signals


# ============================================================
# APP DETECTION
# ============================================================

def best_app(signals):

    apps = signals.get("apps", [])

    if not apps:
        return None

    # VS Code always wins over Terminal when both are visible.
    priority = {
        "Visual Studio Code": 1,
        "VS Code": 2,
        "Google Chrome": 3,
        "Microsoft Edge": 4,
        "Firefox": 5,
        "Spotify": 6,
        "Discord": 7,
        "ChatGPT": 8,
        "PowerShell": 9,
        "Command Prompt": 10,
        "Terminal": 11,
        "File Explorer": 12,
    }

    return sorted(
        apps,
        key=lambda x: priority.get(x, 99)
    )[0]


# ============================================================
# FAST ACTIVITY
# ============================================================

def fast_activity(signals):

    files = signals["files"]
    programming = signals["programming"]
    app = best_app(signals)

    if files and programming:

        filename = files[0]

        if app in [
            "Visual Studio Code",
            "VS Code"
        ]:
            return (
                f"You're working on {filename} in VS Code, "
                f"editing code."
            )

        if app:
            return (
                f"You're working on {filename} in {app}, "
                f"editing code."
            )

        return (
            f"You're working on {filename} in a code editor, "
            f"editing code."
        )

    if files:

        if app:
            return (
                f"{files[0]} is visible in {app}."
            )

        return (
            f"{files[0]} is visible on the screen."
        )

    if app:

        return (
            f"{app} appears to be the main application "
            f"on your screen."
        )

    return None


# ============================================================
# FAST ERROR
# ============================================================

def fast_error(signals):

    errors = signals["errors"]

    if not errors:
        return None

    return (
        "I found visible error text: "
        + errors[0]
    )


# ============================================================
# FAST TEXT
# ============================================================

def fast_text(text, signals):

    if not text:
        return (
            "I couldn't detect any readable text "
            "on the screen."
        )

    important = []

    for filename in signals["files"]:
        if filename not in important:
            important.append(filename)

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        # Skip obvious status bar noise.
        if re.match(
            r"^(Ln|Col|Spaces|Tab Size|UTF-?8|LF|CRLF)\b",
            line,
            re.IGNORECASE
        ):
            continue

        if line not in important:
            important.append(line)

        if len(important) >= 8:
            break

    if not important:
        return "I can see text, but nothing clearly useful to report."

    return "Visible text includes: " + "; ".join(important)


# ============================================================
# LLM REASONING
# ============================================================

def reason(
    question,
    text,
    vision="",
    signals=None
):

    signals = signals or {}

    evidence = []

    if signals.get("apps"):
        evidence.append(
            "Applications: "
            + ", ".join(signals["apps"])
        )

    if signals.get("files"):
        evidence.append(
            "Files: "
            + ", ".join(signals["files"])
        )

    if signals.get("programming"):
        evidence.append(
            "Programming evidence:\n"
            + "\n".join(
                signals["programming"][:8]
            )
        )

    if signals.get("errors"):
        evidence.append(
            "Confirmed error evidence:\n"
            + "\n".join(
                signals["errors"][:8]
            )
        )

    signal_text = "\n\n".join(evidence)

    prompt = f"""
You are SPIDEY's screen analysis engine.

Answer the user's question using ONLY the evidence.

STRICT RULES:
- Never invent details.
- Never claim something is visible unless evidence supports it.
- Never invent an error.
- "--- ERROR ---" or similar headings are not errors.
- "Problems" alone is not an error.
- Ln, Col, Spaces, UTF-8, LF, CRLF, Python,
  venv and GoLive are not errors.
- If an exact error is visible, quote its name accurately.
- If evidence is insufficient, say so.
- Prefer specific OCR evidence over vague visual guesses.
- No roleplay.
- No Spider-Man jokes.
- Maximum 3 sentences.

USER QUESTION:
{question}

EXTRACTED SIGNALS:
{signal_text}

OCR:
{text[:7000]}

VISION:
{vision[:2500]}
"""

    try:

        response = ollama.chat(
            model=REASONING_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            options={
                "temperature": 0,
                "num_predict": 120,
            },
            keep_alive="5m",
        )

        result = (
            response["message"]["content"]
            .strip()
        )

        if (
            len(result) >= 2
            and result[0] == '"'
            and result[-1] == '"'
        ):
            result = result[1:-1]

        return result

    except Exception as e:

        print("[V5] Reasoning error:", e)

        return (
            "I couldn't complete the screen reasoning."
        )


# ============================================================
# VISION FALLBACK
# ============================================================

def get_visual(prompt):

    try:

        return screen_vision.analyze_screen(
            prompt
        )

    except Exception as e:

        print("[V5] Vision error:", e)

        return ""


# ============================================================
# CAPTURE OCR
# ============================================================

def capture_screen():

    print("[V5] OCR scan...")

    text = clean_ocr_text(
        screen_ocr.read_screen()
    )

    signals = extract_signals(text)

    return text, signals


# ============================================================
# ACTIVITY
# ============================================================

def activity_analysis():

    text, signals = capture_screen()

    result = fast_activity(signals)

    if result:

        print("[V5] Activity FAST PATH.")

        return result

    print("[V5] Activity -> vision fallback.")

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

    text, signals = capture_screen()

    result = fast_error(signals)

    if result:

        print("[V5] Confirmed error text.")

        return result

    # Deliberately do NOT call vision here.
    #
    # On a CPU-only machine this is much faster and avoids
    # false positives from vague visual indicators.

    print("[V5] No confirmed textual error.")

    return (
        "I don't see a confirmed error in the visible text."
    )


# ============================================================
# TEXT
# ============================================================

def text_analysis():

    text, signals = capture_screen()

    return fast_text(
        text,
        signals
    )


# ============================================================
# GENERAL
# ============================================================

def general_analysis():

    text, signals = capture_screen()

    result = fast_activity(signals)

    if result:

        print("[V5] General FAST PATH.")

        return result

    print("[V5] General -> vision fallback.")

    vision = get_visual(
        "Look at this computer screen. Identify the "
        "main application, important interface elements, "
        "and what the user appears to be doing."
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

    text, signals = capture_screen()

    print("[V5] Visual question -> vision.")

    vision = get_visual(
        question
    )

    return reason(
        question,
        text,
        vision,
        signals
    )


# ============================================================
# ROUTER
# ============================================================

def analyze_screen(
    mode="general",
    question=None
):

    mode = (
        mode
        or "general"
    ).lower().strip()

    if mode == "activity":
        return activity_analysis()

    if mode == "error":
        return error_analysis()

    if mode == "text":
        return text_analysis()

    if mode == "visual":

        return visual_question(
            question
            or "What do you see on my screen?"
        )

    return general_analysis()


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("==============================")
    print(" SPIDEY SCREEN ANALYZER V5")
    print(" FINAL OPTIMIZED BUILD")
    print("==============================")

    print()
    print("--- ACTIVITY ---")
    print(
        analyze_screen("activity")
    )

    print()
    print("--- ERROR ---")
    print(
        analyze_screen("error")
    )
