import http.server
import socketserver
import webbrowser
import sys
import json
from pathlib import Path
from urllib.parse import urlparse


# ============================================================
# SPIDEY WEB HUD + PYTHON BRIDGE
# ============================================================

PORT = 8765

ROOT = Path(__file__).parent
PROJECT_ROOT = ROOT.parent

sys.path.insert(0, str(PROJECT_ROOT))

import main


# ============================================================
# CURRENT HUD STATE
# ============================================================

last_hud_state = "STANDBY"


# ============================================================
# REQUEST HANDLER
# ============================================================

class SpideyHandler(
    http.server.SimpleHTTPRequestHandler
):

    def __init__(
        self,
        *args,
        **kwargs
    ):

        super().__init__(
            *args,
            directory=str(ROOT),
            **kwargs
        )


    # ========================================================
    # GET REQUESTS
    # ========================================================

    def do_GET(self):

        request_path = urlparse(self.path).path

        # ----------------------------------------------------
        # BROWSER REQUESTS CURRENT HUD STATE
        # ----------------------------------------------------

        if request_path == "/api/state":

            response = {
                "success": True,
                "state": last_hud_state
            }

            data = json.dumps(
                response
            ).encode("utf-8")

            self.send_response(200)

            self.send_header(
                "Content-Type",
                "application/json"
            )

            self.send_header(
                "Content-Length",
                str(len(data))
            )

            self.send_header(
                "Access-Control-Allow-Origin",
                "*"
            )

            self.end_headers()

            self.wfile.write(data)

            return


        # ----------------------------------------------------
        # NORMAL WEBSITE FILES
        # ----------------------------------------------------

        super().do_GET()


    # ========================================================
    # POST REQUESTS
    # ========================================================

    def do_POST(self):

        global last_hud_state

        request_path = urlparse(self.path).path


        # ====================================================
        # HUD STATE UPDATE
        # ====================================================

        # ====================================================
        # CHUP — STOP SPEECH IN MAIN.PY
        # ====================================================

        if request_path == "/api/chup":

            try:

                chup_file = (
                    PROJECT_ROOT /
                    "chup.flag"
                )

                chup_file.touch(
                    exist_ok=True
                )

                print(
                    "HUD CHUP: STOP SIGNAL SENT"
                )

                response = {
                    "success": True,
                    "message":
                        "CHUP signal sent."
                }

            except Exception as e:

                print(
                    "HUD CHUP ERROR:",
                    e
                )

                response = {
                    "success": False,
                    "message":
                        str(e)
                }

            result = json.dumps(
                response
            ).encode("utf-8")

            self.send_response(200)

            self.send_header(
                "Content-Type",
                "application/json"
            )

            self.send_header(
                "Content-Length",
                str(len(result))
            )

            self.send_header(
                "Access-Control-Allow-Origin",
                "*"
            )

            self.end_headers()

            self.wfile.write(result)

            return


        # ====================================================
        # HUD STATE UPDATE
        # ====================================================

        if request_path == "/api/state":

            length = int(
                self.headers.get(
                    "Content-Length",
                    0
                )
            )

            body = (
                self.rfile
                .read(length)
                .decode("utf-8")
            )

            try:

                data = json.loads(
                    body
                )

                hud_state = data.get(
                    "state",
                    "READY"
                )

                last_hud_state = hud_state

                print(
                    "HUD STATE:",
                    hud_state
                )

                response = {
                    "success": True,
                    "state": hud_state
                }

            except Exception as e:

                response = {
                    "success": False,
                    "message": str(e)
                }

            result = json.dumps(
                response
            ).encode("utf-8")

            self.send_response(200)

            self.send_header(
                "Content-Type",
                "application/json"
            )

            self.send_header(
                "Content-Length",
                str(len(result))
            )

            self.send_header(
                "Access-Control-Allow-Origin",
                "*"
            )

            self.end_headers()

            self.wfile.write(
                result
            )

            return


        # ====================================================
        # COMMAND
        # ====================================================

        if request_path != "/api/command":

            self.send_error(404)

            return


        length = int(
            self.headers.get(
                "Content-Length",
                0
            )
        )

        body = (
            self.rfile
            .read(length)
            .decode("utf-8")
        )

        print()
        print(
            "HUD COMMAND:",
            body
        )


        # ====================================================
        # PROCESS COMMAND
        # ====================================================

        try:

            request_data = json.loads(
                body
            )

            command = (
                request_data
                .get(
                    "command",
                    ""
                )
                .strip()
            )

            command_lower = (
                command.lower()
            )


            success = False

            message = (
                "I couldn't understand "
                "that command."
            )


            if (
                "open youtube"
                in command_lower
                or
                "launch youtube"
                in command_lower
            ):

                success = (
                    main.tools.open_youtube()
                )

                message = (
                    "YouTube is open."
                    if success
                    else
                    "I couldn't open YouTube."
                )


            elif (
                "open google"
                in command_lower
                or
                "launch google"
                in command_lower
            ):

                success = (
                    main.tools.open_google()
                )

                message = (
                    "Google is open."
                    if success
                    else
                    "I couldn't open Google."
                )


            elif (
                "open discord"
                in command_lower
                or
                "launch discord"
                in command_lower
            ):

                success = (
                    main.tools.open_discord()
                )

                message = (
                    "Discord is open."
                    if success
                    else
                    "I couldn't open Discord."
                )


            elif (
                "open calculator"
                in command_lower
                or
                "launch calculator"
                in command_lower
            ):

                success = (
                    main.tools.open_calculator()
                )

                message = (
                    "Calculator is open."
                    if success
                    else
                    "I couldn't open Calculator."
                )


            elif (
                "open vs code"
                in command_lower
                or
                "open vscode"
                in command_lower
                or
                "launch vs code"
                in command_lower
                or
                "launch vscode"
                in command_lower
            ):

                success = (
                    main.tools.open_vscode()
                )

                message = (
                    "VS Code is open."
                    if success
                    else
                    "I couldn't open VS Code."
                )


            elif (
                "open downloads"
                in command_lower
                or
                "open my downloads"
                in command_lower
                or
                "launch downloads"
                in command_lower
            ):

                success = (
                    main.tools.open_downloads()
                )

                message = (
                    "Downloads folder is open."
                    if success
                    else
                    "I couldn't open Downloads."
                )


            else:

                success = True

                message = (
                    "Command received: "
                    + command
                )


            response = {
                "success": success,
                "message": message
            }


        except Exception as e:

            print(
                "COMMAND ERROR:",
                e
            )

            response = {
                "success": False,
                "message": str(e)
            }


        # ====================================================
        # SEND RESPONSE
        # ====================================================

        data = json.dumps(
            response
        ).encode("utf-8")

        self.send_response(200)

        self.send_header(
            "Content-Type",
            "application/json"
        )

        self.send_header(
            "Content-Length",
            str(len(data))
        )

        self.send_header(
            "Access-Control-Allow-Origin",
            "*"
        )

        self.end_headers()

        self.wfile.write(
            data
        )


    # ========================================================
    # OPTIONS
    # ========================================================

    def do_OPTIONS(self):

        self.send_response(200)

        self.send_header(
            "Access-Control-Allow-Origin",
            "*"
        )

        self.send_header(
            "Access-Control-Allow-Methods",
            "POST, GET, OPTIONS"
        )

        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type"
        )

        self.end_headers()


# ============================================================
# START SERVER
# ============================================================

print()

print(
    "=" * 50
)

print(
    "        SPIDEY HUD"
)

print(
    "=" * 50
)

print()

print(
    "Starting interface..."
)

print()


with socketserver.ThreadingTCPServer(
    ("127.0.0.1", PORT),
    SpideyHandler
) as server:

    url = (
        f"http://127.0.0.1:"
        f"{PORT}/index.html"
    )

    print(
        "SPIDEY HUD running at:"
    )

    print(
        url
    )

    print()

    print(
        "Python bridge: CONNECTED"
    )

    print()

    print(
        "Opening interface..."
    )

    webbrowser.open(
        url
    )

    print()

    print(
        "Press CTRL+C to stop "
        "SPIDEY HUD."
    )

    print()


    try:

        server.serve_forever()

    except KeyboardInterrupt:

        print()

        print(
            "SPIDEY HUD stopped."
        )