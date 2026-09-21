import time
import os

print()
print("=" * 70)
print("           SPIDEY REAL AI ROUTER TEST")
print("=" * 70)

import main
import ai_router

# ------------------------------------------------------------
# 1. GEMINI DIRECT
# ------------------------------------------------------------

print()
print("[1] GEMINI DIRECT TEST")
print("-" * 70)

try:
    start = time.perf_counter()

    reply = main.ask_gemini(
        "Reply with exactly: SPIDEY GEMINI ROUTER OK"
    )

    elapsed = time.perf_counter() - start

    print("PROVIDER : GEMINI")
    print("TIME     :", f"{elapsed:.3f}s")
    print("REPLY    :", repr(reply))

    if reply and "SPIDEY GEMINI ROUTER OK" in reply:
        print("STATUS   : PASS")
    else:
        print("STATUS   : FAIL")

except Exception as e:
    print("STATUS   : FAIL")
    print("ERROR    :", repr(e))


# ------------------------------------------------------------
# 2. GROQ DIRECT
# ------------------------------------------------------------

print()
print("[2] GROQ DIRECT TEST")
print("-" * 70)

try:
    start = time.perf_counter()

    reply = ai_router.ask_groq(
        "Reply with exactly: SPIDEY GROQ ROUTER OK"
    )

    elapsed = time.perf_counter() - start

    print("PROVIDER : GROQ")
    print("TIME     :", f"{elapsed:.3f}s")
    print("REPLY    :", repr(reply))

    if reply and "SPIDEY GROQ ROUTER OK" in reply:
        print("STATUS   : PASS")
    else:
        print("STATUS   : FAIL")

except Exception as e:
    print("STATUS   : FAIL")
    print("ERROR    :", repr(e))


# ------------------------------------------------------------
# 3. SIMPLE ROUTING
# ------------------------------------------------------------

print()
print("[3] SIMPLE REQUEST ROUTING")
print("-" * 70)

try:
    start = time.perf_counter()

    reply, provider = ai_router.route_ai_request(
        "What is 25 plus 25?",
        main.ask_gemini
    )

    elapsed = time.perf_counter() - start

    print("REQUEST  : What is 25 plus 25?")
    print("EXPECTED : GROQ")
    print("PROVIDER :", provider)
    print("TIME     :", f"{elapsed:.3f}s")
    print("REPLY    :", repr(reply))

    if provider == "groq":
        print("STATUS   : PASS")
    else:
        print("STATUS   : FAIL")

except Exception as e:
    print("STATUS   : FAIL")
    print("ERROR    :", repr(e))


# ------------------------------------------------------------
# 4. COMPLEX ROUTING
# ------------------------------------------------------------

print()
print("[4] COMPLEX REQUEST ROUTING")
print("-" * 70)

try:
    start = time.perf_counter()

    reply, provider = ai_router.route_ai_request(
        "Explain step by step how neural networks learn through backpropagation.",
        main.ask_gemini
    )

    elapsed = time.perf_counter() - start

    print("REQUEST  : Neural network backpropagation")
    print("EXPECTED : GEMINI")
    print("PROVIDER :", provider)
    print("TIME     :", f"{elapsed:.3f}s")
    print("REPLY    :", repr(reply))

    if provider == "gemini":
        print("STATUS   : PASS")
    else:
        print("STATUS   : FAIL")

except Exception as e:
    print("STATUS   : FAIL")
    print("ERROR    :", repr(e))


# ------------------------------------------------------------
# 5. ROUTER CLASSIFICATION
# ------------------------------------------------------------

print()
print("[5] ROUTER CLASSIFICATION")
print("-" * 70)

tests = [
    ("Hello Spidey", "GROQ"),
    ("What is 2 plus 2?", "GROQ"),
    ("What is Python?", "GROQ"),
    ("Summarize this meeting for me", "GEMINI"),
    ("Explain quantum computing in detail", "GEMINI"),
    ("Compare Python and JavaScript in detail", "GEMINI"),
]

for prompt, expected in tests:

    try:
        complex_request = ai_router.is_complex_request(prompt)

        actual = "GEMINI" if complex_request else "GROQ"

        status = "PASS" if actual == expected else "FAIL"

        print(
            f"[{status}] "
            f"EXPECTED={expected:<6} "
            f"ACTUAL={actual:<6} "
            f"| {prompt}"
        )

    except Exception as e:

        print(
            f"[FAIL] {prompt}"
        )
        print(
            "       ERROR:",
            repr(e)
        )


# ------------------------------------------------------------
# 6. ENVIRONMENT
# ------------------------------------------------------------

print()
print("[6] API CONFIGURATION")
print("-" * 70)

print(
    "GEMINI KEY :",
    "SET" if os.getenv("GEMINI_API_KEY") else "MISSING"
)

print(
    "GROQ KEY   :",
    "SET" if os.getenv("GROQ_API_KEY") else "MISSING"
)

print(
    "GEMINI MODEL:",
    getattr(main, "GEMINI_MODEL", "NOT FOUND")
)

print(
    "GROQ MODEL:",
    getattr(ai_router, "GROQ_MODEL", "NOT FOUND")
)


# ------------------------------------------------------------
# SUMMARY
# ------------------------------------------------------------

print()
print("=" * 70)
print("                 ROUTER TEST COMPLETE")
print("=" * 70)
print()
