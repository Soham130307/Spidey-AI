import screen_ocr
import screen_vision
import ollama


# ============================================================
# SPIDEY SCREEN VISION V2
# OCR + VISION + LLM REASONING
# ============================================================

REASONING_MODEL = "llama3.2:3b"


# ============================================================
# CLEAN OCR
# ============================================================

def clean_ocr_text(text):

    if not text:
        return ""

    lines = []

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        # Remove URLs
        if line.startswith(("http://", "https://", "www.")):
            continue

        # Remove very short OCR fragments
        if len(line) < 2:
            continue

        lines.append(line)

    # Remove consecutive duplicates
    cleaned = []

    for line in lines:

        if not cleaned or line != cleaned[-1]:
            cleaned.append(line)

    # Keep context manageable
    return "\n".join(cleaned[:80])


# ============================================================
# CAPTURE TEXT
# ============================================================

def get_screen_text():

    print("[ANALYZER] Capturing screen text...")

    raw = screen_ocr.read_screen()

    return clean_ocr_text(raw)


# ============================================================
# CAPTURE VISUAL CONTEXT
# ============================================================

def get_visual_context(prompt):

    print("[ANALYZER] Capturing visual context...")

    result = screen_vision.analyze_screen(prompt)

    if not result:
        return "No visual information was returned."

    return result.strip()


# ============================================================
# LLM REASONING
# ============================================================

def reason_about_screen(question, text, vision):

    print("[ANALYZER] Reasoning about screen...")

    context = f"""
SCREEN TEXT:

{text[:5000] if text else "No readable text found."}


VISUAL INFORMATION:

{vision[:2000] if vision else "No visual information available."}
"""

    prompt = f"""
You are SPIDEY's screen-understanding system.

The user asks:

"{question}"

Use the screen evidence below to answer.

{context}

IMPORTANT RULES:

- Use the visible evidence.
- Combine the OCR and visual information.
- Do not blindly repeat the OCR.
- Do not invent things that are not supported.
- Do not say "maybe" unless uncertainty is genuinely unavoidable.
- If the exact answer cannot be determined, clearly say what IS visible.
- Prefer specific useful information over generic descriptions.
- Keep the answer short and natural.
- Answer as SPIDEY speaking to the user.
"""

    response = ollama.chat(
        model=REASONING_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"].strip()


# ============================================================
# GENERAL SCREEN UNDERSTANDING
# ============================================================

def general_analysis(question="What is on my screen?"):

    text = get_screen_text()

    vision = get_visual_context(
        """
Look at the entire computer screen.

Identify the important visible content, layout,
applications, documents, images, messages, and UI.

Do not guess.

Give useful visual information that can be combined
with OCR by another reasoning model.
"""
    )

    return reason_about_screen(question, text, vision)


# ============================================================
# ACTIVITY UNDERSTANDING
# ============================================================

def activity_analysis():

    return general_analysis(
        "What am I currently doing on my computer?"
    )


# ============================================================
# ERROR UNDERSTANDING
# ============================================================

def error_analysis():

    text = get_screen_text()

    vision = get_visual_context(
        """
Inspect the computer screen specifically for problems.

Look for:
- errors
- warnings
- failed operations
- red error indicators
- yellow warning indicators
- error dialogs
- terminal errors
- code problems
- unusual or broken UI states

Describe only visible evidence.
"""
    )

    return reason_about_screen(
        "Is there an error or problem on my screen? If so, explain the important one.",
        text,
        vision
    )


# ============================================================
# TEXT UNDERSTANDING
# ============================================================

def text_analysis():

    text = get_screen_text()

    if not text:
        return "I couldn't find readable text on the screen."

    return reason_about_screen(
        "What important text is visible on my screen?",
        text,
        "OCR detected the text directly from the screen."
    )


# ============================================================
# VISUAL QUESTION
# ============================================================

def visual_question(question):

    text = get_screen_text()

    vision = get_visual_context(
        f"""
Look carefully at this computer screen.

The user wants to know:

"{question}"

Identify visual evidence relevant to answering the question.

Do not guess.
"""
    )

    return reason_about_screen(question, text, vision)


# ============================================================
# MAIN ENTRY
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
        return visual_question(
            question if question else "What do you see on my screen?"
        )

    return general_analysis(
        question if question else "What is important on my screen?"
    )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n================================")
    print(" SPIDEY SCREEN VISION V2 TEST")
    print("================================")

    print("\n--- ACTIVITY ---")
    print(analyze_screen("activity"))

    print("\n--- ERROR ---")
    print(analyze_screen("error"))
