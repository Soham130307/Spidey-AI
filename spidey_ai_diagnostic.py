import time
import main
import ai_router

print()
print("=" * 65)
print("        SPIDEY REAL AI BACKEND DIAGNOSTIC")
print("=" * 65)

# ------------------------------------------------------------
# GEMINI DIRECT
# ------------------------------------------------------------

print()
print("[1] GEMINI DIRECT TEST")
print("-" * 65)

try:
    start = time.perf_counter()

    reply = main.ask_gemini(
        "Reply with exactly: SPIDEY GEMINI ONLINE"
    )

    elapsed = time.perf_counter() - start

    print("MODEL :", main.GEMINI_MODEL)
    print("TIME  :", f"{elapsed:.3f}s")
    print("REPLY :", repr(reply))

    if reply and "SPIDEY GEMINI ONLINE" in reply:
        print("STATUS: PASS")
    else:
        print("STATUS: FAIL")

except Exception as e:
    print("STATUS: FAIL")
    print("ERROR :", type(e).__name__, repr(e))


# ------------------------------------------------------------
# GROQ DIRECT
# ------------------------------------------------------------

print()
print("[2] GROQ DIRECT TEST")
print("-" * 65)

try:
    start = time.perf_counter()

    reply = ai_router.ask_groq(
        "Reply with exactly: SPIDEY GROQ ONLINE"
    )

    elapsed = time.perf_counter() - start

    print("MODEL :", ai_router.GROQ_MODEL)
    print("TIME  :", f"{elapsed:.3f}s")
    print("REPLY :", repr(reply))

    if reply and "SPIDEY GROQ ONLINE" in reply:
        print("STATUS: PASS")
    else:
        print("STATUS: FAIL")

except Exception as e:
    print("STATUS: FAIL")
    print("ERROR :", type(e).__name__, repr(e))


# ------------------------------------------------------------
# ROUTING TEST - SIMPLE
# ------------------------------------------------------------

print()
print("[3] SIMPLE REQUEST ROUTING")
print("-" * 65)

try:
    prompt = "What is 2 plus 2?"

    print("REQUEST:", prompt)
    print("EXPECTED: GROQ")

    start = time.perf_counter()

    reply, provider = ai_router.route_ai_request(
        prompt,
        main.ask_gemini
    )

    elapsed = time.perf_counter() - start

    print("PROVIDER:", provider)
    print("TIME    :", f"{elapsed:.3f}s")
    print("REPLY   :", repr(reply))

    if provider in ("groq", "groq_streaming"):
        print("STATUS  : PASS")
    elif provider == "gemini_fallback":
        print("STATUS  : WARNING - GROQ FAILED, GEMINI FALLBACK USED")
    else:
        print("STATUS  : FAIL")

except Exception as e:
    print("STATUS  : FAIL")
    print("ERROR   :", type(e).__name__, repr(e))


# ------------------------------------------------------------
# ROUTING TEST - COMPLEX
# ------------------------------------------------------------

print()
print("[4] COMPLEX REQUEST ROUTING")
print("-" * 65)

try:
    prompt = (
        "Explain step by step the advantages and disadvantages "
        "of using artificial intelligence in education."
    )

    print("REQUEST:", prompt)
    print("EXPECTED: GEMINI")

    start = time.perf_counter()

    reply, provider = ai_router.route_ai_request(
        prompt,
        main.ask_gemini
    )

    elapsed = time.perf_counter() - start

    print("PROVIDER:", provider)
    print("TIME    :", f"{elapsed:.3f}s")
    print("REPLY   :", repr(reply)[:500])

    if provider == "gemini":
        print("STATUS  : PASS")
    else:
        print("STATUS  : FAIL")

except Exception as e:
    print("STATUS  : FAIL")
    print("ERROR   :", type(e).__name__, repr(e))


# ------------------------------------------------------------
# ROUTER LOGIC TEST
# ------------------------------------------------------------

print()
print("[5] ROUTER LOGIC")
print("-" * 65)

tests = [
    ("Hello", "GROQ"),
    ("What is 25 + 25?", "GROQ"),
    ("What is Python?", "GROQ"),
    ("Summarize this meeting", "GEMINI"),
    ("Explain step by step how neural networks work", "GEMINI"),
    ("Compare Python and JavaScript in detail", "GEMINI"),
]

for prompt, expected in tests:
    complex_request = ai_router.is_complex_request(prompt)

    actual = "GEMINI" if complex_request else "GROQ"

    status = "PASS" if actual == expected else "FAIL"

    print(
        f"[{status}] {actual:<6} | "
        f"Expected {expected:<6} | {prompt}"
    )


# ------------------------------------------------------------
# FINAL
# ------------------------------------------------------------

print()
print("=" * 65)
print("                 DIAGNOSTIC COMPLETE")
print("=" * 65)
print()
