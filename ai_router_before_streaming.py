from dotenv import load_dotenv
load_dotenv()

import re
import os
from groq import Groq


GROQ_MODEL = "openai/gpt-oss-20b"


# ============================================================
# FAST SPIDEY AI ROUTER
#
# Simple  ? Groq
# Complex ? Gemini
# Math    ? Groq for now
# ============================================================

groq_client = Groq(
    api_key=os.environ["GROQ_API_KEY"]
)


COMPLEX_TASKS = [
    "summarize",
    "summary",
    "meeting notes",
    "action items",
    "rewrite",
    "rewrite this",
    "email",
    "presentation",
    "presentation outline",
    "linkedin",
    "linkedin post",
    "brainstorm",
    "study notes",
    "translate",
    "translation",
    "analyze",
    "analysis",
    "compare",
    "research",
    "report",
    "project plan",
    "create a plan",
    "code",
    "program",
    "python",
    "javascript",
    "debug",
    "debugging",
]


COMPLEX_SIGNALS = [
    "in detail",
    "detailed",
    "step by step",
    "step-by-step",
    "deep dive",
    "thoroughly",
    "explain why",
    "explain how",
    "advantages and disadvantages",
    "pros and cons",
    "difference between",
    "multiple",
    "several",
]


SIMPLE_PATTERNS = [
    r"^hi\b",
    r"^hello\b",
    r"^hey\b",
    r"^thanks\b",
    r"^thank you\b",
    r"^good morning\b",
    r"^good afternoon\b",
    r"^good evening\b",
    r"^how are you\b",
    r"^what('?s| is) your name\b",
    r"^who are you\b",
]


def is_deterministic_request(command):
    text = command.lower().strip()

    if re.fullmatch(r"[\d\s\+\-\*\/\(\)\.%]+", text):
        return True

    return False


def is_complex_request(command):
    text = command.lower().strip()

    for pattern in SIMPLE_PATTERNS:
        if re.search(pattern, text):
            return False

    for keyword in COMPLEX_TASKS:
        if keyword in text:
            return True

    for signal in COMPLEX_SIGNALS:
        if signal in text:
            return True

    if len(text.split()) >= 45:
        return True

    instruction_words = [
        "and then",
        "also",
        "additionally",
        "then create",
        "then explain",
        "and create",
        "and explain",
    ]

    if any(word in text for word in instruction_words):
        return True

    return False


def ask_groq(prompt):
    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are SPIDEY, a fast personal AI assistant. "
                    "Always identify yourself as SPIDEY, never as ChatGPT. "
                    "Be concise, natural, helpful, and conversational. "
                    "For simple questions, answer in 1-3 sentences. "
                    "Do not use tables, sections, long explanations, "
                    "or unnecessary details unless the user explicitly "
                    "asks for a detailed answer."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
        max_completion_tokens=250
    )
    return response.choices[0].message.content.strip()


def route_ai_request(prompt, gemini_function):

    if is_complex_request(prompt):
        print("AI ROUTER: COMPLEX REQUEST ? GEMINI")
        reply = gemini_function(prompt)
        return reply, "gemini"

    print("AI ROUTER: SIMPLE REQUEST ? GROQ")

    try:
        reply = ask_groq(prompt)

        if reply:
            print("AI ROUTER: GROQ RESPONSE RECEIVED")
            return reply, "groq"

        raise RuntimeError("Groq returned an empty response.")

    except Exception as e:
        print()
        print("AI ROUTER: GROQ FAILED")
        print("ERROR:", repr(e))
        print("AI ROUTER: FALLING BACK TO GEMINI")
        print()

        reply = gemini_function(prompt)
        return reply, "gemini_fallback"


