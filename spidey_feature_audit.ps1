$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "             SPIDEY COMPLETE FEATURE AUDIT" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$main  = Get-Content ".\main.py" -Raw -ErrorAction SilentlyContinue
$tools = if (Test-Path ".\tools.py") { Get-Content ".\tools.py" -Raw } else { "" }
$app   = if (Test-Path ".\spidey_web\app.js") { Get-Content ".\spidey_web\app.js" -Raw } else { "" }
$hud   = if (Test-Path ".\spidey_web\run_spidey_hud_native.py") { Get-Content ".\spidey_web\run_spidey_hud_native.py" -Raw } else { "" }

$implemented = 0
$missing = 0
$needsTest = 0

function Feature($name, $patterns, $files) {

    $found = $false
    $hits = @()

    foreach ($f in $files) {
        if ($f.Text) {
            foreach ($p in $patterns) {
                if ($f.Text -match $p) {
                    $found = $true
                    $hits += $f.Name
                    break
                }
            }
        }
    }

    if ($found) {
        Write-Host "[ OK ] $name" -ForegroundColor Green
        Write-Host "       Code/wiring detected in: $($hits -join ', ')" -ForegroundColor DarkGray
        $script:implemented++
    }
    else {
        Write-Host "[ -- ] $name" -ForegroundColor DarkGray
        $script:missing++
    }
}

function TestLive($name, $condition) {
    if ($condition) {
        Write-Host "[LIVE] $name" -ForegroundColor Green
    }
    else {
        Write-Host "[----] $name - requires SPIDEY running" -ForegroundColor Yellow
        $script:needsTest++
    }
}

$files = @(
    [PSCustomObject]@{Name="main.py"; Text=$main},
    [PSCustomObject]@{Name="tools.py"; Text=$tools},
    [PSCustomObject]@{Name="app.js"; Text=$app},
    [PSCustomObject]@{Name="HUD server"; Text=$hud}
)

# ============================================================
# CORE ASSISTANT
# ============================================================

Write-Host ""
Write-Host "================ CORE ASSISTANT ================" -ForegroundColor Magenta

Feature "SPIDEY main command loop" @(
    "run_spidey",
    "while True"
) $files

Feature "Voice input / microphone" @(
    "sounddevice",
    "InputStream",
    "listen\("
) $files

Feature "Text-to-speech / voice output" @(
    "pyttsx3",
    "edge_tts",
    "say\(",
    "speak\("
) $files

Feature "Wake word detection" @(
    "listen_for_wake_word",
    "hi spidey",
    "hey spidey",
    "wake"
) $files

Feature "Push-to-talk / SPACE activation" @(
    "space_held",
    "keyboard.is_pressed.*space",
    "wait_for_space"
) $files

Feature "Typed command input" @(
    "TYPED_COMMAND_FILE",
    "pop_typed_command",
    "/api/command",
    "commandBox"
) $files

# ============================================================
# AI
# ============================================================

Write-Host ""
Write-Host "================ AI / BRAIN ================" -ForegroundColor Magenta

Feature "AI router" @(
    "ai_router",
    "route",
    "router"
) $files

Feature "Gemini integration" @(
    "gemini",
    "GenerativeModel",
    "GOOGLE_API_KEY",
    "GEMINI"
) $files

Feature "Ollama integration" @(
    "ollama",
    "localhost:11434",
    "11434"
) $files

Feature "AI fallback/routing" @(
    "fallback",
    "OLLAMA",
    "GEMINI",
    "AI.*router"
) $files

Feature "Conversation/memory system" @(
    "memory",
    "MEMORY LOADED",
    "load_memory",
    "save_memory"
) $files

# ============================================================
# PRODUCTIVITY
# ============================================================

Write-Host ""
Write-Host "================ PRODUCTIVITY ================" -ForegroundColor Magenta

Feature "Meeting Notes Summarizer" @(
    "meeting notes",
    "meeting.*summar",
    "summar.*meeting"
) $files

Feature "Action Item Generator" @(
    "action items",
    "action item",
    "generate.*action"
) $files

Feature "Email Rewriter" @(
    "rewrite email",
    "email rewriter",
    "rewrite.*email"
) $files

Feature "Presentation Outline Generator" @(
    "presentation outline",
    "presentation.*outline"
) $files

Feature "LinkedIn Post Generator" @(
    "linkedin",
    "LinkedIn"
) $files

Feature "Brainstorm Ideas" @(
    "brainstorm"
) $files

Feature "Translation" @(
    "translation",
    "translate"
) $files

Feature "Study Notes" @(
    "study notes",
    "study.*notes",
    "study"
) $files

# ============================================================
# SYSTEM AUTOMATION
# ============================================================

Write-Host ""
Write-Host "================ SYSTEM AUTOMATION ================" -ForegroundColor Magenta

Feature "Application launching" @(
    "subprocess",
    "os.startfile",
    "launch"
) $files

Feature "Browser / web opening" @(
    "webbrowser",
    "open.*browser",
    "http"
) $files

Feature "YouTube search/opening" @(
    "youtube",
    "YouTube"
) $files

Feature "Spotify control" @(
    "spotify",
    "Spotify"
) $files

Feature "Computer control" @(
    "computer",
    "pyautogui",
    "mouse",
    "keyboard"
) $files

Feature "Browser automation" @(
    "browser",
    "selenium",
    "playwright"
) $files

# ============================================================
# TIME / REMINDERS
# ============================================================

Write-Host ""
Write-Host "================ TIME / REMINDERS ================" -ForegroundColor Magenta

Feature "Alarm system" @(
    "alarm",
    "alarm_manager",
    "set_alarm"
) $files

Feature "Timer system" @(
    "timer",
    "countdown",
    "set_timer"
) $files

Feature "Stop/cancel alarm" @(
    "stop_alarm",
    "cancel_alarm",
    "alarm.*stop"
) $files

Feature "Time/date queries" @(
    "datetime",
    "strftime",
    "what time",
    "current time"
) $files

# ============================================================
# VISION
# ============================================================

Write-Host ""
Write-Host "================ VISION ================" -ForegroundColor Magenta

Feature "Screen vision" @(
    "screen_vision",
    "screen analyzer",
    "screen_analyzer"
) $files

Feature "Screen OCR" @(
    "screen_ocr",
    "OCR",
    "pytesseract"
) $files

Feature "Screenshot analysis" @(
    "screenshot",
    "ImageGrab",
    "mss"
) $files

Feature "Computer vision" @(
    "cv2",
    "opencv",
    "vision"
) $files

# ============================================================
# GESTURES / SECURITY
# ============================================================

Write-Host ""
Write-Host "================ GESTURES / SECURITY ================" -ForegroundColor Magenta

Feature "Gesture recognition" @(
    "gesture",
    "MediaPipe",
    "mediapipe"
) $files

Feature "Fist gesture" @(
    "fist",
    "FIST"
) $files

Feature "Face recognition/security" @(
    "face_security",
    "face",
    "Face"
) $files

Feature "Camera input" @(
    "VideoCapture",
    "camera"
) $files

# ============================================================
# MODES
# ============================================================

Write-Host ""
Write-Host "================ SPIDEY MODES ================" -ForegroundColor Magenta

Feature "Standby mode" @(
    "STANDBY",
    "standby"
) $files

Feature "Listening mode" @(
    "LISTENING",
    "Listening"
) $files

Feature "Sleep mode" @(
    "SLEEP",
    "sleep"
) $files

Feature "Wake from sleep" @(
    "wake.*sleep",
    "sleep.*wake"
) $files

Feature "Thinking/processing state" @(
    "THINKING",
    "thinking"
) $files

# ============================================================
# HUD
# ============================================================

Write-Host ""
Write-Host "================ HUD / UI ================" -ForegroundColor Magenta

Feature "Native desktop HUD" @(
    "run_spidey_hud_native",
    "8765"
) $files

Feature "HUD state updates" @(
    "update_hud",
    "/api/state",
    "state"
) $files

Feature "HUD command API" @(
    "/api/command"
) $files

Feature "HUD typed input box" @(
    "commandBox",
    "id=.*command",
    "placeholder"
) $files

Feature "HUD Enter-to-submit" @(
    "keydown",
    "Enter"
) $files

# ============================================================
# N8N / HERMES
# ============================================================

Write-Host ""
Write-Host "================ HERMES / N8N ================" -ForegroundColor Magenta

Feature "HERMES references" @(
    "HERMES",
    "hermes"
) $files

Feature "n8n integration" @(
    "n8n",
    "N8N",
    "webhook"
) $files

# ============================================================
# LIVE STATUS
# ============================================================

Write-Host ""
Write-Host "================ LIVE STATUS ================" -ForegroundColor Magenta

$port = Get-NetTCPConnection -LocalPort 8765 -ErrorAction SilentlyContinue

if ($port) {
    TestLive "HUD server port 8765" $true
} else {
    TestLive "HUD server port 8765" $false
}

$proc = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -match "main\.py" }

if ($proc) {
    TestLive "SPIDEY main.py process" $true
} else {
    TestLive "SPIDEY main.py process" $false
}

# ============================================================
# SYNTAX OF CURRENT CORE FILES ONLY
# ============================================================

Write-Host ""
Write-Host "================ CURRENT CORE FILES ================" -ForegroundColor Magenta

$currentFiles = @(
    ".\main.py",
    ".\tools.py",
    ".\ai_router.py",
    ".\memory.py",
    ".\alarm_manager.py",
    ".\screen_analyzer.py",
    ".\screen_ocr.py",
    ".\screen_vision.py",
    ".\face_security.py",
    ".\spidey_web\run_spidey_hud_native.py"
)

foreach ($f in $currentFiles) {
    if (Test-Path $f) {
        python -m py_compile $f 2>$null

        if ($LASTEXITCODE -eq 0) {
            Write-Host "[ OK ] Syntax: $f" -ForegroundColor Green
        } else {
            Write-Host "[FAIL] Syntax: $f" -ForegroundColor Red
        }
    }
}

# ============================================================
# FINAL
# ============================================================

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "                  SPIDEY FEATURE REPORT" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Features with code/wiring detected : $implemented" -ForegroundColor Green
Write-Host "Features not detected              : $missing" -ForegroundColor Red
Write-Host "Features requiring live testing    : $needsTest" -ForegroundColor Yellow

Write-Host ""
Write-Host "IMPORTANT:" -ForegroundColor Yellow
Write-Host "GREEN = feature appears implemented/wired."
Write-Host "LIVE  = feature is currently running and can be tested."
Write-Host "RED   = feature was not detected in the current code."
Write-Host ""
Write-Host "This audit does NOT modify your SPIDEY code." -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
