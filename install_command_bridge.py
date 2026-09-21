from pathlib import Path
import shutil
import py_compile

ROOT = Path.cwd()

MAIN = ROOT / "main.py"
HUD = ROOT / "spidey_web" / "run_spidey_hud_native.py"

MAIN_BACKUP = ROOT / "main.py.before_command_bridge"
HUD_BACKUP = ROOT / "spidey_web" / "run_spidey_hud_native.py.before_command_bridge"

# ------------------------------------------------------------
# BACKUPS
# ------------------------------------------------------------

shutil.copy2(MAIN, MAIN_BACKUP)
shutil.copy2(HUD, HUD_BACKUP)

print("Backups created.")

# ------------------------------------------------------------
# MAIN.PY
# ------------------------------------------------------------

main = MAIN.read_text(encoding="utf-8-sig")
main = main.replace("\r\n", "\n")

if "TYPED_COMMAND_FILE" not in main:

    marker = "def wait_for_space():"

    if marker not in main:
        raise RuntimeError("wait_for_space() not found.")

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

    print("OK: main bridge added.")

else:

    print("OK: main bridge already exists.")


# ------------------------------------------------------------
# PATCH THE WAKE LISTENER
# ------------------------------------------------------------

wake_old = "        user_input = listen_for_wake_word(WAKE_LISTEN_TIME)"

if wake_old not in main:
    raise RuntimeError(
        "Could not find the exact wake listener line."
    )

wake_new = '''        typed_command = pop_typed_command()

        if typed_command:

            print(
                "SPIDEY: TYPED COMMAND RECEIVED:",
                repr(typed_command)
            )

            user_input = "hey spidey"

        else:

            user_input = listen_for_wake_word(
                WAKE_LISTEN_TIME
            )'''

main = main.replace(
    wake_old,
    wake_new,
    1
)

print("OK: wake listener connected.")


# ------------------------------------------------------------
# PATCH THE COMMAND LISTENER
# ------------------------------------------------------------

command_old = '''            user_input = listen(
                COMMAND_LISTEN_TIME
            )'''

if command_old not in main:
    raise RuntimeError(
        "Could not find command listener block."
    )

command_new = '''            if typed_command:

                user_input = typed_command

                print(
                    "REAL SPIDEY TYPED COMMAND:",
                    repr(user_input)
                )

                typed_command = ""

            else:

                user_input = listen(
                    COMMAND_LISTEN_TIME
                )'''

main = main.replace(
    command_old,
    command_new,
    1
)

print("OK: command listener connected.")

MAIN.write_text(
    main,
    encoding="utf-8"
)

print("OK: main.py saved.")


# ------------------------------------------------------------
# HUD SERVER
# ------------------------------------------------------------

hud = HUD.read_text(encoding="utf-8-sig")
hud = hud.replace("\r\n", "\n")

if "typed_command.txt" not in hud:

    # We insert the command endpoint immediately before
    # the end of do_POST(), identified by the transition
    # from the handler method to the next class-level method
    # or top-level section.

    # Find the /api/chup section.
    chup_marker = 'if request_path == "/api/chup":'

    chup_start = hud.find(chup_marker)

    if chup_start < 0:
        raise RuntimeError(
            "Could not find /api/chup in HUD server."
        )

    # Find the next method definition after /api/chup.
    # This marks the end of the POST handler.
    next_method = hud.find(
        "\n    def ",
        chup_start + len(chup_marker)
    )

    if next_method < 0:

        # If there is no next method, find the server/main
        # section after the handler.
        candidates = [
            hud.find("\n# ============================================================", chup_start + 1),
            hud.find("\ndef start_server(", chup_start + 1),
            hud.find("\ndef main(", chup_start + 1),
        ]

        candidates = [
            x for x in candidates
            if x >= 0
        ]

        if not candidates:
            raise RuntimeError(
                "Could not determine end of do_POST()."
            )

        insertion_point = min(candidates)

    else:

        insertion_point = next_method

    command_endpoint = '''

        # ====================================================
        # TYPED COMMAND
        # ====================================================

        if request_path == "/api/command":

            try:

                length = int(
                    self.headers.get(
                        "Content-Length",
                        "0"
                    )
                )

                body = self.rfile.read(
                    length
                )

                payload = json.loads(
                    body.decode(
                        "utf-8"
                    )
                )

                command = (
                    payload.get(
                        "command",
                        ""
                    )
                    or
                    ""
                ).strip()

                if not command:

                    response = {
                        "success": False,
                        "message": "Command is empty."
                    }

                    self.send_json(
                        response
                    )

                    return

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

                response = {
                    "success": True,
                    "message": "Command sent to SPIDEY."
                }

            except Exception as e:

                print(
                    "HUD COMMAND ERROR:",
                    e
                )

                response = {
                    "success": False,
                    "message": str(e)
                }

            self.send_json(
                response
            )

            return

'''

    hud = (
        hud[:insertion_point]
        +
        command_endpoint
        +
        hud[insertion_point:]
    )

    HUD.write_text(
        hud,
        encoding="utf-8"
    )

    print("OK: /api/command endpoint added.")

else:

    print("OK: HUD command bridge already exists.")


# ------------------------------------------------------------
# SYNTAX CHECK
# ------------------------------------------------------------

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
# VERIFY
# ------------------------------------------------------------

main_check = MAIN.read_text(
    encoding="utf-8-sig"
)

hud_check = HUD.read_text(
    encoding="utf-8-sig"
)

checks = [
    ("main.py", "TYPED_COMMAND_FILE", main_check),
    ("main.py", "pop_typed_command", main_check),
    ("main.py", "TYPED COMMAND RECEIVED", main_check),
    ("main.py", "REAL SPIDEY TYPED COMMAND", main_check),
    ("HUD", '/api/command', hud_check),
    ("HUD", 'typed_command.txt', hud_check),
]

for location, text, content in checks:

    if text not in content:

        raise RuntimeError(
            f"Verification failed: {location} missing {text}"
        )

print("")
print("============================================")
print(" SPIDEY TEXT COMMAND BRIDGE READY")
print("============================================")
print("")
print("main.py: OK")
print("HUD /api/command: OK")
print("Syntax: OK")
print("Verification: OK")
print("")
print("DO NOT START SPIDEY YET.")
