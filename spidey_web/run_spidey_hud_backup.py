import http.server
import socketserver
import webbrowser
from pathlib import Path


# ============================================================
# SPIDEY WEB HUD LAUNCHER
# ============================================================

PORT = 8765

ROOT = Path(__file__).parent


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


print()
print("=" * 50)
print("        SPIDEY HUD")
print("=" * 50)
print()
print("Starting interface...")
print()


with socketserver.TCPServer(
    ("127.0.0.1", PORT),
    SpideyHandler
) as server:

    url = (
        f"http://127.0.0.1:"
        f"{PORT}/index.html"
    )

    print(
        f"SPIDEY HUD running at:"
    )

    print(url)

    print()
    print(
        "Opening interface..."
    )

    webbrowser.open(url)

    print()
    print(
        "Press CTRL+C to stop SPIDEY HUD."
    )

    print()

    try:

        server.serve_forever()

    except KeyboardInterrupt:

        print()
        print(
            "SPIDEY HUD stopped."
        )