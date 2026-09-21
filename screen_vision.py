from dotenv import load_dotenv
load_dotenv()

import base64
import os

import pyautogui
from groq import Groq

VISION_MODEL = "qwen/qwen3.6-27b"
SCREENSHOT_PATH = "spidey_screen.jpg"

groq_client = Groq(
    api_key=os.environ["GROQ_API_KEY"]
)


def analyze_screen(question="What do you see in this image?"):
    print("[VISION] Capturing screen...")

    screenshot = pyautogui.screenshot()

    if screenshot.width > 1280:
        ratio = 1280 / screenshot.width
        screenshot = screenshot.resize(
            (1280, int(screenshot.height * ratio))
        )

    screenshot.save(
        SCREENSHOT_PATH,
        format="JPEG",
        quality=70
    )

    print("[VISION] Analyzing...")

    try:
        with open(SCREENSHOT_PATH, "rb") as image_file:
            image_data = base64.b64encode(
                image_file.read()
            ).decode("utf-8")

        response = groq_client.chat.completions.create(
            model=VISION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": question,
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": (
                                    f"data:image/jpeg;base64,"
                                    f"{image_data}"
                                )
                            },
                        },
                    ],
                }
            ],
            temperature=0.2,
            max_completion_tokens=500,
        )

        return response.choices[0].message.content.strip()

    finally:
        if os.path.exists(SCREENSHOT_PATH):
            os.remove(SCREENSHOT_PATH)


if __name__ == "__main__":
    result = analyze_screen()

    print("\n[SPIDEY]:")
    print(result)
