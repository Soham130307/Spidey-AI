import customtkinter as ctk
import tkinter as tk
import threading
import http.server
import socketserver
import json
import os
import time
import math
import urllib.request
from pathlib import Path

try:
    import psutil
except Exception:
    psutil = None


# ============================================================
# SPIDEY // NATIVE WINDOWS HUD
# ============================================================

PORT = 8765
BG = "#020202"
PANEL = "#070707"
PANEL_2 = "#0A0A0A"
RED = "#FF1717"
RED2 = "#FF3B3B"
DARK_RED = "#5E0000"
LINE = "#300606"
WHITE = "#F5F5F5"
GRAY = "#777777"
MUTED = "#444444"

ROOT = Path(__file__).resolve().parent
CHUP_FLAG_FILE = ROOT / "chup.flag"

last_hud_state = "STANDBY|Starting SPIDEY..."
server = None
app = None


# ============================================================
# HTTP BRIDGE
# ============================================================

class SpideyHandler(http.server.BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        # Keep the terminal clean; the native HUD is the UI now.
        pass

    def _send_json(self, payload):
        data = json.dumps(payload).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        self.wfile.write(data)

    def do_GET(self):

        if self.path.split("?", 1)[0] == "/api/state":

            self._send_json({
                "success": True,
                "state": last_hud_state
            })

            return

        self.send_error(404)

    def do_POST(self):

        global last_hud_state

        path = self.path.split("?", 1)[0]

        if path == "/api/state":

            try:
                length = int(
                    self.headers.get(
                        "Content-Length",
                        "0"
                    )
                )

                body = self.rfile.read(length)
                data = json.loads(body.decode("utf-8"))

                last_hud_state = data.get(
                    "state",
                    "READY"
                )

                if app is not None:
                    app.after(
                        0,
                        app.apply_hud_state,
                        last_hud_state
                    )

                self._send_json({
                    "success": True,
                    "state": last_hud_state
                })

            except Exception as e:

                self._send_json({
                    "success": False,
                    "message": str(e)
                })

            return

        if path == "/api/chup":

            try:
                CHUP_FLAG_FILE.touch(exist_ok=True)

                self._send_json({
                    "success": True,
                    "message": "CHUP signal sent."
                })

            except Exception as e:

                self._send_json({
                    "success": False,
                    "message": str(e)
                })

            return

        self.send_error(404)


def start_bridge():

    global server

    try:

        server = socketserver.ThreadingTCPServer(
            ("127.0.0.1", PORT),
            SpideyHandler
        )

        server.daemon_threads = True
        server.allow_reuse_address = True

        print(
            f"SPIDEY native bridge running on 127.0.0.1:{PORT}"
        )

        server.serve_forever()

    except Exception as e:

        print(
            "Native HUD bridge error:",
            e
        )


# ============================================================
# NATIVE HUD
# ============================================================

class SpideyHUD(ctk.CTk):

    def __init__(self):

        super().__init__()

        global app
        app = self

        self.title("SPIDEY")
        self.geometry("1600x900")
        self.minsize(1200, 720)
        self.configure(
            fg_color=BG
        )

        self.running = True
        self.phase = 0.0
        self.start_time = time.time()

        self.current_state = "STANDBY"
        self.current_message = "Starting SPIDEY..."

        self.protocol(
            "WM_DELETE_WINDOW",
            self.close
        )

        self.build_ui()

        self.after(
            60,
            self.tick
        )

        self.after(
            250,
            self.update_stats
        )

    # ========================================================
    # UI
    # ========================================================

    def build_ui(self):

        self.hud = tk.Canvas(
            self,
            bg=BG,
            highlightthickness=0
        )

        self.hud.place(
            relx=0,
            rely=0,
            relwidth=1,
            relheight=1
        )

        self.ui = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.ui.place(
            relx=0.018,
            rely=0.018,
            relwidth=0.964,
            relheight=0.964
        )

        self.ui.grid_columnconfigure(
            0,
            weight=25
        )

        self.ui.grid_columnconfigure(
            1,
            weight=50
        )

        self.ui.grid_columnconfigure(
            2,
            weight=25
        )

        self.ui.grid_rowconfigure(
            1,
            weight=1
        )

        self.top_bar()
        self.left_column()
        self.center_column()
        self.right_column()
        self.bottom_bar()

    # ========================================================
    # TOP
    # ========================================================

    def top_bar(self):

        bar = ctk.CTkFrame(
            self.ui,
            fg_color="transparent"
        )

        bar.grid(
            row=0,
            column=0,
            columnspan=3,
            sticky="ew",
            pady=(0, 8)
        )

        bar.grid_columnconfigure(
            1,
            weight=1
        )

        brand = ctk.CTkFrame(
            bar,
            fg_color="transparent"
        )

        brand.grid(
            row=0,
            column=0,
            sticky="w"
        )

        ctk.CTkLabel(
            brand,
            text="◉",
            font=("Consolas", 24, "bold"),
            text_color=RED
        ).pack(
            side="left",
            padx=(0, 12)
        )

        ctk.CTkLabel(
            brand,
            text="SPIDEY",
            font=("Consolas", 25, "bold"),
            text_color=WHITE
        ).pack(
            side="left"
        )

        self.online = ctk.CTkLabel(
            brand,
            text="  ● ONLINE",
            font=("Consolas", 13, "bold"),
            text_color=RED
        )

        self.online.pack(
            side="left"
        )

        self.time_top = ctk.CTkLabel(
            bar,
            text="00:00:00",
            font=("Consolas", 15),
            text_color=GRAY
        )

        self.time_top.grid(
            row=0,
            column=1,
            sticky="e",
            padx=(0, 20)
        )

        self.native_badge = ctk.CTkLabel(
            bar,
            text="NATIVE DESKTOP",
            font=("Consolas", 11, "bold"),
            text_color=RED2
        )

        self.native_badge.grid(
            row=0,
            column=2,
            sticky="e"
        )

    # ========================================================
    # LEFT
    # ========================================================

    def left_column(self):

        frame = ctk.CTkFrame(
            self.ui,
            fg_color=PANEL,
            corner_radius=12,
            border_width=1,
            border_color=LINE
        )

        frame.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=(0, 8)
        )

        ctk.CTkLabel(
            frame,
            text="SYSTEM",
            font=("Consolas", 13, "bold"),
            text_color=RED
        ).pack(
            anchor="w",
            padx=18,
            pady=(18, 12)
        )

        self.cpu = self.stat_row(
            frame,
            "CPU"
        )

        self.ram = self.stat_row(
            frame,
            "RAM"
        )

        self.disk = self.stat_row(
            frame,
            "DISK"
        )

        self.uptime = self.stat_row(
            frame,
            "UPTIME"
        )

        ctk.CTkLabel(
            frame,
            text="NETWORK",
            font=("Consolas", 11, "bold"),
            text_color=GRAY
        ).pack(
            anchor="w",
            padx=18,
            pady=(28, 8)
        )

        self.down = ctk.CTkLabel(
            frame,
            text="↓  DOWNLOAD     -- KB/s",
            font=("Consolas", 10),
            text_color=GRAY
        )

        self.down.pack(
            anchor="w",
            padx=18,
            pady=3
        )

        self.up = ctk.CTkLabel(
            frame,
            text="↑  UPLOAD       -- KB/s",
            font=("Consolas", 10),
            text_color=GRAY
        )

        self.up.pack(
            anchor="w",
            padx=18,
            pady=3
        )

        self.net_canvas = tk.Canvas(
            frame,
            height=90,
            bg=PANEL,
            highlightthickness=0
        )

        self.net_canvas.pack(
            fill="x",
            padx=18,
            pady=(10, 18)
        )

    def stat_row(self, parent, name):

        row = ctk.CTkFrame(
            parent,
            fg_color=PANEL_2,
            corner_radius=7
        )

        row.pack(
            fill="x",
            padx=12,
            pady=4
        )

        ctk.CTkLabel(
            row,
            text=name,
            font=("Consolas", 10, "bold"),
            text_color=GRAY
        ).pack(
            side="left",
            padx=10,
            pady=8
        )

        value = ctk.CTkLabel(
            row,
            text="--",
            font=("Consolas", 11, "bold"),
            text_color=WHITE
        )

        value.pack(
            side="right",
            padx=10
        )

        return value

    # ========================================================
    # CENTER
    # ========================================================

    def center_column(self):

        frame = ctk.CTkFrame(
            self.ui,
            fg_color=PANEL,
            corner_radius=12,
            border_width=1,
            border_color=LINE
        )

        frame.grid(
            row=1,
            column=1,
            sticky="nsew",
            padx=8
        )

        self.core = tk.Canvas(
            frame,
            bg=PANEL,
            highlightthickness=0
        )

        self.core.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        self.status = ctk.CTkLabel(
            frame,
            text="STANDBY",
            font=("Consolas", 18, "bold"),
            text_color=RED
        )

        self.status.pack(
            pady=(0, 4)
        )

        self.message = ctk.CTkLabel(
            frame,
            text="Starting SPIDEY...",
            font=("Consolas", 11),
            text_color=GRAY,
            wraplength=650
        )

        self.message.pack(
            pady=(0, 15)
        )

        self.wave = tk.Canvas(
            frame,
            height=40,
            bg=PANEL,
            highlightthickness=0
        )

        self.wave.pack(
            fill="x",
            padx=35,
            pady=(0, 20)
        )

    # ========================================================
    # RIGHT
    # ========================================================

    def right_column(self):

        frame = ctk.CTkFrame(
            self.ui,
            fg_color=PANEL,
            corner_radius=12,
            border_width=1,
            border_color=LINE
        )

        frame.grid(
            row=1,
            column=2,
            sticky="nsew",
            padx=(8, 0)
        )

        ctk.CTkLabel(
            frame,
            text="SPIDEY CONTROL",
            font=("Consolas", 13, "bold"),
            text_color=RED
        ).pack(
            anchor="w",
            padx=18,
            pady=(18, 15)
        )

        ctk.CTkLabel(
            frame,
            text="CURRENT STATE",
            font=("Consolas", 10),
            text_color=GRAY
        ).pack(
            anchor="w",
            padx=18
        )

        self.state_detail = ctk.CTkLabel(
            frame,
            text="STANDBY",
            font=("Consolas", 12, "bold"),
            text_color=WHITE
        )

        self.state_detail.pack(
            anchor="w",
            padx=18,
            pady=(5, 20)
        )

        self.chup_button = ctk.CTkButton(
            frame,
            text="CHUP  //  STOP SPEECH",
            font=("Consolas", 11, "bold"),
            fg_color=RED,
            hover_color=RED2,
            text_color=WHITE,
            height=42,
            command=self.chup
        )

        self.chup_button.pack(
            fill="x",
            padx=18,
            pady=(0, 18)
        )

        ctk.CTkLabel(
            frame,
            text="BRIDGE",
            font=("Consolas", 10),
            text_color=GRAY
        ).pack(
            anchor="w",
            padx=18,
            pady=(8, 5)
        )

        self.bridge = ctk.CTkLabel(
            frame,
            text="● CONNECTED",
            font=("Consolas", 11, "bold"),
            text_color=RED
        )

        self.bridge.pack(
            anchor="w",
            padx=18
        )

        ctk.CTkLabel(
            frame,
            text="HUD MODE",
            font=("Consolas", 10),
            text_color=GRAY
        ).pack(
            anchor="w",
            padx=18,
            pady=(22, 5)
        )

        ctk.CTkLabel(
            frame,
            text="NATIVE WINDOWS",
            font=("Consolas", 11, "bold"),
            text_color=WHITE
        ).pack(
            anchor="w",
            padx=18
        )

        ctk.CTkLabel(
            frame,
            text="No browser required.",
            font=("Consolas", 10),
            text_color=MUTED
        ).pack(
            anchor="w",
            padx=18,
            pady=(4, 0)
        )

    # ========================================================
    # BOTTOM
    # ========================================================

    def bottom_bar(self):

        bar = ctk.CTkFrame(
            self.ui,
            fg_color="transparent"
        )

        bar.grid(
            row=2,
            column=0,
            columnspan=3,
            sticky="ew",
            pady=(8, 0)
        )

        self.date = ctk.CTkLabel(
            bar,
            text="",
            font=("Consolas", 10),
            text_color=GRAY
        )

        self.date.pack(
            side="left"
        )

        self.footer = ctk.CTkLabel(
            bar,
            text="SPIDEY // NATIVE DESKTOP CORE",
            font=("Consolas", 10),
            text_color=MUTED
        )

        self.footer.pack(
            side="right"
        )

    # ========================================================
    # STATE
    # ========================================================

    def apply_hud_state(self, value):

        if not self.running:
            return

        self.current_state = value.split(
            "|",
            1
        )[0].upper()

        if "|" in value:
            self.current_message = value.split(
                "|",
                1
            )[1]
        else:
            self.current_message = value

        self.status.configure(
            text=self.current_state
        )

        self.state_detail.configure(
            text=self.current_state
        )

        self.message.configure(
            text=self.current_message
        )

        if self.current_state == "LISTENING":
            self.status.configure(
                text_color=RED2
            )

        elif self.current_state == "THINKING":
            self.status.configure(
                text_color=WHITE
            )

        elif self.current_state == "SPEAKING":
            self.status.configure(
                text_color=RED
            )

        else:
            self.status.configure(
                text_color=RED
            )

    # ========================================================
    # ANIMATION
    # ========================================================

    def tick(self):

        if not self.running:
            return

        self.phase += 0.055

        self.draw_core()
        self.draw_wave()
        self.update_time()

        self.after(
            60,
            self.tick
        )

    def draw_core(self):

        self.core.delete("all")

        width = max(
            self.core.winfo_width(),
            500
        )

        height = max(
            self.core.winfo_height(),
            400
        )

        cx = width / 2
        cy = height / 2

        radius = min(
            width,
            height
        ) * 0.34

        # outer rings
        for r, w in [
            (radius, 1),
            (radius - 28, 1),
            (radius - 58, 1)
        ]:

            self.core.create_oval(
                cx - r,
                cy - r,
                cx + r,
                cy + r,
                outline=LINE,
                width=w
            )

        # crosshair
        self.core.create_line(
            cx - radius - 30,
            cy,
            cx - radius + 30,
            cy,
            fill=RED,
            width=1
        )

        self.core.create_line(
            cx + radius - 30,
            cy,
            cx + radius + 30,
            cy,
            fill=RED,
            width=1
        )

        self.core.create_line(
            cx,
            cy - radius - 30,
            cx,
            cy - radius + 30,
            fill=RED,
            width=1
        )

        self.core.create_line(
            cx,
            cy + radius - 30,
            cx,
            cy + radius + 30,
            fill=RED,
            width=1
        )

        # rotating dots
        for i in range(8):

            angle = (
                self.phase * 0.75
                +
                i * math.pi / 4
            )

            x = cx + math.cos(angle) * radius
            y = cy + math.sin(angle) * radius

            self.core.create_oval(
                x - 3,
                y - 3,
                x + 3,
                y + 3,
                fill=RED2,
                outline=""
            )

        # spider
        self.draw_spider(
            cx,
            cy
        )

        # center
        self.core.create_oval(
            cx - 4,
            cy - 4,
            cx + 4,
            cy + 4,
            fill=WHITE,
            outline=""
        )

    def draw_spider(self, cx, cy):

        pulse = (
            math.sin(
                self.phase * 2
            ) + 1
        ) * 3

        self.core.create_oval(
            cx - 78 - pulse,
            cy - 78 - pulse,
            cx + 78 + pulse,
            cy + 78 + pulse,
            outline=DARK_RED,
            width=1
        )

        # body
        self.core.create_oval(
            cx - 24,
            cy - 20,
            cx + 24,
            cy + 42,
            fill=RED,
            outline=RED2,
            width=1
        )

        # head
        self.core.create_oval(
            cx - 19,
            cy - 56,
            cx + 19,
            cy - 19,
            fill=RED,
            outline=RED2
        )

        # eyes
        for sx in (-8, 8):

            self.core.create_oval(
                cx + sx - 2,
                cy - 45,
                cx + sx + 2,
                cy - 41,
                fill=WHITE,
                outline=""
            )

        # legs
        for side in (-1, 1):

            for i in range(4):

                y1 = (
                    cy - 18
                    +
                    i * 17
                )

                x1 = cx + side * 16

                x2 = (
                    cx
                    +
                    side * (
                        48
                        +
                        i * 8
                    )
                )

                y2 = y1 - 13

                x3 = (
                    cx
                    +
                    side * (
                        82
                        +
                        i * 7
                    )
                )

                y3 = (
                    y1
                    +
                    (-25 + i * 16)
                )

                self.core.create_line(
                    x1,
                    y1,
                    x2,
                    y2,
                    x3,
                    y3,
                    fill=RED2,
                    width=4
                )

    def draw_wave(self):

        self.wave.delete("all")

        width = max(
            self.wave.winfo_width(),
            450
        )

        mid = 20
        points = []

        for x in range(
            0,
            width,
            5
        ):

            envelope = math.sin(
                math.pi * x / width
            )

            amplitude = 9

            if self.current_state == "LISTENING":
                amplitude = 13

            elif self.current_state == "SPEAKING":
                amplitude = 16

            y = (
                mid
                +
                math.sin(
                    x * 0.10
                    +
                    self.phase * 5
                )
                * amplitude
                * envelope
            )

            points.append(
                (x, y)
            )

        if len(points) > 1:

            self.wave.create_line(
                points,
                fill=RED,
                width=2,
                smooth=True
            )

    # ========================================================
    # DATA
    # ========================================================

    def update_time(self):

        now = time.localtime()

        value = time.strftime(
            "%H:%M:%S",
            now
        )

        self.time_top.configure(
            text=value
        )

        self.date.configure(
            text=time.strftime(
                "%A, %d %B %Y",
                now
            )
        )

    def update_stats(self):

        if not self.running:
            return

        try:

            if psutil is not None:

                cpu = psutil.cpu_percent(
                    interval=None
                )

                ram = psutil.virtual_memory().percent

                disk = psutil.disk_usage(
                    "C:\\"
                ).percent

                self.cpu.configure(
                    text=f"{cpu:.0f}%"
                )

                self.ram.configure(
                    text=f"{ram:.0f}%"
                )

                self.disk.configure(
                    text=f"{disk:.0f}%"
                )

            elapsed = int(
                time.time()
                -
                self.start_time
            )

            self.uptime.configure(
                text=time.strftime(
                    "%H:%M:%S",
                    time.gmtime(elapsed)
                )
            )

        except Exception:
            pass

        self.after(
            1000,
            self.update_stats
        )

    # ========================================================
    # CHUP
    # ========================================================

    def chup(self):

        try:

            CHUP_FLAG_FILE.touch(
                exist_ok=True
            )

            self.message.configure(
                text="Speech stop requested..."
            )

        except Exception as e:

            self.message.configure(
                text=f"CHUP error: {e}"
            )

    # ========================================================
    # CLOSE
    # ========================================================

    def close(self):

        global server

        self.running = False

        try:

            if server is not None:
                server.shutdown()
                server.server_close()

        except Exception:
            pass

        self.destroy()


# ============================================================
# START
# ============================================================

def main():

    bridge = threading.Thread(
        target=start_bridge,
        daemon=True
    )

    bridge.start()

    time.sleep(0.25)

    hud = SpideyHUD()

    print(
        "SPIDEY NATIVE DESKTOP HUD: ONLINE"
    )

    hud.mainloop()


if __name__ == "__main__":
    main()
