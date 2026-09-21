import screen_ocr
import screen_vision


# ============================================================
# SPIDEY SCREEN VISION ENGINE
# ============================================================

def clean_ocr_text(text):
    if not text:
        return ""

    lines = []

    for line in text.splitlines():
        line = line.strip()

        if not line:
            continue

        # Remove browser URLs
        if line.startswith(("http://", "https://", "www.")):
            continue

        if len(line) < 2:
            continue

        lines.append(line)

    if len(lines) > 30:
        lines = lines[:30]

    return "\n".join(lines)


# ============================================================
# OCR
# ============================================================

def get_screen_text():
    print("[ANALYZER] Capturing screen text...")

    raw_text = screen_ocr.read_screen()

    return clean_ocr_text(raw_text)


# ============================================================
# GENERAL VISION
# ============================================================

def general_vision():
    print("[ANALYZER] General visual analysis...")

    return screen_vision.analyze_screen(
        """
Look carefully at the entire computer screen.

Describe the important things that are actually visible.

Focus on:
- the main content
- important images or objects
- visible applications or websites
- important messages
- what appears to be happening

Do not guess.
Do not invent details.

Give a concise answer in 1-3 sentences.
"""
    )


# ============================================================
# ACTIVITY ANALYSIS
# ============================================================

def activity_analysis():
    print("[ANALYZER] Analyzing user activity...")

    text = get_screen_text()

    vision = screen_vision.analyze_screen(
        """
Look carefully at this computer screen.

Determine what the user appears to be doing RIGHT NOW.

Use visible evidence from:
- the application or website
- visible text
- buttons and controls
- images
- documents
- conversations
- code
- videos
- other visible content

Do not guess.

If the exact activity cannot be determined,
describe the visible activity instead.

Answer in 1-2 clear sentences.
"""
    )

    if text:
        return (
            "VISIBLE TEXT:\n"
            + text[:2500]
            + "\n\nVISUAL CONTEXT:\n"
            + (vision or "")
        )

    return vision or ""


# ============================================================
# ERROR ANALYSIS
# ============================================================

def error_analysis():
    print("[ANALYZER] Searching for errors...")

    text = get_screen_text()

    vision = screen_vision.analyze_screen(
        """
Inspect this computer screen carefully.

Look specifically for:
- error messages
- warnings
- failed operations
- red error indicators
- dialogs reporting problems
- broken or unexpected UI states

Use only visible evidence.

If you see an error:
briefly identify what it says and where it appears.

If you do not see an obvious error:
say exactly that.

Do not guess.
"""
    )

    return (
        "VISIBLE TEXT:\n"
        + (text[:2500] if text else "No readable text found.")
        + "\n\nVISUAL CHECK:\n"
        + (vision or "No visual result.")
    )


# ============================================================
# TEXT ANALYSIS
# ============================================================

def text_analysis():
    print("[ANALYZER] Reading screen with OCR...")

    text = get_screen_text()

    if not text:
        return "I couldn't find any readable text on the screen."

    return text


# ============================================================
# VISUAL QUESTION
# ============================================================

def visual_question(question):
    print("[ANALYZER] Answering visual question...")

    return screen_vision.analyze_screen(
        f"""
Look carefully at this computer screen.

The user asks:

"{question}"

Answer the question using ONLY what is visibly present
on the screen.

Do not guess.
If the answer cannot be determined from the screen,
say that clearly.

Keep the answer concise.
"""
    )


# ============================================================
# MAIN ANALYZER
# ============================================================

def analyze_screen(mode="general", question=None):

    mode = mode.lower().strip()

    if mode == "text":
        return text_analysis()

    if mode == "activity":
        return activity_analysis()

    if mode == "error":
        return error_analysis()

    if mode == "question":
        if question:
            return visual_question(question)

        return general_vision()

    return general_vision()


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n================================")
    print(" SPIDEY SCREEN VISION TEST")
    print("================================")

    print("\n--- GENERAL ---")
    print(analyze_screen("general"))

    print("\n--- TEXT ---")
    print(analyze_screen("text"))

    print("\n--- ACTIVITY ---")
    print(analyze_screen("activity"))

    print("\n--- ERROR ---")
    print(analyze_screen("error"))
