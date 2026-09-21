import os
import base64
import pyautogui
import ollama


# ============================================================
# SCREEN VISION SETTINGS
# ============================================================

VISION_MODEL = "moondream"

SCREENSHOT_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "spidey_screen.png"
)


# ============================================================
# CAPTURE SCREEN
# ============================================================

def capture_screen():
    """Capture the entire primary screen."""

    try:
        screenshot = pyautogui.screenshot()

        screenshot.save(SCREENSHOT_FILE)

        print("VISION: Screen captured.")
        print("VISION: Saved to:", SCREENSHOT_FILE)

        return SCREENSHOT_FILE

    except Exception as e:

        print("VISION: Screenshot error:", e)

        return None


# ============================================================
# ANALYZE SCREEN
# ============================================================

def analyze_screen(question="Describe what is visible on my screen."):
    """Capture and analyze the current screen using Ollama vision."""

    image_path = capture_screen()

    if not image_path:
        return "I couldn't capture your screen."

    try:

        response = ollama.chat(
            model=VISION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": question,
                    "images": [image_path]
                }
            ]
        )

        answer = response["message"]["content"].strip()

        print()
        print("VISION:", answer)
        print()

        return answer

    except Exception as e:

        print("VISION: AI error:", e)

        return (
            "I captured the screen, but I couldn't "
            "analyze it."
        )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("================================")
    print("       SPIDEY SCREEN VISION")
    print("================================")
    print()

    result = analyze_screen()

    print("SPIDEY:", result)