import screen_ocr
import screen_vision
import ollama
import re


# ============================================================
# SPIDEY SCREEN VISION V3
# Evidence-first screen understanding
# ============================================================

REASONING_MODEL = "llama3.2:3b"


# ============================================================
# OCR CLEANING
# ============================================================

def clean_ocr_text(text):

    if not text:
        return ""

    lines = []

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        # Ignore URLs
        if re.match(r"^(https?://|www\.)", line, re.IGNORECASE):
            continue

        # Ignore obvious OCR garbage
        if len(line) < 2:
            continue

        # Remove repeated spaces
        line = re.sub(r"\s+", " ", line)

        lines.append(line)

    # Remove duplicate lines while preserving order
    result = []

    for line in lines:

        if line not in result:
            result.append(line)

    return "\n".join(result[:80])


# ============================================================
# OCR
# ============================================================

def get_screen_text():

    print("[ANALYZER] Capturing screen text...")

    raw_text = screen_ocr.read_screen()

    return clean_ocr_text(raw_text)


# ============================================================
# VISION
# ============================================================

def get_visual_context(prompt):

    print("[ANALYZER] Capturing visual context...")

    result = screen_vision.analyze_screen(prompt)

    if not result:
        return "No visual information available."

    return result.strip()


# ============================================================
# REASONING
# ============================================================

def reason_about_screen(question, text, vision):

    print("[ANALYZER] Reasoning from screen evidence...")

    prompt = f"""
You are SPIDEY's screen analysis system.

USER QUESTION:
{question}

SCREEN EVIDENCE:

[OCR TEXT]
{text if text else "No readable text was detected."}

[VISUAL ANALYSIS]
{vision if vision else "No visual analysis was available."}


YOUR JOB:

Answer the user's question using the evidence above.

STRICT RULES:

1. Treat OCR and visual analysis as evidence, not guesses.
2. Do not invent information.
3. Do not claim something is visible unless the evidence supports it.
4. If OCR gives specific text, use that information when relevant.
5. If OCR and vision disagree, prefer the specific readable OCR evidence.
6. Do not assume an error is a syntax error unless the evidence actually says so.
7. If something cannot be determined, say so clearly.
8. Never use phrases like "Hey there", "citizen", "web-slinger", or other roleplay.
9. Do not give generic descriptions when specific evidence is available.
10. Answer directly and naturally.
11. Keep the answer to 1-3 sentences unless the user asks for details.

Return ONLY the answer to the user.
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

    answer = response["message"]["content"].strip()

    # Remove accidental quotation wrapping
    if len(answer) >= 2:
        if answer.startswith('"') and answer.endswith('"'):
            answer = answer[1:-1].strip()

    return answer


# ============================================================
# GENERAL
# ============================================================

def general_analysis(question="What is on my screen?"):

    text = get_screen_text()

    vision = get_visual_context(
        """
Analyze the entire computer screen.

Report useful visual facts:
- main application
- important content
- visible documents
- images
- dialogs
- buttons
- warnings
- other important UI

Do not guess.
Do not give a generic description if something specific
can be identified.
Return concise factual observations.
"""
    )

    return reason_about_screen(question, text, vision)


# ============================================================
# ACTIVITY
# ============================================================

def activity_analysis():

    text = get_screen_text()

    vision = get_visual_context(
        """
Analyze this computer screen to determine the user's
current activity.

Look for evidence such as:
- application or website
- document or code being edited
- conversation
- video
- search
- terminal
- settings
- programming
- browsing
- other visible tasks

Do not guess.
If the exact activity is unclear, state only what is
supported by the visible evidence.
"""
    )

    return reason_about_screen(
        "What am I currently doing on my computer?",
        text,
        vision
    )


# ============================================================
# ERROR ANALYSIS
# ============================================================

def error_analysis():

    text = get_screen_text()

    vision = get_visual_context(
        """
Inspect this screen for visible problems.

Look for:
- error messages
- warnings
- failed operations
- exceptions
- red error indicators
- yellow warning indicators
- dialogs reporting failures
- terminal errors
- code errors

Report only clearly visible evidence.

Do not assume the type of error if it cannot be determined.
"""
    )

    return reason_about_screen(
        "Is there a visible error or problem on my screen? If yes, what does the evidence show?",
        text,
        vision
    )


# ============================================================
# TEXT
# ============================================================

def text_analysis():

    text = get_screen_text()

    if not text:
        return "I couldn't find readable text on the screen."

    # Ask the reasoning model to select useful text
    return reason_about_screen(
        "What are the most important pieces of readable text on my screen? Ignore URLs and unimportant UI labels.",
        text,
        "The text was extracted directly from the screen using OCR."
    )


# ============================================================
# VISUAL QUESTION
# ============================================================

def visual_question(question):

    text = get_screen_text()

    vision = get_visual_context(
        f"""
Look carefully at the computer screen.

The user asks:

{question}

Identify only visual evidence relevant to answering
that question.

Do not guess.
"""
    )

    return reason_about_screen(
        question,
        text,
        vision
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
    print(" SPIDEY SCREEN VISION V3 TEST")
    print("================================")

    print("\n--- ACTIVITY ---")
    print(analyze_screen("activity"))

    print("\n--- ERROR ---")
    print(analyze_screen("error"))
