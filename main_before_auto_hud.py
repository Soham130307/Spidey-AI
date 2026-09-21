import ollama
import memory
import sounddevice as sd
import speech_recognition as sr
import asyncio
import edge_tts
import subprocess
import uuid
import os
import time
import re
import tools
import pygame


# ============================================================
# SETTINGS
# ============================================================

SAMPLE_RATE = 16000
LISTEN_TIME = 5

MODEL = "llama3.2:3b"
VOICE = "en-US-GuyNeural"

recognizer = sr.Recognizer()
# ============================================================
# HUD CONNECTION
# ============================================================

HUD_URL = "http://127.0.0.1:8765/api/state"


def update_hud(state):

    try:

        import urllib.request
        import json

        data = json.dumps({
            "state": state
        }).encode("utf-8")

        request = urllib.request.Request(
            HUD_URL,
            data=data,
            headers={
                "Content-Type": "application/json"
            },
            method="POST"
        )

        urllib.request.urlopen(
            request,
            timeout=0.5
        )

    except Exception:
        # HUD may not be running.
        # Spidey continues working normally.
        pass

# ============================================================
# AI INTENT DETECTION
# ============================================================

def detect_intent(command):

    prompt = f"""
You are JARVIS's command classifier.

Classify the user's command.

Return ONLY one line in exactly this format:

OPEN_WEBSITE|name
OPEN_APP|name
OPEN_FOLDER|name
NORMAL_CHAT|none

Examples:

open Instagram
OPEN_WEBSITE|instagram

can you open Instagram for me
OPEN_WEBSITE|instagram

take me to GitHub
OPEN_WEBSITE|github

launch Reddit
OPEN_WEBSITE|reddit

open Discord
OPEN_APP|discord

can you launch Discord for me
OPEN_APP|discord

start Discord
OPEN_APP|discord

open calculator
OPEN_APP|calculator

open notepad
OPEN_APP|notepad

start VS Code
OPEN_APP|vscode

open my downloads
OPEN_FOLDER|downloads

what is the capital of India
NORMAL_CHAT|none

tell me a joke
NORMAL_CHAT|none

IMPORTANT:

Discord, Calculator, Notepad and VS Code are applications.

Instagram, YouTube, GitHub, Reddit, Spotify, Netflix,
Google and Facebook are websites.

Return ONLY the classification.

Do not explain.
Do not say that you opened anything.

User command:
{command}
"""

    try:

        response = ollama.chat(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        raw_result = response["message"]["content"].strip()

        # Get first non-empty line
        result = next(
            (
                line.strip()
                for line in raw_result.splitlines()
                if line.strip()
            ),
            "NORMAL_CHAT|none"
        )

        # Remove accidental markdown
        result = result.replace("`", "").strip()

        # Validate result
        match = re.match(
            r"^(OPEN_WEBSITE|OPEN_APP|OPEN_FOLDER|NORMAL_CHAT)\|(.+)$",
            result,
            re.IGNORECASE
        )

        if match:

            intent_type = match.group(1).upper()
            name = match.group(2).strip().lower()

            result = f"{intent_type}|{name}"

        else:

            result = "NORMAL_CHAT|none"

        print("INTENT:", result)

        return result

    except Exception as e:

        print("Intent error:", e)

        return "NORMAL_CHAT|none"


# ============================================================
# VOICE OUTPUT
# ============================================================

async def create_voice(text, filename):

    communicate = edge_tts.Communicate(
        text,
        VOICE
    )

    await communicate.save(filename)


def speak(text):

    print("JARVIS:", text)

    filename = f"jarvis_{uuid.uuid4().hex}.mp3"

    try:

        # Create the voice MP3
        asyncio.run(
            create_voice(
                text,
                filename
            )
        )

        # Start pygame audio
        pygame.mixer.init()

        # Load generated voice
        pygame.mixer.music.load(
            filename
        )

        # Play voice
        pygame.mixer.music.play()

        # Wait until JARVIS finishes speaking
        while pygame.mixer.music.get_busy():

            time.sleep(0.1)

        # Stop and close pygame
        pygame.mixer.music.stop()

        pygame.mixer.quit()

        # Delete temporary MP3
        if os.path.exists(filename):

            os.remove(filename)

    except Exception as e:

        print(
            "Voice error:",
            e
        )

        try:

            pygame.mixer.music.stop()
            pygame.mixer.quit()

        except Exception:

            pass

        # Clean up MP3 if it still exists
        try:

            if os.path.exists(filename):

                os.remove(filename)

        except Exception:

            pass

# ============================================================
# VOICE INPUT
# ============================================================

def listen():

    print("\nJARVIS: Listening...")

    try:

        audio = sd.rec(
            int(
                LISTEN_TIME *
                SAMPLE_RATE
            ),
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="int16"
        )

        sd.wait()

        audio_data = sr.AudioData(
            audio.tobytes(),
            SAMPLE_RATE,
            2
        )

        try:

            text = recognizer.recognize_google(
                audio_data
            )

            print(
                "You:",
                text
            )

            return text

        except sr.UnknownValueError:

            print(
                "JARVIS: I couldn't understand you."
            )

            return ""

        except sr.RequestError:

            print(
                "JARVIS: Speech recognition unavailable."
            )

            return ""

    except Exception as e:

        print(
            "Microphone error:",
            e
        )

        return ""


# ============================================================
# LOAD MEMORY
# ============================================================

try:

    saved_memories = memory.get_memories()

except Exception as e:

    print(
        "Memory loading error:",
        e
    )

    saved_memories = []


memory_text = ""

if saved_memories:

    memory_text = "\n".join(
        f"- {item[0]}"
        for item in saved_memories
    )


# ============================================================
# AI CONVERSATION
# ============================================================

messages = [

    {
        "role": "system",
        "content": f"""
You are JARVIS, a personal AI assistant.

Be helpful, intelligent, concise and natural.

Use the user's permanent memories when relevant.

Permanent memories:

{memory_text}
"""
    }

]


# ============================================================
# WEBSITE MAP
# ============================================================

WEBSITE_MAP = {

    "instagram":
        "https://www.instagram.com",

    "facebook":
        "https://www.facebook.com",

    "twitter":
        "https://twitter.com",

    "x":
        "https://x.com",

    "reddit":
        "https://www.reddit.com",

    "github":
        "https://github.com",

    "spotify":
        "https://open.spotify.com",

    "netflix":
        "https://www.netflix.com",

    "linkedin":
        "https://www.linkedin.com",

    "amazon":
        "https://www.amazon.com",

    "youtube":
        "https://www.youtube.com",

    "google":
        "https://www.google.com"

}


# ============================================================
# START JARVIS
# ============================================================

print()
print("================================")
# ============================================================
# SPIDEY ASSISTANT LOOP
# ============================================================

def run_spidey():

    print()
    print("================================")
    print("       SPIDEY IS ONLINE")
    print("================================")
    print()
    print("Speak to SPIDEY.")
    print("Say 'exit' to shut down.")
    print()

    speak(
        "Spidey is online. How can I help you?"
    )

    # ========================================================
    # MAIN LOOP
    # ========================================================

    while True:

               # ----------------------------------------------------
        # WAKE WORD
        # ----------------------------------------------------

        update_hud("STANDBY")

        user_input = listen()

        if not user_input:
            continue

        wake_command = user_input.lower().strip()

        # Ignore everything until "Hey Spidey" is heard
        if "hey spidey" not in wake_command:
            continue

        # ----------------------------------------------------
        # SPIDEY ACTIVATED
        # ----------------------------------------------------

        update_hud("LISTENING")

        speak(
            "Yes?"
        )

        # ----------------------------------------------------
        # LISTEN FOR ACTUAL COMMAND
        # ----------------------------------------------------

        user_input = listen()

        if not user_input:

            update_hud("STANDBY")

            continue

        update_hud("THINKING")
        # ----------------------------------------------------
        # CLEAN COMMAND
        # ----------------------------------------------------

        command = user_input.lower().strip()

        print(
            "DEBUG COMMAND:",
            repr(command)
        )

        # ====================================================
        # EXIT
        # ====================================================

        if command in [
            "exit",
            "quit",
            "shutdown",
            "goodbye",
            "shut down"
        ]:

            speak(
                "Goodbye. It was a pleasure assisting you."
            )

            try:
                memory.close_memory()

            except Exception as e:

                print(
                    "Memory close error:",
                    e
                )

            break

        # ====================================================
        # REMEMBER
        # ====================================================

        if command.startswith("remember"):

            information = user_input[
                len("remember"):
            ].strip()

            if information:

                try:

                    memory.save_memory(
                        information
                    )

                    messages.append(
                        {
                            "role": "user",
                            "content": user_input
                        }
                    )

                    messages.append(
                        {
                            "role": "assistant",
                            "content": "I'll remember that."
                        }
                    )

                    speak(
                        "I'll remember that."
                    )

                except Exception as e:

                    print(
                        "Memory error:",
                        e
                    )

                    speak(
                        "I couldn't save that memory."
                    )

            else:

                speak(
                    "What would you like me to remember?"
                )

            continue

        # ====================================================
        # DATE + TIME
        # ====================================================

        if (
            "date" in command
            and "time" in command
        ):

            current_datetime = tools.get_datetime()

            speak(
                f"It is {current_datetime}."
            )

            continue

        # ====================================================
        # DATE
        # ====================================================

        if "date" in command:

            today = tools.get_date()

            speak(
                f"Today is {today}."
            )

            continue

        # ====================================================
        # TIME
        # ====================================================

        if "time" in command:

            current_time = tools.get_time()

            speak(
                f"The current time is {current_time}."
            )

            continue

        # ====================================================
        # FIXED YOUTUBE COMMAND
        # ====================================================

        if (
            "open youtube" in command
            or "launch youtube" in command
        ):

            success = tools.open_youtube()

            if success:

                speak(
                    "YouTube is open."
                )

            else:

                speak(
                    "I couldn't open YouTube."
                )

            continue

        # ====================================================
        # FIXED GOOGLE COMMAND
        # ====================================================

        if (
            "open google" in command
            or "launch google" in command
        ):

            success = tools.open_google()

            if success:

                speak(
                    "Google is open."
                )

            else:

                speak(
                    "I couldn't open Google."
                )

            continue

        # ====================================================
        # FIXED DOWNLOADS COMMAND
        # ====================================================

        if (
            "open downloads" in command
            or "open my downloads" in command
            or "launch downloads" in command
        ):

            success = tools.open_downloads()

            if success:

                speak(
                    "Your Downloads folder is open."
                )

            else:

                speak(
                    "I couldn't open your Downloads folder."
                )

            continue

        # ====================================================
        # FIXED CHROME COMMAND
        # ====================================================

        if (
            "open chrome" in command
            or "launch chrome" in command
        ):

            success = tools.open_chrome()

            if success:

                speak(
                    "Chrome is open."
                )

            else:

                speak(
                    "I couldn't open Chrome."
                )

            continue

        # ====================================================
        # FIXED VS CODE COMMAND
        # ====================================================

        if (
            "open vs code" in command
            or "open vscode" in command
            or "launch vs code" in command
            or "launch vscode" in command
        ):

            success = tools.open_vscode()

            if success:

                speak(
                    "Visual Studio Code is open."
                )

            else:

                speak(
                    "I couldn't open Visual Studio Code."
                )

            continue

        # ====================================================
        # AI INTENT DETECTION
        # ====================================================

        intent = detect_intent(command)

        print(
            "DETECTED INTENT:",
            intent
        )

        # ====================================================
        # SMART APP COMMAND
        # ====================================================

        if intent.startswith(
            "OPEN_APP|"
        ):

            app_name = intent.split(
                "|",
                1
            )[1].strip()

            print(
                "DEBUG: SMART APP COMMAND DETECTED"
            )

            if app_name == "discord":

                success = tools.open_discord()

            elif app_name == "calculator":

                success = tools.open_calculator()

            elif app_name == "notepad":

                success = tools.open_notepad()

            elif app_name in [
                "vscode",
                "vs code"
            ]:

                success = tools.open_vscode()

            else:

                success = False

            if success:

                speak(
                    f"Opening {app_name}."
                )

            else:

                speak(
                    f"I couldn't open {app_name}."
                )

            continue

        # ====================================================
        # SMART FOLDER COMMAND
        # ====================================================

        if intent.startswith(
            "OPEN_FOLDER|"
        ):

            folder_name = intent.split(
                "|",
                1
            )[1].strip()

            print(
                "DEBUG: SMART FOLDER COMMAND DETECTED"
            )

            if folder_name in [
                "downloads",
                "download"
            ]:

                success = tools.open_downloads()

                if success:

                    speak(
                        "Your Downloads folder is open."
                    )

                else:

                    speak(
                        "I couldn't open your Downloads folder."
                    )

                continue

        # ====================================================
        # SMART WEBSITE COMMAND
        # ====================================================

        if intent.startswith(
            "OPEN_WEBSITE|"
        ):

            website_name = intent.split(
                "|",
                1
            )[1].strip()

            print(
                "DEBUG: SMART WEBSITE COMMAND DETECTED"
            )

            url = WEBSITE_MAP.get(
                website_name,
                website_name
            )

            success = tools.open_website(
                url
            )

            if success:

                speak(
                    f"Opening {website_name}."
                )

            else:

                speak(
                    f"I couldn't open {website_name}."
                )

            continue

        # ====================================================
        # NORMAL AI QUESTION
        # ====================================================

        print(
            "DEBUG: SENDING COMMAND TO OLLAMA"
        )

        messages.append(
            {
                "role": "user",
                "content": user_input
            }
        )

        try:

            response = ollama.chat(
                model=MODEL,
                messages=messages
            )

            reply = response[
                "message"
            ][
                "content"
            ]

            messages.append(
                {
                    "role": "assistant",
                    "content": reply
                }
            )

            speak(
                reply
            )

        except Exception as e:

            print(
                "AI error:",
                e
            )

            speak(
                "Sorry, I encountered an error while processing your request."
            )


# ============================================================
# START ONLY WHEN RUN DIRECTLY
# ============================================================

if __name__ == "__main__":
    run_spidey()