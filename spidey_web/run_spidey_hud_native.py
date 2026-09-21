import http.server
import socketserver
import threading
import json
from pathlib import Path
from urllib.parse import urlparse

try:
    import webview

except ImportError:

    print()
    print("SPIDEY ERROR: pywebview is not installed.")
    print("Run:")
    print("    pip install pywebview")
    print()

    raise


# ============================================================
# SPIDEY NATIVE HUD HOST
# ============================================================
#
# This server:
#
# 1. Serves the existing SPIDEY web HUD
# 2. Connects the HTML/JS HUD to main.py
# 3. Sends state to the frontend
# 4. Sends user commands to the frontend
# 5. Sends SPIDEY responses to the frontend
# 6. Provides the CHUP stop endpoint
#
# ============================================================


PORT = 8765


# ------------------------------------------------------------
# PATHS
# ------------------------------------------------------------

ROOT = Path(__file__).resolve().parent

PROJECT_ROOT = ROOT.parent

HUD_ROOT = ROOT


# ============================================================
# SHARED HUD STATE
# ============================================================

last_hud_state = "STANDBY"

last_user_command = ""

last_spidey_message = ""


# ============================================================
# REQUEST HANDLER
# ============================================================

class SpideyHandler(
    http.server.SimpleHTTPRequestHandler
):


    # ========================================================
    # INITIALIZER
    # ========================================================

    def __init__(
        self,
        *args,
        **kwargs
    ):

        super().__init__(
            *args,
            directory=str(HUD_ROOT),
            **kwargs
        )


    # ========================================================
    # TERMINAL LOG
    # ========================================================

    def log_message(
        self,
        format,
        *args
    ):

        # Keep terminal clean.
        pass


    # ========================================================
    # GET
    # ========================================================

    def do_GET(self):

        global last_hud_state
        global last_user_command
        global last_spidey_message


        request_path = urlparse(
            self.path
        ).path


        # ====================================================
        # HUD STATE API
        # ====================================================

        if request_path == "/api/state":

            response = {

                "success":
                    True,

                "state":
                    last_hud_state,

                "user_command":
                    last_user_command,

                "spidey_message":
                    last_spidey_message
            }


            data = json.dumps(
                response
            ).encode(
                "utf-8"
            )


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
                "Cache-Control",
                "no-store"
            )


            self.send_header(
                "Access-Control-Allow-Origin",
                "*"
            )


            self.end_headers()


            self.wfile.write(
                data
            )


            return


        # ====================================================
        # NORMAL HUD FILES
        # ====================================================

        super().do_GET()


    # ========================================================
    # POST
    # ========================================================

    def do_POST(self):

        global last_hud_state
        global last_user_command
        global last_spidey_message


        request_path = urlparse(
            self.path
        ).path


        # ====================================================
        # HUD STATE UPDATE
        # ====================================================

        if request_path == "/api/state":

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


                # ------------------------------------------------
                # STATE
                # ------------------------------------------------

                last_hud_state = payload.get(
                    "state",
                    "STANDBY"
                )


                # ------------------------------------------------
                # USER COMMAND
                # ------------------------------------------------

                if (
                    "user_command"
                    in payload
                ):

                    last_user_command = (
                        payload.get(
                            "user_command"
                        )
                        or
                        ""
                    )


                # ------------------------------------------------
                # SPIDEY MESSAGE
                # ------------------------------------------------

                if (
                    "spidey_message"
                    in payload
                ):

                    last_spidey_message = (
                        payload.get(
                            "spidey_message"
                        )
                        or
                        ""
                    )


                print(
                    "HUD STATE:",
                    last_hud_state
                )


                if last_user_command:

                    print(
                        "USER:",
                        last_user_command
                    )


                if last_spidey_message:

                    print(
                        "SPIDEY:",
                        last_spidey_message
                    )


                response = {

                    "success":
                        True,

                    "state":
                        last_hud_state,

                    "user_command":
                        last_user_command,

                    "spidey_message":
                        last_spidey_message
                }


            except Exception as e:

                print(
                    "HUD STATE ERROR:",
                    e
                )


                response = {

                    "success":
                        False,

                    "message":
                        str(e)
                }


            self.send_json(
                response
            )


            return


        # ====================================================
        # CHUP
        # ====================================================

        if request_path == "/api/chup":

            try:

                # --------------------------------------------
                # main.py watches this file.
                # --------------------------------------------

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

                    "success":
                        True,

                    "message":
                        "CHUP signal sent."
                }


            except Exception as e:

                print(
                    "HUD CHUP ERROR:",
                    e
                )


                response = {

                    "success":
                        False,

                    "message":
                        str(e)
                }


            self.send_json(
                response
            )


            return


        # ====================================================
        # UNKNOWN POST
        # ====================================================

        self.send_error(
            404
        )


    # ========================================================
    # JSON RESPONSE
    # ========================================================


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


    def send_json(
        self,
        response
    ):

        data = json.dumps(
            response
        ).encode(
            "utf-8"
        )


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
            "Cache-Control",
            "no-store"
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
            "GET, POST, OPTIONS"
        )


        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type"
        )


        self.end_headers()


# ============================================================
# REUSABLE TCP SERVER
# ============================================================

class ReusableTCPServer(
    socketserver.ThreadingTCPServer
):

    allow_reuse_address = True

    daemon_threads = True


# ============================================================
# START SERVER
# ============================================================

def start_server():

    server = ReusableTCPServer(
        (
            "127.0.0.1",
            PORT
        ),
        SpideyHandler
    )


    print()
    print(
        "=================================================="
    )
    print(
        "             SPIDEY NATIVE HUD"
    )
    print(
        "=================================================="
    )
    print()


    print(
        "Existing HUD:"
    )


    print(
        f"    {HUD_ROOT / 'index.html'}"
    )


    print()


    print(
        "Python bridge: CONNECTED"
    )


    print(
        "State API: READY"
    )


    print(
        "CHUP API: READY"
    )


    print(
        "Native WebView: READY"
    )


    print()


    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True
    )


    thread.start()


    return server


# ============================================================
# MAIN
# ============================================================

def main():

    server = start_server()


    url = (
        f"http://127.0.0.1:"
        f"{PORT}/index.html"
    )


    print(
        "Loading EXISTING SPIDEY interface:"
    )


    print(
        url
    )


    print()


    try:

        window = webview.create_window(

            "SPIDEY // AI CORE",

            url,

            fullscreen=True,

            resizable=True,

            text_select=False,

            confirm_close=True
        )


        # ----------------------------------------------------
        # WebView2 renders the existing HTML/CSS/JS.
        # ----------------------------------------------------

        webview.start(
            debug=False
        )


    finally:

        try:

            server.shutdown()

        except Exception:

            pass


        try:

            server.server_close()

        except Exception:

            pass


        print(
            "SPIDEY Native HUD stopped."
        )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()