from pathlib import Path
"""
SPIDEY Productivity Features

Current features:
1. Meeting Notes Summarizer
2. Action Item Generator

The AI function is injected from main.py so this module does
not create a second AI client or cause circular imports.
"""

from typing import Callable


def _clean(text: str) -> str:
    return " ".join(str(text).strip().split())


def _call_ai(ai_call: Callable[[str], str], prompt: str) -> str:
    if not callable(ai_call):
        raise ValueError("AI callback is not available.")

    result = ai_call(prompt)

    if result is None:
        raise RuntimeError("AI returned no response.")

    result = str(result).strip()

    if not result:
        raise RuntimeError("AI returned an empty response.")

    return result


def summarize_meeting_notes(
    notes: str,
    ai_call: Callable[[str], str],
) -> str:
    """
    Summarize meeting notes using only the supplied notes.
    """

    notes = str(notes).strip()

    if not notes:
        raise ValueError("Meeting notes are empty.")

    prompt = f"""
You are SPIDEY's Meeting Notes Summarizer.

Summarize the meeting notes below using ONLY the information
provided in the notes. Do not invent names, decisions, dates,
deadlines, or facts.

Return a concise, useful structure:

MEETING SUMMARY
- 2-5 bullet points covering the main discussion.

KEY DECISIONS
- List decisions that are explicitly present.
- If none are present, say: None specified.

IMPORTANT DISCUSSION POINTS
- List the most important topics.

NEXT STEPS
- List explicitly mentioned next steps.
- If none are present, say: None specified.

Use "Not specified" whenever the notes do not contain the
required information.

MEETING NOTES:
----------------
{notes}
----------------
"""

    return _call_ai(ai_call, prompt)


def generate_action_items(
    notes: str,
    ai_call: Callable[[str], str],
) -> str:
    """
    Extract actionable tasks from meeting notes.
    """

    notes = str(notes).strip()

    if not notes:
        raise ValueError("Meeting notes are empty.")

    prompt = f"""
You are SPIDEY's Action Item Generator.

Extract actionable tasks ONLY from the meeting notes below.

Do NOT invent tasks, owners, deadlines, priorities, or other
information that is not supported by the notes.

Return:

ACTION ITEMS

1. Task:
   Owner:
   Deadline:
   Priority:

2. Task:
   Owner:
   Deadline:
   Priority:

Continue for all clearly identifiable action items.

Rules:
- Owner should be "Not specified" if absent.
- Deadline should be "Not specified" if absent.
- Priority should be "Not specified" unless the notes clearly
  indicate a priority.
- Do not turn general discussion into an action item.
- If there are no actionable tasks, say:
  "No clear action items found."

MEETING NOTES:
----------------
{notes}
----------------
"""

    return _call_ai(ai_call, prompt)


# ============================================================
# EMAIL REWRITER
# ============================================================

def rewrite_email(email, ai_call, style="professional"):
    """
    Rewrite email text while preserving the original meaning.

    The email is supplied by SPIDEY from the Windows clipboard.
    """

    email = str(email or "").strip()
    style = str(style or "professional").strip().lower()

    if not email:
        raise ValueError("No email text was provided.")

    style_instructions = {
        "professional": (
            "Rewrite the email in a professional and polished tone."
        ),
        "formal": (
            "Rewrite the email in a formal and respectful tone."
        ),
        "friendly": (
            "Rewrite the email in a friendly, natural and warm tone "
            "while remaining appropriate for email."
        ),
        "polite": (
            "Rewrite the email to sound more polite, respectful and "
            "considerate."
        ),
        "concise": (
            "Rewrite the email to be concise and clear while preserving "
            "all important information."
        ),
        "short": (
            "Rewrite the email in a shorter and more concise form "
            "without losing important information."
        ),
        "clear": (
            "Rewrite the email to make it clearer, easier to understand "
            "and grammatically correct."
        ),
    }

    instruction = style_instructions.get(
        style,
        style_instructions["professional"]
    )

    prompt = f"""
You are SPIDEY's Email Rewriter.

Rewrite the email below.

REWRITING STYLE:
{style}

INSTRUCTION:
{instruction}

STRICT RULES:
- Preserve the original meaning and intent.
- Do not invent facts, dates, names, reasons or commitments.
- Correct grammar, spelling and awkward wording.
- Keep important details from the original.
- Return ONLY the rewritten email.
- Do not explain what you changed.
- Do not add commentary before or after the email.

ORIGINAL EMAIL:
{email}
"""

    result = ai_call(prompt)

    if not result:
        raise RuntimeError("AI returned an empty email.")

    return result.strip()


def get_clipboard_text():
    """
    Read text directly from the Windows clipboard.
    No paste operation is required.
    """

    try:
        import tkinter as tk

        root = tk.Tk()
        root.withdraw()

        try:
            text = root.clipboard_get()
        finally:
            root.destroy()

        return str(text or "").strip()

    except Exception as e:
        print("SPIDEY CLIPBOARD ERROR:", e)
        return ""


def save_email_to_spidey_output(email_text, style="professional"):
    """
    Save the rewritten email to:
        Desktop\\SPIDEY Output

    The generated .txt file is then opened in Windows Notepad.
    """

    import os
    from datetime import datetime
    import subprocess

    desktop = Path(
        os.path.join(
            os.path.expanduser("~"),
            "Desktop"
        )
    )

    output_dir = desktop / "SPIDEY Output"
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    filename = (
        f"rewritten_email_{style}_{timestamp}.txt"
    )

    output_file = output_dir / filename

    output_file.write_text(
        email_text,
        encoding="utf-8"
    )

    print(
        "SPIDEY EMAIL SAVED:",
        str(output_file)
    )

    try:
        subprocess.Popen(
            ["notepad.exe", str(output_file)]
        )
    except Exception as e:
        print(
            "SPIDEY NOTEPAD ERROR:",
            e
        )

    return str(output_file)


# ============================================================
# BRAINSTORM IDEAS
# ============================================================

def brainstorm_ideas(
    topic: str,
    ai_call: Callable[[str], str],
    count: int = 10,
) -> str:
    """
    Generate multiple useful ideas around a supplied topic.
    """

    topic = str(topic or "").strip()

    if not topic:
        raise ValueError("Brainstorm topic is empty.")

    try:
        count = int(count)
    except Exception:
        count = 10

    count = max(3, min(count, 20))

    prompt = f"""
You are SPIDEY's Brainstorm Ideas assistant.

Generate {count} useful and creative ideas for the topic below.

TOPIC:
{topic}

Return the following structure:

BRAINSTORM IDEAS

1. IDEA NAME
   Concept:
   Problem / Opportunity:
   Key Features:
   Potential Use:

2. IDEA NAME
   Concept:
   Problem / Opportunity:
   Key Features:
   Potential Use:

Continue until you have exactly {count} ideas.

RULES:
- Make the ideas meaningfully different from each other.
- Avoid repeating the same concept with different names.
- Keep each idea practical and understandable.
- Be creative but realistic.
- Do not invent facts about existing companies, products,
  statistics, or research.
- Do not explain the brainstorming process.
- Return ONLY the brainstorm results.

TOPIC:
----------------
{topic}
----------------
"""

    return _call_ai(ai_call, prompt)


# LINKEDIN POST GENERATOR
def generate_linkedin_post(topic, ai_call, style="professional"):
    topic = str(topic or "").strip()
    style = str(style or "professional").strip().lower()

    if not topic:
        raise ValueError("LinkedIn post topic is empty.")

    style_instructions = {
        "professional": "Write in a polished, professional LinkedIn tone.",
        "engaging": "Write in an engaging, energetic LinkedIn tone.",
        "casual": "Write in a natural, friendly and conversational tone.",
        "storytelling": "Use a concise storytelling style with a strong opening.",
    }

    instruction = style_instructions.get(
        style,
        style_instructions["professional"]
    )

    prompt = f"""
You are SPIDEY's LinkedIn Post Generator.

Create a high-quality LinkedIn post based ONLY on the
information provided by the user.

TOPIC / USER INFORMATION:
{topic}

STYLE:
{style}

INSTRUCTION:
{instruction}

STRICT RULES:
- Do not invent achievements, companies, statistics, certificates,
  technologies, experiences, names, dates or results.
- Preserve the user's actual meaning.
- Make the opening engaging without using clickbait.
- Keep the post suitable for LinkedIn.
- Use short paragraphs for readability.
- Use emojis only when they naturally fit.
- Include a concise closing statement.
- Add 4-8 relevant hashtags.
- Do not mention that you are an AI.
- Do not explain what you changed.
- Return ONLY the final LinkedIn post.

LINKEDIN POST:
----------------
"""

    result = _call_ai(ai_call, prompt)

    if not result:
        raise RuntimeError("AI returned an empty LinkedIn post.")

    return result.strip()
# TRANSLATION
def translate_text(text, target_language, ai_call):
    text = str(text or "").strip()
    target_language = str(target_language or "").strip()

    if not text:
        raise ValueError("Translation text is empty.")

    if not target_language:
        raise ValueError("Target language is required.")

    prompt = f"""
You are SPIDEY's Translation Assistant.

Translate the text below into {target_language}.

SOURCE TEXT:
{text}

STRICT RULES:
- Preserve the exact meaning and intent.
- Do not add information.
- Do not remove information.
- Preserve names, numbers, dates and important terminology.
- Preserve the original tone and level of formality.
- Return ONLY the translation.
- Do not explain the translation.
- Do not add quotation marks unless they are part of the source.

TEXT TO TRANSLATE:
----------------
{text}
----------------
"""

    result = _call_ai(ai_call, prompt)

    if not result:
        raise RuntimeError("AI returned an empty translation.")

    return result.strip()
