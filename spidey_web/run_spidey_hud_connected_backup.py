import http.server
import socketserver
import webbrowser
import sys
import json
from pathlib import Path


# ============================================================
# SPIDEY WEB HUD + PYTHON BRIDGE
# ============================================================

PORT = 8765

ROOT = Path(__file__).parent
PROJECT_ROOT = ROOT.parent

# Allow Python to find main.py
sys.path.insert(0, str(PROJECT_ROOT))

import main


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
    # POST REQUEST
    # ========================================================

    def do_POST(self):

        if self.path != "/api/command":

            self.send_error(404)

            return


        # ----------------------------------------------------
        # READ REQUEST
        # ----------------------------------------------------

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


            # ------------------------------------------------
            # YOUTUBE
            # ------------------------------------------------

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

                if success:

                    message = (
                        "YouTube is open."
                    )

                else:

                    message = (
                        "I couldn't open YouTube."
                    )


            # ------------------------------------------------
            # GOOGLE
            # ------------------------------------------------

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

                if success:

                    message = (
                        "Google is open."
                    )

                else:

                    message = (
                        "I couldn't open Google."
                    )


            # ------------------------------------------------
            # DISCORD
            # ------------------------------------------------

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

                if success:

                    message = (
                        "Discord is open."
                    )

                else:

                    message = (
                        "I couldn't open Discord."
                    )


            # ------------------------------------------------
            # CALCULATOR
            # ------------------------------------------------

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

                if success:

                    message = (
                        "Calculator is open."
                    )

                else:

                    message = (
                        "I couldn't open Calculator."
                    )


            # ------------------------------------------------
            # VS CODE
            # ------------------------------------------------

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

                if success:

                    message = (
                        "VS Code is open."
                    )

                else:

                    message = (
                        "I couldn't open VS Code."
                    )


            # ------------------------------------------------
            # DOWNLOADS
            # ------------------------------------------------

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

                if success:

                    message = (
                        "Downloads folder "
                        "is open."
                    )

                else:

                    message = (
                        "I couldn't open "
                        "Downloads."
                    )


            # ------------------------------------------------
            # UNKNOWN COMMAND
            # ------------------------------------------------

            else:

                success = True

                message = (
                    "Command received: "
                    + command
                )


            # ------------------------------------------------
            # RESPONSE
            # ------------------------------------------------

            response = {

                "success":
                    success,

                "message":
                    message
            }


        except Exception as e:

            print()
            print(
                "COMMAND ERROR:",
                e
            )

            response = {

                "success":
                    False,

                "message":
                    str(e)
            }


        # ====================================================
        # SEND RESPONSE TO BROWSER
        # ====================================================

        data = json.dumps(
            response
        ).encode("utf-8")


        self.send_response(
            200
        )

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

        self.send_response(
            200
        )

        self.send_header(
            "Access-Control-Allow-Origin",
            "*"
        )

        self.send_header(
            "Access-Control-Allow-Methods",
            "POST, OPTIONS"
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