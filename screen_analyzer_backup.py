import screen_ocr
import screen_vision


def analyze_screen(mode="general"):

    # =========================
    # TEXT MODE
    # =========================
    if mode == "text":
        print("[ANALYZER] Using OCR...")

        text = screen_ocr.read_screen()

        if not text:
            return "I couldn't find any readable text on the screen."

        # Remove common browser/UI noise
        lines = []

        for line in text.splitlines():
            line = line.strip()

            if not line:
                continue

            # Ignore browser URLs
            if line.startswith(("http://", "https://", "www.")):
                continue

            # Ignore very short UI fragments
            if len(line) < 2:
                continue

            lines.append(line)

        # Limit the amount of raw OCR returned
        if len(lines) > 20:
            lines = lines[:20]

        return "\n".join(lines)


    # =========================
    # ACTIVITY MODE
    # =========================
    if mode == "activity":
        print("[ANALYZER] Using vision...")

        return screen_vision.analyze_screen(
            """Look carefully at this computer screen.

Determine what the user is currently doing.

Use only visible evidence from the screen.
Identify:
1. The application or website being used.
2. The user's apparent activity.
3. Any specific task visible on the screen.

Do NOT guess.
Do NOT say "maybe", "perhaps", or "or something".
If you cannot determine the exact activity, describe only what is clearly visible.

Answer in 1-2 short sentences."""
        )


    # =========================
    # APP MODE
    # =========================
    if mode == "app":
        print("[ANALYZER] Using vision...")

        return screen_vision.analyze_screen(
            """Look at this computer screen.

Identify the application or website currently visible.

Use visible evidence such as the interface, title bar, logo, or distinctive layout.

Do not guess.
If the exact application cannot be determined, say what type of application or website it appears to be.

Answer briefly in one sentence."""
        )


    # =========================
    # ERROR MODE
    # =========================
    if mode == "error":
        print("[ANALYZER] Using OCR + vision...")

        text = screen_ocr.read_screen()

        vision = screen_vision.analyze_screen(
            """Look carefully at this computer screen.

Determine whether there is a clearly visible:
- error
- warning
- failure
- problem
- red error message
- dialog reporting an issue

Do not guess.

If there is no obvious problem, say:
"No obvious error is visible."

If there is an error, briefly describe what it says and where it appears."""
        )

        return (
            "TEXT FOUND:\n"
            + text
            + "\n\nVISUAL ANALYSIS:\n"
            + vision
        )


    # =========================
    # GENERAL MODE
    # =========================
    print("[ANALYZER] Using vision...")

    return screen_vision.analyze_screen(
        """Look at this computer screen.

Briefly describe the important things visible on the screen.

Focus on:
- the main application or website
- important content
- what appears to be happening

Do not guess.
Do not invent details.

Answer in 1-2 short sentences."""
    )


# =========================
# TEST
# =========================

if __name__ == "__main__":

    print("\n--- GENERAL ---")
    print(analyze_screen("general"))

    print("\n--- TEXT ---")
    print(analyze_screen("text"))

    print("\n--- APPLICATION ---")
    print(analyze_screen("app"))

    print("\n--- ACTIVITY ---")
    print(analyze_screen("activity"))