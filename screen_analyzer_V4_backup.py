import re
import ollama
import screen_ocr
import screen_vision


# ============================================================
# SPIDEY SCREEN ANALYZER V4
# Evidence-first + speed optimized
# ============================================================

REASONING_MODEL = "llama3.2:3b"


# ------------------------------------------------------------
# Error patterns
# ------------------------------------------------------------

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
    r"\bException\b",
    r"\bFAILED\b",
    r"\bFAILURE\b",
    r"\bERROR\b",
]

WARNING_PATTERNS = [
    r"\bWARNING\b",
    r"\bWARN\b",
]


# ------------------------------------------------------------
# OCR cleanup
# ------------------------------------------------------------

def clean_ocr_text(text):
    if not text:
        return ""

    lines = []
    seen = set()

    for raw in text.splitlines():
        line = raw.strip()

        if not line:
            continue

        # Remove obvious URL noise
        if line.startswith(("http://", "https://", "www.")):
            continue

        # Remove repeated spaces
        line = re.sub(r"\s+", " ", line)

        # Ignore common VS Code status-bar metadata
        if re.fullmatch(
            r"(Ln\s+\d+,\s*Col\s+\d+|Spaces:\s*\d+|"
            r"Tab Size:\s*\d+|UTF-?8|LF|CRLF|"
            r"Python|venv|GoLive)",
            line,
            re.IGNORECASE,
        ):
            continue

        key = line.lower()

        if key in seen:
            continue

        seen.add(key)
        lines.append(line)

        if len(lines) >= 100:
            break

    return "\n".join(lines)


# ------------------------------------------------------------
# Screen signals
# ------------------------------------------------------------

def extract_screen_signals(text):
    """
    Extract useful evidence before sending anything
    to the reasoning model.
    """

    if not text:
        return {
            "files": [],
            "apps": [],
            "programming": [],
            "errors": [],
            "warnings": [],
        }

    lines = [x.strip() for x in text.splitlines() if x.strip()]

    files = []
    apps = []
    programming = []
    errors = []
    warnings = []

    # File names
    file_pattern = re.compile(
        r"\b[\w.-]+\.(?:py|js|ts|tsx|jsx|html|css|json|md|txt|ps1|bat|"
        r"cpp|c|java|go|rs|yaml|yml|xml)\b",
        re.IGNORECASE,
    )

    # Applications
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

    # Programming evidence
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
        "pygame",
        "ollama",
        "pyautogui",
    ]

    for line in lines:

        # Files
        for match in file_pattern.findall(line):
            if match not in files:
                files.append(match)

        # Apps
        for app in app_keywords:
            if app.lower() in line.lower() and app not in apps:
                apps.append(app)

        # Programming
        for keyword in programming_keywords:
            if keyword.lower() in line.lower():
                if line not in programming:
                    programming.append(line)
                break

        # Actual errors
        has_error = any(
            re.search(pattern, line, re.IGNORECASE)
            for pattern in ERROR_PATTERNS
        )

        # Don't mistake status bar information for errors
        status_only = re.search(
            r"\b(Ln|Col|Spaces|UTF-?8|LF|CRLF|venv|Python)\b",
            line,
            re.IGNORECASE,
        )

        if has_error and not (
            status_only
            and not re.search(
                r"\b(Traceback|SyntaxError|NameError|TypeError|"
                r"ModuleNotFoundError|ImportError|IndentationError|"
                r"AttributeError|KeyError|IndexError|ValueError|"
                r"RuntimeError|Exception|FAILED|FAILURE|ERROR)\b",
                line,
                re.IGNORECASE,
            )
        ):
            if line not in errors:
                errors.append(line)

        # Warnings
        if any(
            re.search(pattern, line, re.IGNORECASE)
            for pattern in WARNING_PATTERNS
        ):
            if line not in warnings:
                warnings.append(line)

    return {
        "files": files[:10],
        "apps": apps[:10],
        "programming": programming[:12],
        "errors": errors[:12],
        "warnings": warnings[:12],
    }


# ------------------------------------------------------------
# Build compact evidence
# ------------------------------------------------------------

def build_signal_text(signals):
    parts = []

    if signals["apps"]:
        parts.append("Applications: " + ", ".join(signals["apps"]))

    if signals["files"]:
        parts.append("Files: " + ", ".join(signals["files"]))

    if signals["programming"]:
        parts.append(
            "Programming evidence:\n"
            + "\n".join(signals["programming"][:8])
        )

    if signals["errors"]:
        parts.append(
            "CONFIRMED ERROR TEXT:\n"
            + "\n".join(signals["errors"])
        )

    if signals["warnings"]:
        parts.append(
            "WARNING TEXT:\n"
            + "\n".join(signals["warnings"])
        )

    if not parts:
        return "No strong textual signals detected."

    return "\n\n".join(parts)


# ------------------------------------------------------------
# Reasoning
# ------------------------------------------------------------

def reason_about_screen(question, text, vision, signals):
    evidence = build_signal_text(signals)

    prompt = f"""
You are SPIDEY's screen reasoning engine.

Answer the user's question using ONLY evidence from:
1. extracted screen signals
2. OCR text
3. visual analysis

IMPORTANT RULES:
- Do NOT invent details.
- Do NOT assume something is an error without evidence.
- VS Code status-bar information such as "Ln", "Col", "Spaces",
  "UTF-8", "LF", "Python", or "venv" is NOT an error.
- The word "Problems" alone does NOT prove an error.
- A red/yellow UI indicator may indicate a possible issue,
  but do not invent the error type.
- If exact error text is visible, use it.
- If a filename is visible, mention it when useful.
- Prefer specific OCR evidence over vague visual guesses.
- Be concise.
- No roleplay.
- No Spider-Man jokes.
- Answer naturally in 1-3 sentences.

USER QUESTION:
{question}

EXTRACTED SIGNALS:
{evidence}

OCR TEXT:
{text[:7000]}

VISUAL ANALYSIS:
{vision[:2500]}
"""

    response = ollama.chat(
        model=REASONING_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    result = response["message"]["content"].strip()

    # Remove accidental quote wrapping
    if len(result) >= 2 and result[0] == '"' and result[-1] == '"':
        result = result[1:-1]

    return result


# ------------------------------------------------------------
# Visual context
# ------------------------------------------------------------

def get_visual_context(prompt):
    try:
        return screen_vision.analyze_screen(prompt)
    except Exception as e:
        return f"Visual analysis unavailable: {e}"


# ------------------------------------------------------------
# GENERAL
# ------------------------------------------------------------

def general_analysis():
    text = clean_ocr_text(screen_ocr.read_screen())
    signals = extract_screen_signals(text)

    vision = get_visual_context(
        "Look at this computer screen. Identify the main application, "
        "important visible interface elements, and what the user appears "
        "to be doing. Do not guess text."
    )

    return reason_about_screen(
        "What is happening on my screen?",
        text,
        vision,
        signals,
    )


# ------------------------------------------------------------
# ACTIVITY
# ------------------------------------------------------------

def activity_analysis():
    text = clean_ocr_text(screen_ocr.read_screen())
    signals = extract_screen_signals(text)

    vision = get_visual_context(
        "Look at this computer screen and determine the user's "
        "current activity. Focus on the main application and task."
    )

    return reason_about_screen(
        "What am I currently doing on my computer?",
        text,
        vision,
        signals,
    )


# ------------------------------------------------------------
# ERROR
# ------------------------------------------------------------

def error_analysis():
    text = clean_ocr_text(screen_ocr.read_screen())
    signals = extract_screen_signals(text)

    # If OCR found no actual error text, we still inspect visually,
    # but explicitly prevent hallucinated error claims.
    vision = get_visual_context(
        "Inspect this computer screen specifically for visible "
        "error messages, warnings, failed operations, or problem "
        "indicators. Do not treat normal status-bar information "
        "as an error. If no clear problem is visible, say so."
    )

    return reason_about_screen(
        "Are there any errors or problems on my screen? "
        "If yes, explain only what is actually supported by the evidence.",
        text,
        vision,
        signals,
    )


# ------------------------------------------------------------
# TEXT
# ------------------------------------------------------------

def text_analysis():
    text = clean_ocr_text(screen_ocr.read_screen())

    if not text:
        return "I couldn't detect any readable text on the screen."

    signals = extract_screen_signals(text)

    vision = "OCR is the primary evidence for this request."

    return reason_about_screen(
        "What important readable text is visible on my screen? "
        "Mention useful text such as filenames, headings, commands, "
        "messages, or code-related information. Ignore URLs and UI noise.",
        text,
        vision,
        signals,
    )


# ------------------------------------------------------------
# VISUAL QUESTION
# ------------------------------------------------------------

def visual_question(question):
    text = clean_ocr_text(screen_ocr.read_screen())
    signals = extract_screen_signals(text)

    vision = get_visual_context(question)

    return reason_about_screen(
        question,
        text,
        vision,
        signals,
    )


# ------------------------------------------------------------
# ROUTER
# ------------------------------------------------------------

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


# ------------------------------------------------------------
# TEST
# ------------------------------------------------------------

if __name__ == "__main__":

    print("\n==============================")
    print(" SPIDEY SCREEN ANALYZER V4")
    print("==============================")

    print("\n--- ACTIVITY ---")
    print(analyze_screen("activity"))

    print("\n--- ERROR ---")
    print(analyze_screen("error"))
