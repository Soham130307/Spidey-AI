import customtkinter as ctk
import tkinter as tk
import psutil
import time
import math
import random


# ============================================================
# SPIDEY // HUD INTERFACE
# Black + red futuristic desktop interface
# Standalone prototype — does NOT modify main.py
# ============================================================

BG = "#020202"
BLACK = "#000000"
PANEL = "#070707"
PANEL_2 = "#0A0A0A"
RED = "#FF1717"
RED2 = "#FF3B3B"
DARK_RED = "#5E0000"
LINE = "#300606"
WHITE = "#F5F5F5"
GRAY = "#777777"
MUTED = "#444444"


class SpideyHUD(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("SPIDEY")
        self.geometry("1600x900")
        self.minsize(1250, 720)
        self.configure(fg_color=BG)

        self.running = True
        self.phase = 0.0
        self.start_time = time.time()
        self.net_samples = [0.0] * 80

        self.protocol("WM_DELETE_WINDOW", self.close)

        self.build_ui()
        self.tick()

    # --------------------------------------------------------
    # ROOT
    # --------------------------------------------------------

    def build_ui(self):
        self.hud = tk.Canvas(
            self,
            bg=BG,
            highlightthickness=0
        )
        self.hud.place(
            relx=0, rely=0,
            relwidth=1, relheight=1
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

        self.ui.grid_columnconfigure(0, weight=25)
        self.ui.grid_columnconfigure(1, weight=50)
        self.ui.grid_columnconfigure(2, weight=25)
        self.ui.grid_rowconfigure(1, weight=1)

        self.top_bar()
        self.left_column()
        self.center_column()
        self.right_column()
        self.bottom_bar()

    # --------------------------------------------------------
    # TOP
    # --------------------------------------------------------

    def top_bar(self):
        bar = ctk.CTkFrame(
            self.ui,
            fg_color="transparent"
        )
        bar.grid(
            row=0, column=0, columnspan=3,
            sticky="ew", pady=(0, 8)
        )
        bar.grid_columnconfigure(1, weight=1)

        brand = ctk.CTkFrame(
            bar, fg_color="transparent"
        )
        brand.grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            brand,
            text="◉",
            font=("Consolas", 24, "bold"),
            text_color=RED
        ).pack(side="left", padx=(0, 12))

        ctk.CTkLabel(
            brand,
            text="SPIDEY",
            font=("Consolas", 25, "bold"),
            text_color=WHITE
        ).pack(side="left")

        self.online = ctk.CTkLabel(
            brand,
            text="  ● ONLINE",
            font=("Consolas", 13, "bold"),
            text_color=RED
        )
        self.online.pack(side="left", padx=18)

        self.mode = ctk.CTkLabel(
            bar,
            text="PERSONAL AI CORE  //  v1.0",
            font=("Consolas", 10),
            text_color=MUTED
        )
        self.mode.grid(row=0, column=1)

        self.time_top = ctk.CTkLabel(
            bar,
            text="00:00:00",
            font=("Consolas", 23, "bold"),
            text_color=RED
        )
        self.time_top.grid(row=0, column=2, sticky="e")

    # --------------------------------------------------------
    # LEFT
    # --------------------------------------------------------

    def left_column(self):
        col = ctk.CTkFrame(
            self.ui, fg_color="transparent"
        )
        col.grid(
            row=1, column=0,
            sticky="nsew",
            padx=(0, 12)
        )

        self.box_system(col)
        self.box_monitor(col)
        self.box_network(col)

    def box_system(self, parent):
        box = self.panel(parent, "SYSTEM STATUS")

        self.label(box, "SPIDEY", GRAY, 11, 18)
        self.label(box, "ONLINE", RED, 21, 2, True)

        self.label(box, "VOICE ENGINE", GRAY, 11, 18)
        self.voice = self.label(
            box, "STANDBY", RED, 18, 2, True
        )

        self.separator(box)

        self.label(box, "CORE LINK", GRAY, 11, 10)
        self.core_link = self.label(
            box, "CONNECTED", WHITE, 14, 2, True
        )

        self.label(box, "SECURITY", GRAY, 11, 12)
        self.label(
            box, "LOCAL / PRIVATE",
            WHITE, 13, 2, True
        )

    def box_monitor(self, parent):
        box = self.panel(parent, "SYSTEM MONITOR")

        self.cpu = self.metric(box, "CPU")
        self.ram = self.metric(box, "RAM")
        self.disk = self.metric(box, "DISK")

        self.separator(box)

        self.label(box, "UPTIME", GRAY, 10, 4)
        self.uptime = self.label(
            box, "00:00:00", RED, 14, 3, True
        )

    def box_network(self, parent):
        box = self.panel(parent, "NETWORK ACTIVITY")

        self.down = self.label(
            box, "↓  DOWNLOAD     0 KB/s",
            WHITE, 11, 7
        )
        self.up = self.label(
            box, "↑  UPLOAD       0 KB/s",
            WHITE, 11, 5
        )

        self.net_canvas = tk.Canvas(
            box,
            height=75,
            bg=PANEL,
            highlightthickness=0
        )
        self.net_canvas.pack(
            fill="x",
            padx=12,
            pady=(8, 10)
        )

    # --------------------------------------------------------
    # CENTER
    # --------------------------------------------------------

    def center_column(self):
        col = ctk.CTkFrame(
            self.ui, fg_color="transparent"
        )
        col.grid(
            row=1, column=1,
            sticky="nsew",
            padx=12
        )

        ctk.CTkLabel(
            col,
            text="S P I D E Y",
            font=("Consolas", 46, "bold"),
            text_color=RED
        ).pack(pady=(0, 0))

        ctk.CTkLabel(
            col,
            text="YOUR PERSONAL AI ASSISTANT",
            font=("Segoe UI", 11),
            text_color=GRAY
        ).pack()

        self.core = tk.Canvas(
            col,
            bg=BG,
            highlightthickness=0
        )
        self.core.pack(
            fill="both",
            expand=True,
            pady=(0, 0)
        )

        self.state_label = ctk.CTkLabel(
            col,
            text="S T A N D B Y",
            font=("Consolas", 23, "bold"),
            text_color=RED
        )
        self.state_label.pack()

        ctk.CTkLabel(
            col,
            text="SAY HEY SPIDEY TO ACTIVATE",
            font=("Segoe UI", 12),
            text_color=WHITE
        ).pack(pady=(4, 10))

        entry_frame = ctk.CTkFrame(
            col,
            fg_color=PANEL,
            border_width=1,
            border_color=DARK_RED,
            corner_radius=2
        )
        entry_frame.pack(
            fill="x",
            padx=25
        )

        self.command = ctk.CTkEntry(
            entry_frame,
            height=46,
            placeholder_text="Speak a command...",
            fg_color=PANEL,
            border_width=0,
            text_color=WHITE,
            placeholder_text_color=GRAY,
            font=("Segoe UI", 13)
        )
        self.command.pack(
            fill="x",
            padx=10
        )

        self.wave = tk.Canvas(
            col,
            height=38,
            bg=BG,
            highlightthickness=0
        )
        self.wave.pack(
            fill="x",
            padx=55,
            pady=(4, 0)
        )

    # --------------------------------------------------------
    # RIGHT
    # --------------------------------------------------------

    def right_column(self):
        col = ctk.CTkFrame(
            self.ui, fg_color="transparent"
        )
        col.grid(
            row=1, column=2,
            sticky="nsew",
            padx=(12, 0)
        )

        self.time_box(col)
        self.log_box(col)
        self.commands_box(col)

    def time_box(self, parent):
        box = self.panel(parent, "LOCAL TIME")

        self.big_time = self.label(
            box,
            "00:00:00",
            RED, 29, 3, True
        )

        self.date = self.label(
            box,
            "Tuesday, 25 August 2026",
            GRAY, 10, 2
        )

        self.label(
            box,
            "SYSTEM CLOCK  //  LOCAL",
            MUTED, 9, 10
        )

    def log_box(self, parent):
        box = self.panel(
            parent,
            "SPIDEY LOG",
            expand=True
        )

        self.log = ctk.CTkTextbox(
            box,
            fg_color=PANEL,
            border_width=0,
            text_color=WHITE,
            font=("Consolas", 10),
            wrap="word"
        )
        self.log.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=8
        )

        self.write_log("System initialized")
        self.write_log("Voice engine online")
        self.write_log("Core connection established")
        self.write_log("SPIDEY standing by")

    def commands_box(self, parent):
        box = self.panel(parent, "QUICK COMMANDS")

        commands = [
            "OPEN YOUTUBE",
            "SEARCH GOOGLE",
            "OPEN DISCORD",
            "OPEN CALCULATOR",
            "SYSTEM INFORMATION"
        ]

        for item in commands:
            ctk.CTkButton(
                box,
                text="›  " + item,
                height=33,
                anchor="w",
                fg_color="transparent",
                hover_color="#240000",
                text_color=WHITE,
                font=("Consolas", 10),
                command=lambda x=item: self.quick_command(x)
            ).pack(
                fill="x",
                padx=7,
                pady=1
            )

    # --------------------------------------------------------
    # BOTTOM
    # --------------------------------------------------------

    def bottom_bar(self):
        bottom = ctk.CTkFrame(
            self.ui,
            fg_color=PANEL,
            border_width=1,
            border_color=DARK_RED,
            corner_radius=2,
            height=64
        )
        bottom.grid(
            row=2, column=0, columnspan=3,
            sticky="ew",
            pady=(10, 0)
        )

        bottom.grid_columnconfigure(0, weight=1)
        bottom.grid_columnconfigure(1, weight=1)
        bottom.grid_columnconfigure(2, weight=1)

        music = ctk.CTkFrame(
            bottom, fg_color="transparent"
        )
        music.grid(
            row=0, column=0,
            sticky="w", padx=18
        )

        ctk.CTkLabel(
            music,
            text="♫  NOW PLAYING",
            font=("Consolas", 10, "bold"),
            text_color=RED
        ).pack(anchor="w")

        ctk.CTkLabel(
            music,
            text="NO MEDIA DETECTED",
            font=("Segoe UI", 9),
            text_color=GRAY
        ).pack(anchor="w")

        self.activation = ctk.CTkLabel(
            bottom,
            text="◉   DOUBLE CLAP  //  ACTIVATE SPIDEY",
            font=("Consolas", 12, "bold"),
            text_color=RED
        )
        self.activation.grid(row=0, column=1)

        weather = ctk.CTkFrame(
            bottom, fg_color="transparent"
        )
        weather.grid(
            row=0, column=2,
            sticky="e", padx=18
        )

        ctk.CTkLabel(
            weather,
            text="WEATHER",
            font=("Consolas", 10, "bold"),
            text_color=RED
        ).pack(anchor="e")

        ctk.CTkLabel(
            weather,
            text="--°C   --",
            font=("Segoe UI", 9),
            text_color=GRAY
        ).pack(anchor="e")

    # --------------------------------------------------------
    # STYLE HELPERS
    # --------------------------------------------------------

    def panel(self, parent, title, expand=False):
        box = ctk.CTkFrame(
            parent,
            fg_color=PANEL,
            border_width=1,
            border_color=DARK_RED,
            corner_radius=2
        )
        box.pack(
            fill="both" if expand else "x",
            expand=expand,
            pady=5
        )

        ctk.CTkLabel(
            box,
            text=title,
            font=("Consolas", 11, "bold"),
            text_color=RED
        ).pack(
            anchor="w",
            padx=15,
            pady=(12, 5)
        )
        return box

    def label(
        self, parent, text, color,
        size=11, top=4, bold=False
    ):
        lbl = ctk.CTkLabel(
            parent,
            text=text,
            font=(
                "Consolas",
                size,
                "bold" if bold else "normal"
            ),
            text_color=color
        )
        lbl.pack(
            anchor="w",
            padx=18,
            pady=(top, 0)
        )
        return lbl

    def separator(self, parent):
        ctk.CTkFrame(
            parent,
            height=1,
            fg_color=LINE
        ).pack(
            fill="x",
            padx=15,
            pady=10
        )

    def metric(self, parent, name):
        row = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )
        row.pack(
            fill="x",
            padx=18,
            pady=4
        )

        ctk.CTkLabel(
            row,
            text=name,
            font=("Consolas", 11),
            text_color=WHITE
        ).pack(side="left")

        value = ctk.CTkLabel(
            row,
            text="--%",
            font=("Consolas", 11, "bold"),
            text_color=RED
        )
        value.pack(side="right")

        return value

    # --------------------------------------------------------
    # SPIDER HUD
    # --------------------------------------------------------

    def draw_core(self):
        self.core.delete("all")

        w = max(self.core.winfo_width(), 560)
        h = max(self.core.winfo_height(), 430)
        cx = w / 2
        cy = h / 2

        p = 5 * (math.sin(self.phase) + 1)

        # large outer circles
        for r, color, width in [
            (195, DARK_RED, 1),
            (178, RED, 2),
            (158, DARK_RED, 1),
            (140, RED, 2),
            (115, DARK_RED, 1),
        ]:
            self.core.create_oval(
                cx-r-p,
                cy-r-p,
                cx+r+p,
                cy+r+p,
                outline=color,
                width=width
            )

        # segmented arcs
        for start in range(0, 360, 60):
            self.core.create_arc(
                cx-190, cy-190,
                cx+190, cy+190,
                start=start + 8,
                extent=38,
                style=tk.ARC,
                outline=RED,
                width=3
            )

        for start in range(20, 360, 90):
            self.core.create_arc(
                cx-160, cy-160,
                cx+160, cy+160,
                start=start,
                extent=28,
                style=tk.ARC,
                outline=RED2,
                width=2
            )

        # technical crosshair
        self.core.create_line(
            cx-220, cy, cx-150, cy,
            fill=RED, width=1
        )
        self.core.create_line(
            cx+150, cy, cx+220, cy,
            fill=RED, width=1
        )
        self.core.create_line(
            cx, cy-220, cx, cy-150,
            fill=RED, width=1
        )
        self.core.create_line(
            cx, cy+150, cx, cy+220,
            fill=RED, width=1
        )

        # four target ticks
        for dx, dy in [
            (-190, -190), (190, -190),
            (-190, 190), (190, 190)
        ]:
            self.core.create_line(
                cx+dx, cy+dy,
                cx+dx + (15 if dx < 0 else -15),
                cy+dy,
                fill=RED,
                width=2
            )

        # spider
        self.spider(cx, cy)

        # rotating orbit dots
        angle = self.phase * 0.8
        for i in range(6):
            a = angle + i * math.pi / 3
            r = 190
            x = cx + math.cos(a) * r
            y = cy + math.sin(a) * r
            self.core.create_oval(
                x-3, y-3, x+3, y+3,
                fill=RED2,
                outline=""
            )

        # center dot
        self.core.create_oval(
            cx-4, cy-4, cx+4, cy+4,
            fill=WHITE, outline=""
        )

    def spider(self, cx, cy):
        # subtle spider aura
        self.core.create_oval(
            cx-70, cy-70,
            cx+70, cy+70,
            outline="#310505",
            width=1
        )

        # body
        self.core.create_oval(
            cx-24, cy-22,
            cx+24, cy+40,
            fill=RED,
            outline=RED2,
            width=1
        )

        # head
        self.core.create_oval(
            cx-19, cy-55,
            cx+19, cy-19,
            fill=RED,
            outline=RED2
        )

        # eyes
        for sx in (-8, 8):
            self.core.create_oval(
                cx+sx-2, cy-44,
                cx+sx+2, cy-40,
                fill=WHITE,
                outline=""
            )

        # legs with angular shape
        for side in (-1, 1):
            for i in range(4):
                y1 = cy - 18 + i * 17
                x1 = cx + side * 16

                x2 = cx + side * (48 + i * 8)
                y2 = y1 - 13

                x3 = cx + side * (82 + i * 7)
                y3 = y1 + (-25 + i * 16)

                self.core.create_line(
                    x1, y1,
                    x2, y2,
                    x3, y3,
                    fill=RED2,
                    width=4
                )

    # --------------------------------------------------------
    # ANIMATION / DATA
    # --------------------------------------------------------

    def tick(self):
        if not self.running:
            return

        self.phase += 0.055
        self.draw_core()
        self.draw_wave()
        self.update_time()
        self.update_stats()

        self.after(60, self.tick)

    def draw_wave(self):
        self.wave.delete("all")

        w = max(self.wave.winfo_width(), 450)
        mid = 19
        points = []

        for x in range(0, w, 5):
            envelope = math.sin(
                math.pi * x / w
            )
            y = mid + math.sin(
                x * 0.10 + self.phase * 5
            ) * 9 * envelope
            points.append((x, y))

        if len(points) > 1:
            self.wave.create_line(
                points,
                fill=RED,
                width=2,
                smooth=True
            )

    def update_time(self):
        now = time.localtime()
        value = time.strftime("%H:%M:%S", now)

        self.time_top.configure(text=value)
        self.big_time.configure(text=value)
        self.date.configure(
            text=time.strftime("%A, %d %B %Y", now)
        )

    def update_stats(self):
        try:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            disk = psutil.disk_usage("C:\\").percent

            self.cpu.configure(text=f"{cpu:.0f}%")
            self.ram.configure(text=f"{ram:.0f}%")
            self.disk.configure(text=f"{disk:.0f}%")

            elapsed = int(time.time() - self.start_time)
            self.uptime.configure(
                text=time.strftime(
                    "%H:%M:%S",
                    time.gmtime(elapsed)
                )
            )

            # Simulated HUD network trace for visual prototype
            v = random.uniform(0, 35)
            self.net_samples.append(v)
            self.net_samples = self.net_samples[-80:]

            self.down.configure(
                text=f"↓  DOWNLOAD     {v:.0f} KB/s"
            )
            self.up.configure(
                text=f"↑  UPLOAD       {v/2:.0f} KB/s"
            )

            self.net_canvas.delete("all")
            width = max(
                self.net_canvas.winfo_width(), 250
            )
            height = 75

            points = []
            for i, value in enumerate(self.net_samples):
                x = i * width / 79
                y = height - 10 - value * 1.3
                points.append((x, y))

            if len(points) > 1:
                self.net_canvas.create_line(
                    points,
                    fill=RED,
                    width=1,
                    smooth=True
                )

        except Exception:
            pass

    # --------------------------------------------------------
    # COMMANDS
    # --------------------------------------------------------

    def write_log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.log.insert(
            "end",
            f"{timestamp}  {message}\n"
        )
        self.log.see("end")

    def quick_command(self, command):
        self.command.delete(0, "end")
        self.command.insert(0, command)
        self.write_log(
            f"Command queued: {command}"
        )

    def close(self):
        self.running = False
        self.destroy()


if __name__ == "__main__":
    app = SpideyHUD()
    app.mainloop()
