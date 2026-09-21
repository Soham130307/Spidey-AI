from pathlib import Path
import shutil

ROOT = Path.cwd()
TOOLS = ROOT / "tools.py"
MAIN = ROOT / "main.py"

print("SPIDEY YouTube Search V1 installer")
print("=" * 40)

if not TOOLS.exists():
    raise SystemExit("ERROR: tools.py not found. Run this from C:\\Users\\Soham\\Desktop\\Spidy Ai")

if not MAIN.exists():
    raise SystemExit("ERROR: main.py not found. Run this from C:\\Users\\Soham\\Desktop\\Spidy Ai")

tools_backup = ROOT / "tools_before_youtube_v1.py"
main_backup = ROOT / "main_before_youtube_v1.py"

shutil.copy2(TOOLS, tools_backup)
shutil.copy2(MAIN, main_backup)

print(f"Backup created: {tools_backup.name}")
print(f"Backup created: {main_backup.name}")

# PATCH tools.py
tools_text = TOOLS.read_text(encoding="utf-8")

if "def search_youtube(" not in tools_text:
    marker = "\n# ============================================================\n# WINDOWS APPS\n# ============================================================\n"

    if marker not in tools_text:
        raise SystemExit("ERROR: tools.py marker not found. NO CHANGES MADE.")

    youtube_function = '''
# ============================================================
# YOUTUBE SEARCH
# ============================================================

def search_youtube(query):
    \"\"
    Search YouTube directly in the default browser.
    Returns True on successful browser launch.
    \"\"

    try:
        from urllib.parse import quote_plus

        query = (query or "").strip()

        if not query:
            return False

        search_url = (
            "https://www.youtube.com/results?search_query="
            + quote_plus(query)
        )

        webbrowser.open_new_tab(search_url)

        return True

    except Exception as e:

        print(
            "YouTube search error:",
            e
        )

        return False

'''
    tools_text = tools_text.replace(marker, youtube_function + marker, 1)
    TOOLS.write_text(tools_text, encoding="utf-8")
    print("OK: Added search_youtube() to tools.py")
else:
    print("OK: search_youtube() already exists")

# PATCH main.py
main_text = MAIN.read_text(encoding="utf-8")

if "DEBUG: YOUTUBE SEARCH COMMAND DETECTED" not in main_text:

    marker = "            # FAST SEARCH\n"

    if marker not in main_text:
        marker = "            # -------------------------------------------------\n            # FAST SEARCH\n"

    if marker not in main_text:
        raise SystemExit("ERROR: FAST SEARCH marker not found in main.py. NO MAIN.PY CHANGES MADE.")

    youtube_block = '''
            # -------------------------------------------------
            # FAST YOUTUBE SEARCH
            # -------------------------------------------------
            # Examples:
            #   search youtube for python
            #   search youtube python tutorial
            #   youtube search python
            #   find on youtube gym workout
            #   play youtube <query>
            #
            # This runs BEFORE Google search and BEFORE Ollama.
            # -------------------------------------------------

            youtube_search_match = re.match(
                r"^(?:search youtube(?: for)?|youtube search|find on youtube|play youtube)\\s+(.+)$",
                command,
                re.IGNORECASE
            )

            if youtube_search_match:

                youtube_query = (
                    youtube_search_match.group(1)
                    .strip()
                    .rstrip(".,!?")
                )

                if youtube_query:

                    print(
                        "DEBUG: YOUTUBE SEARCH COMMAND DETECTED"
                    )

                    update_hud(
                        "THINKING",
                        f"Searching YouTube for: {youtube_query}"
                    )

                    success = tools.search_youtube(
                        youtube_query
                    )

                    if success:

                        speak(
                            f"Searching YouTube for {youtube_query}."
                        )

                    else:

                        speak(
                            "I couldn't open the YouTube search."
                        )

                    update_hud(
                        "LISTENING",
                        "Listening for your command..."
                    )

                continue

'''

    main_text = main_text.replace(marker, youtube_block + marker, 1)
    MAIN.write_text(main_text, encoding="utf-8")
    print("OK: Added YouTube search routing to main.py")
else:
    print("OK: YouTube search routing already exists")

print()
print("Installation complete.")
print("Backups are preserved.")
print()
print("Test commands:")
print('  "Hey Spidey, search YouTube for Python tutorials"')
print('  "Hey Spidey, search YouTube for GTA 5 gameplay"')
print('  "Hey Spidey, find on YouTube gym workout"')
