from pathlib import Path
import re
import shutil
import sys

ROOT = Path.cwd()

MAIN = ROOT / "main.py"
HUD = ROOT / "spidey_web" / "run_spidey_hud_native.py"

MAIN_BACKUP = ROOT / "main.py.before_python_bridge"
HUD_BACKUP = ROOT / "spidey_web" / "run_spidey_hud_native.py.before_python_bridge"

print("============================================")
print(" SPIDEY TYPED COMMAND BRIDGE")
print("============================================")

# ------------------------------------------------------------
# BACKUPS
# ------------------------------------------------------------

shutil.copy2(MAIN, MAIN_BACKUP)
shutil.copy2(HUD, HUD_BACKUP)

print("OK: Backups created.")

# ------------------------------------------------------------
# READ FILES
# ------------------------------------------------------------

main = MAIN.read_text(encoding="utf-8-sig")
hud = HUD.read_text(encoding="utf-8-sig")

# Normalize line endings for reliable editing.
main = main.replace("\r\n", "\n")
hud = hud.replace("\r\n", "\n")

# ------------------------------------------------------------
# 1. ADD TYPED COMMAND READER
# ------------------------------------------------------------

if "TYPED_COMMAND_FILE" not in main:

    marker = "def wait_for_space():"

    if marker not in main:
        raise RuntimeError(
            "Could not find wait_for_space()."
        )

    bridge = '''# ============================================================
# HUD TYPED COMMAND BRIDGE
# ============================================================

TYPED_COMMAND_FILE = os.path.join(
    os.path.dirname(
        os.path.abspath(__file__)
    ),
    "typed_command.txt"
)


def pop_typed_command():

    try:

        if not os.path.exists(
            TYPED_COMMAND_FILE
        ):
            return ""

        with open(
            TYPED_COMMAND_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            command = f.read().strip()

        try:
            os.remove(
                TYPED_COMMAND_FILE
            )
        except Exception:
            pass

        if command:

            print(
                "HUD -> REAL SPIDEY:",
                repr(command)
            )

        return command

    except Exception as e:

        print(
            "Typed command bridge error:",
            e
        )

        return ""


'''

    main = main.replace(
        marker,
        bridge + marker,
        1
    )

    print("OK: Typed command reader added.")

else:

    print("OK: Typed command reader already exists.")


# ------------------------------------------------------------
# 2. PATCH OUTER WAKE LISTENER
# ------------------------------------------------------------

wake_pattern = re.compile(
    r'(?m)^(\s*)user_input\s*=\s*listen_for_wake_word\(\s*WAKE_LISTEN_TIME\s*\)\s*$'
)

wake_matches = list(wake_pattern.finditer(main))

if len(wake_matches) != 1:

    raise RuntimeError(
        f"Expected 1 wake listener call, found {len(wake_matches)}."
    )

indent = wake_matches[0].group(1)

wake_replacement = f'''{indent}typed_command = pop_typed_command()

{indent}if typed_command:

{indent}    print(
{indent}        "SPIDEY: TYPED COMMAND RECEIVED:",
{indent}        repr(typed_command)
{indent}    )

{indent}    user_input = "hey spidey"

{indent}else:

{indent}    user_input = listen_for_wake_word(
{indent}        WAKE_LISTEN_TIME
{indent}    )'''

main = wake_pattern.sub(
    wake_replacement,
    main,
    count=1
)

print("OK: Wake listener patched.")


# ------------------------------------------------------------
# 3. PATCH COMMAND LISTENER
# ------------------------------------------------------------

command_pattern = re.compile(
    r'(?m)^(\s*)user_input\s*=\s*listen\(\s*COMMAND_LISTEN_TIME\s*\)\s*$'
)

command_matches = list(command_pattern.finditer(main))

if len(command_matches) != 1:

    raise RuntimeError(
        f"Expected 1 command listener call, found {len(command_matches)}."
    )

indent = command_matches[0].group(1)

command_replacement = f'''{indent}if typed_command:

{indent}    # Remove an optional typed wake phrase.
{indent}    typed_lower = typed_command.lower().strip()

{indent}    typed_wake_words = [
{indent}        "hey spidey",
{indent}        "hey spidy",
{indent}        "hi spidey",
{indent}        "hi spidy",
{indent}        "hey speedy",
{indent}        "hi speedy",
{indent}        "high speedy",
{indent}        "high speed",
{indent}        "hi spider",
{indent}        "spidey",
{indent}        "spidy"
{indent}    ]

{indent}    for wake_word in typed_wake_words:

{indent}        if typed_lower == wake_word:

{indent}            typed_command = ""
{indent}            break

{indent}        if typed_lower.startswith(
{indent}            wake_word + " "
{indent}        ):

{indent}            typed_command = typed_command[
{indent}                len(wake_word):
{indent}            ].strip()

{indent}            break

{indent}    user_input = typed_command

{indent}    print(
{indent}        "REAL SPIDEY TYPED COMMAND:",
{indent}        repr(user_input)
{indent}    )

{indent}    typed_command = ""

{indent}else:

{indent}    user_input = listen(
{indent}        COMMAND_LISTEN_TIME
{indent}    )'''

main = command_pattern.sub(
    command_replacement,
    main,
    count=1
)

print("OK: Command listener patched.")


# ------------------------------------------------------------
# 4. WRITE MAIN.PY
# ------------------------------------------------------------

MAIN.write_text(
    main,
    encoding="utf-8"
)

print("OK: main.py saved.")


# ------------------------------------------------------------
# 5. PATCH HUD SERVER
# ------------------------------------------------------------

if "typed_command.txt" not in hud:

    hud_pattern = re.compile(
        r'''(?s)else:\s*
            success\s*=\s*True\s*
            message\s*=\s*\(\s*
            "Command received: "\s*\+\s*command\s*
            \)'''
        ,
        re.VERBOSE
    )

    hud_matches = list(
        hud_pattern.finditer(hud)
    )

    if len(hud_matches) != 1:

        raise RuntimeError(
            f"Could not uniquely find HUD fallback. "
            f"Found {len(hud_matches)} matches."
        )

    hud_replacement = '''else:

                try:

                    command_file = (
                        PROJECT_ROOT /
                        "typed_command.txt"
                    )

                    command_file.write_text(
                        command,
                        encoding="utf-8"
                    )

                    print(
                        "HUD -> SPIDEY:",
                        repr(command)
                    )

                    success = True

                    message = (
                        "Command sent to SPIDEY."
                    )

                except Exception as e:

                    print(
                        "HUD command error:",
                        e
                    )

                    success = False

                    message = (
                        "Could not send command to SPIDEY."
                    )'''

    hud = hud_pattern.sub(
        hud_replacement,
        hud,
        count=1
    )

    HUD.write_text(
        hud,
        encoding="utf-8"
    )

    print("OK: HUD server patched.")

else:

    print("OK: HUD server bridge already exists.")


# ------------------------------------------------------------
# 6. SYNTAX CHECK
# ------------------------------------------------------------

import py_compile

print("")
print("Checking main.py...")

py_compile.compile(
    str(MAIN),
    doraise=True
)

print("main.py syntax: OK")

print("")
print("Checking HUD server...")

py_compile.compile(
    str(HUD),
    doraise=True
)

print("HUD server syntax: OK")


# ------------------------------------------------------------
# 7. FINAL VERIFICATION
# ------------------------------------------------------------

main_check = MAIN.read_text(
    encoding="utf-8-sig"
)

hud_check = HUD.read_text(
    encoding="utf-8-sig"
)

required_main = [
    "TYPED_COMMAND_FILE",
    "pop_typed_command",
    "TYPED COMMAND RECEIVED",
    "REAL SPIDEY TYPED COMMAND",
]

required_hud = [
    "typed_command.txt",
    "HUD -> SPIDEY",
    "Command sent to SPIDEY",
]

for item in required_main:

    if item not in main_check:
        raise RuntimeError(
            f"Verification failed in main.py: {item}"
        )

for item in required_hud:

    if item not in hud_check:
        raise RuntimeError(
            f"Verification failed in HUD: {item}"
        )

print("")
print("============================================")
print(" TEXT COMMAND BRIDGE INSTALLED SUCCESSFULLY")
print("============================================")
print("")
print("main.py: OK")
print("HUD server: OK")
print("Bridge verification: OK")
print("")
print("DO NOT START SPIDEY YET.")

