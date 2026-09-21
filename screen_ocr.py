import pyautogui
import pytesseract
from PIL import ImageOps, ImageEnhance
import os

TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
SCREENSHOT_PATH = "spidey_ocr.png"

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


def read_screen():
    print("[OCR] Capturing screen...")

    screenshot = pyautogui.screenshot()

    image = ImageOps.grayscale(screenshot)
    image = ImageEnhance.Contrast(image).enhance(2.0)

    image = image.resize(
        (image.width * 2, image.height * 2)
    )

    image.save(SCREENSHOT_PATH)

    print("[OCR] Reading text...")

    text = pytesseract.image_to_string(
        image,
        config="--psm 6"
    )

    lines = []

    for line in text.splitlines():
        line = line.strip()

        if line:
            lines.append(line)

    result = "\n".join(lines)

    if os.path.exists(SCREENSHOT_PATH):
        os.remove(SCREENSHOT_PATH)

    return result


if __name__ == "__main__":
    result = read_screen()

    print("\n[OCR RESULT]")
    print(result)