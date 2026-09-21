from datetime import datetime
import subprocess
import os
import webbrowser


# ============================================================
# DATE & TIME
# ============================================================

def get_date():
    """
    Return the current date.
    """

    return datetime.now().strftime(
        "%A, %B %d, %Y"
    )


def get_time():
    """
    Return the current time.
    """

    return datetime.now().strftime(
        "%I:%M:%S %p"
    )


def get_datetime():
    """
    Return the current date and time.
    """

    return datetime.now().strftime(
        "%A, %B %d, %Y at %I:%M:%S %p"
    )


# ============================================================
# WEBSITES
# ============================================================

def open_youtube():
    """
    Open YouTube in the default browser
    and bring the browser window to the front.
    """

    try:

        url = "https://www.youtube.com"

        # Open using the user's default browser.
        webbrowser.open_new_tab(url)

        # Give the browser time to load/create the window.
        import time
        time.sleep(1.0)

        # Bring the browser window containing YouTube
        # to the foreground.
        focus_script = r"""
Add-Type -AssemblyName Microsoft.VisualBasic

$processes = Get-Process |
    Where-Object {
        ($_.ProcessName -eq "msedge" -or
         $_.ProcessName -eq "chrome" -or
         $_.ProcessName -eq "firefox") -and
        $_.MainWindowHandle -ne 0
    }

$youtube = $processes |
    Where-Object {
        $_.MainWindowTitle -match "YouTube"
    } |
    Select-Object -First 1

if ($youtube) {
    [Microsoft.VisualBasic.Interaction]::AppActivate(
        $youtube.Id
    )
}
else {
    $browser = $processes |
        Select-Object -First 1

    if ($browser) {
        [Microsoft.VisualBasic.Interaction]::AppActivate(
            $browser.Id
        )
    }
}
"""

        subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-WindowStyle",
                "Hidden",
                "-Command",
                focus_script
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False
        )

        return True

    except Exception as e:

        print(
            "YouTube error:",
            e
        )

        return False

def open_google():
    """
    Open Google in the default browser.
    """

    try:

        webbrowser.open_new_tab(
            "https://www.google.com"
        )

        return True

    except Exception as e:

        print(
            "Google error:",
            e
        )

        return False


# ============================================================
# WINDOWS APPS
# ============================================================

def open_chrome():
    """
    Open Google Chrome.
    """

    chrome_paths = [

        r"C:\Program Files\Google\Chrome\Application\chrome.exe",

        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",

        os.path.expandvars(
            r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"
        )
    ]


    for chrome_path in chrome_paths:

        if os.path.exists(chrome_path):

            try:

                subprocess.Popen(
                    [chrome_path]
                )

                return True

            except Exception as e:

                print(
                    "Chrome error:",
                    e
                )

                return False


    print(
        "Chrome executable was not found."
    )

    return False


def open_vscode():
    """
    Open Visual Studio Code.
    """

    vscode_paths = [

        os.path.expandvars(
            r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe"
        ),

        r"C:\Program Files\Microsoft VS Code\Code.exe",

        r"C:\Program Files (x86)\Microsoft VS Code\Code.exe"
    ]


    for vscode_path in vscode_paths:

        if os.path.exists(vscode_path):

            try:

                subprocess.Popen(
                    [vscode_path]
                )

                return True

            except Exception as e:

                print(
                    "VS Code error:",
                    e
                )

                return False


    print(
        "VS Code executable was not found."
    )

    return False


# ============================================================
# FOLDERS
# ============================================================

def open_downloads():
    """
    Open the user's Downloads folder.
    """

    try:

        downloads = os.path.join(
            os.path.expanduser("~"),
            "Downloads"
        )

        if not os.path.exists(downloads):

            print(
                "Downloads folder not found."
            )

            return False


        os.startfile(downloads)

        return True

    except Exception as e:

        print(
            "Downloads error:",
            e
        )

        return False
    # ============================================================
# GENERIC WEBSITE OPENER
# ============================================================
def open_website(url):
    try:
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        webbrowser.open_new_tab(url)
        return True

    except Exception as e:
        print("Website error:", e)
        return False
def open_discord():
    try:
        discord_paths = [
            os.path.expandvars(
                r"%LOCALAPPDATA%\Discord\Update.exe"
            ),
            os.path.expandvars(
                r"%APPDATA%\Discord\Update.exe"
            )
        ]

        for path in discord_paths:

            if os.path.exists(path):

                subprocess.Popen(
                    [
                        path,
                        "--processStart",
                        "Discord.exe"
                    ]
                )

                return True

        print("Discord executable was not found.")
        return False

    except Exception as e:

        print(
            "Discord error:",
            e
        )

        return False

def open_calculator():
    try:
        subprocess.Popen(
            "calc.exe"
        )
        return True
    except Exception as e:
        print("Calculator error:", e)
        return False


def open_notepad():
    try:
        subprocess.Popen(
            "notepad.exe"
        )
        return True
    except Exception as e:
        print("Notepad error:", e)
        return False
    # ============================================================

# ============================================================
# COMPUTER CONTROLS
# ============================================================

def take_screenshot():
    """Take a screenshot and save it to the user's Pictures folder."""
    try:
        import pyautogui
        pictures = os.path.join(os.path.expanduser("~"), "Pictures")
        os.makedirs(pictures, exist_ok=True)
        filename = os.path.join(
            pictures,
            "spidey_screenshot_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".png"
        )
        pyautogui.screenshot(filename)
        print("Screenshot saved:", filename)
        return True
    except Exception as e:
        print("Screenshot error:", e)
        return False


def volume_up():
    """Increase system volume."""
    try:
        import pyautogui
        for _ in range(5):
            pyautogui.press("volumeup")
        return True
    except Exception as e:
        print("Volume up error:", e)
        return False


def volume_down():
    """Decrease system volume."""
    try:
        import pyautogui
        for _ in range(5):
            pyautogui.press("volumedown")
        return True
    except Exception as e:
        print("Volume down error:", e)
        return False


def volume_mute():
    """Toggle system mute."""
    try:
        import pyautogui
        pyautogui.press("volumemute")
        return True
    except Exception as e:
        print("Mute error:", e)
        return False


def media_play_pause():
    """Play or pause the currently active media player."""
    try:
        import pyautogui
        pyautogui.press("playpause")
        return True
    except Exception as e:
        print("Media control error:", e)
        return False


def minimize_window():
    """Minimize the currently active window."""
    try:
        import pyautogui
        pyautogui.hotkey("win", "down")
        return True
    except Exception as e:
        print("Minimize error:", e)
        return False


def maximize_window():
    """Maximize the currently active window."""
    try:
        import pyautogui
        pyautogui.hotkey("win", "up")
        return True
    except Exception as e:
        print("Maximize error:", e)
        return False


def close_current_window():
    """Close the currently active window."""
    try:
        import pyautogui
        pyautogui.hotkey("alt", "f4")
        return True
    except Exception as e:
        print("Close window error:", e)
        return False


def refresh_window():
    """Refresh the currently active window."""
    try:
        import pyautogui
        pyautogui.press("f5")
        return True
    except Exception as e:
        print("Refresh error:", e)
        return False


def switch_window():
    """Switch to the next open Windows application."""
    try:
        import pyautogui
        pyautogui.hotkey("alt", "tab")
        return True
    except Exception as e:
        print("Window switch error:", e)
        return False


def lock_pc():
    """Lock Windows."""
    try:
        subprocess.run(
            ["rundll32.exe", "user32.dll,LockWorkStation"],
            check=False
        )
        return True
    except Exception as e:
        print("Lock PC error:", e)
        return False
    # ============================================================
# SPOTIFY
# ============================================================

def search_spotify(song):
    """Open a Spotify search for a song."""
    try:
        from urllib.parse import quote

        song = song.strip()

        if not song:
            return False

        url = (
            "https://open.spotify.com/search/"
            + quote(song)
        )

        webbrowser.open_new_tab(url)

        print(
            "Spotify search opened:",
            song
        )

        return True

    except Exception as e:
        print(
            "Spotify search error:",
            e
        )
        return False
