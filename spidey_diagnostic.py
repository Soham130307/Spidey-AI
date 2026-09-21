import os
import sys
import time
import ast
import importlib
import traceback

print()
print("=" * 65)
print("             SPIDEY FULL SYSTEM DIAGNOSTIC")
print("=" * 65)
print()

passed = 0
failed = 0
warnings = 0

def result(name, status, detail=""):
    global passed, failed, warnings

    if status == "PASS":
        symbol = "[PASS]"
        passed += 1
    elif status == "FAIL":
        symbol = "[FAIL]"
        failed += 1
    else:
        symbol = "[WARN]"
        warnings += 1

    print(f"{symbol:<7} {name}")
    if detail:
        print(f"        {detail}")

# ------------------------------------------------------------
# 1. PYTHON
# ------------------------------------------------------------
print("SYSTEM")
print("-" * 65)

result(
    "Python",
    "PASS",
    f"{sys.version.split()[0]} | {sys.executable}"
)

# ------------------------------------------------------------
# 2. MAIN.PY COMPILE
# ------------------------------------------------------------
try:
    with open("main.py", "r", encoding="utf-8") as f:
        source = f.read()

    ast.parse(source, filename="main.py")
    result("main.py syntax", "PASS")
except Exception as e:
    result("main.py syntax", "FAIL", repr(e))

# ------------------------------------------------------------
# 3. CHECK OLLAMA REFERENCES
# ------------------------------------------------------------
try:
    ollama_calls = [
        line for line in source.splitlines()
        if "ollama." in line
    ]

    if ollama_calls:
        result(
            "Ollama calls removed",
            "FAIL",
            f"Found {len(ollama_calls)} ollama. reference(s)"
        )
    else:
        result("Ollama calls removed", "PASS")
except Exception as e:
    result("Ollama scan", "WARN", repr(e))

# ------------------------------------------------------------
# 4. REQUIRED IMPORTS
# ------------------------------------------------------------
print()
print("PYTHON MODULES")
print("-" * 65)

modules = [
    "google.genai",
    "groq",
    "memory",
    "pygame",
    "cv2",
    "mediapipe",
    "sounddevice",
    "speech_recognition",
    "edge_tts",
    "pyautogui",
]

for module in modules:
    try:
        importlib.import_module(module)
        result(module, "PASS")
    except Exception as e:
        result(module, "FAIL", str(e))

# ------------------------------------------------------------
# 5. IMPORT SPIDEY
# ------------------------------------------------------------
print()
print("SPIDEY CORE")
print("-" * 65)

try:
    import main
    result("Import main.py", "PASS")
except Exception as e:
    result("Import main.py", "FAIL", repr(e))
    print()
    print("Cannot continue core tests because main.py failed to import.")
    sys.exit(1)

# ------------------------------------------------------------
# 6. GEMINI
# ------------------------------------------------------------
print()
print("AI BACKENDS")
print("-" * 65)

try:
    model = main.GEMINI_MODEL
    client = main.gemini_client

    start = time.perf_counter()

    response = client.models.generate_content(
        model=model,
        contents="Reply with exactly: SPIDEY GEMINI OK",
        config={
            "temperature": 0.1,
            "max_output_tokens": 1000
        }
    )

    elapsed = time.perf_counter() - start
    text = response.text

    if text and "SPIDEY GEMINI OK" in text:
        result(
            "Gemini API",
            "PASS",
            f"Model={model} | {elapsed:.3f}s | {text!r}"
        )
    else:
        result(
            "Gemini API",
            "FAIL",
            f"Model={model} | {elapsed:.3f}s | Response={text!r}"
        )

except Exception as e:
    result(
        "Gemini API",
        "FAIL",
        f"{type(e).__name__}: {e}"
    )

# ------------------------------------------------------------
# 7. GROQ
# ------------------------------------------------------------
try:
    groq_client = None

    # Try common names used by SPIDEY
    for attr in ["groq_client", "client_groq", "groq"]:
        if hasattr(main, attr):
            candidate = getattr(main, attr)
            if candidate is not None:
                groq_client = candidate
                break

    if groq_client is None:
        result(
            "Groq API",
            "FAIL",
            "Could not find a Groq client in main.py"
        )
    else:
        groq_model = None

        for attr in [
            "GROQ_MODEL",
            "GROQ_MODEL_NAME",
            "FAST_MODEL"
        ]:
            if hasattr(main, attr):
                groq_model = getattr(main, attr)
                break

        if not groq_model:
            groq_model = "llama-3.1-8b-instant"

        start = time.perf_counter()

        response = groq_client.chat.completions.create(
            model=groq_model,
            messages=[
                {
                    "role": "user",
                    "content": "Reply with exactly: SPIDEY GROQ OK"
                }
            ],
            temperature=0.1,
            max_tokens=30
        )

        elapsed = time.perf_counter() - start
        text = response.choices[0].message.content

        if text and "SPIDEY GROQ OK" in text:
            result(
                "Groq API",
                "PASS",
                f"Model={groq_model} | {elapsed:.3f}s | {text!r}"
            )
        else:
            result(
                "Groq API",
                "FAIL",
                f"Model={groq_model} | Response={text!r}"
            )

except Exception as e:
    result(
        "Groq API",
        "FAIL",
        f"{type(e).__name__}: {e}"
    )

# ------------------------------------------------------------
# 8. INTENT CLASSIFIER
# ------------------------------------------------------------
print()
print("AI ROUTING")
print("-" * 65)

try:
    if hasattr(main, "detect_intent"):
        start = time.perf_counter()

        intent = main.detect_intent(
            "What is the capital of France?"
        )

        elapsed = time.perf_counter() - start

        if intent:
            result(
                "Intent classifier",
                "PASS",
                f"{elapsed:.3f}s | {intent!r}"
            )
        else:
            result(
                "Intent classifier",
                "FAIL",
                "Returned empty result"
            )
    else:
        result(
            "Intent classifier",
            "FAIL",
            "detect_intent() not found"
        )

except Exception as e:
    result(
        "Intent classifier",
        "FAIL",
        f"{type(e).__name__}: {e}"
    )

# ------------------------------------------------------------
# 9. MEMORY
# ------------------------------------------------------------
print()
print("CORE FEATURES")
print("-" * 65)

try:
    if hasattr(main, "memory"):
        result("Memory system", "PASS", "memory module loaded")
    else:
        result("Memory system", "WARN", "memory attribute not found")
except Exception as e:
    result("Memory system", "FAIL", repr(e))

# ------------------------------------------------------------
# 10. TTS
# ------------------------------------------------------------
try:
    if hasattr(main, "speak"):
        result("TTS function", "PASS", "speak() found")
    else:
        result("TTS function", "FAIL", "speak() not found")
except Exception as e:
    result("TTS function", "FAIL", repr(e))

# ------------------------------------------------------------
# 11. HUD
# ------------------------------------------------------------
try:
    if hasattr(main, "update_hud"):
        result("HUD bridge", "PASS", "update_hud() found")
    else:
        result("HUD bridge", "FAIL", "update_hud() not found")
except Exception as e:
    result("HUD bridge", "FAIL", repr(e))

# ------------------------------------------------------------
# 12. GESTURES
# ------------------------------------------------------------
try:
    gesture_names = [
        "gesture",
        "gesture_thread",
        "detect_gesture",
        "process_gesture"
    ]

    found = [
        name for name in gesture_names
        if hasattr(main, name)
    ]

    if found:
        result(
            "Gesture engine",
            "PASS",
            ", ".join(found)
        )
    else:
        result(
            "Gesture engine",
            "WARN",
            "Gesture functions not found by generic scan"
        )

except Exception as e:
    result("Gesture engine", "WARN", repr(e))

# ------------------------------------------------------------
# 13. SPOTIFY
# ------------------------------------------------------------
try:
    spotify_names = [
        name for name in dir(main)
        if "spotify" in name.lower()
    ]

    if spotify_names:
        result(
            "Spotify integration",
            "PASS",
            ", ".join(spotify_names[:10])
        )
    else:
        result(
            "Spotify integration",
            "WARN",
            "No Spotify functions detected"
        )

except Exception as e:
    result("Spotify integration", "WARN", repr(e))

# ------------------------------------------------------------
# 14. WAKE WORD
# ------------------------------------------------------------
try:
    wake_names = [
        name for name in dir(main)
        if "wake" in name.lower()
    ]

    if wake_names:
        result(
            "Wake-word system",
            "PASS",
            ", ".join(wake_names[:10])
        )
    else:
        result(
            "Wake-word system",
            "WARN",
            "Wake-word functions not detected"
        )

except Exception as e:
    result("Wake-word system", "WARN", repr(e))

# ------------------------------------------------------------
# SUMMARY
# ------------------------------------------------------------
print()
print("=" * 65)
print("                 DIAGNOSTIC SUMMARY")
print("=" * 65)

print(f"PASS    : {passed}")
print(f"FAIL    : {failed}")
print(f"WARNING : {warnings}")

print()

if failed == 0:
    print("OVERALL: ALL AUTOMATED TESTS PASSED")
else:
    print("OVERALL: SOME TESTS FAILED - SEE ABOVE")

print("=" * 65)
