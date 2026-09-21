Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "                 SPIDEY FULL SYSTEM CHECK" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$root = (Get-Location).Path
$errors = 0
$warnings = 0

function OK($msg) {
    Write-Host "[ OK ] $msg" -ForegroundColor Green
}

function FAIL($msg) {
    Write-Host "[FAIL] $msg" -ForegroundColor Red
    $script:errors++
}

function WARN($msg) {
    Write-Host "[WARN] $msg" -ForegroundColor Yellow
    $script:warnings++
}

function INFO($msg) {
    Write-Host "[INFO] $msg" -ForegroundColor Gray
}

# ============================================================
# 1. PROJECT ROOT
# ============================================================

Write-Host ""
Write-Host "---- PROJECT STRUCTURE ----" -ForegroundColor Magenta

if (Test-Path ".\main.py") {
    OK "main.py exists"
} else {
    FAIL "main.py missing"
}

if (Test-Path ".\spidey_web") {
    OK "spidey_web folder exists"
} else {
    FAIL "spidey_web folder missing"
}

if (Test-Path ".\spidey_web\index.html") {
    OK "HUD index.html exists"
} else {
    FAIL "HUD index.html missing"
}

if (Test-Path ".\spidey_web\app.js") {
    OK "HUD app.js exists"
} else {
    FAIL "HUD app.js missing"
}

if (Test-Path ".\spidey_web\run_spidey_hud_native.py") {
    OK "Native HUD server exists"
} else {
    FAIL "Native HUD server missing"
}

# ============================================================
# 2. VIRTUAL ENVIRONMENT
# ============================================================

Write-Host ""
Write-Host "---- PYTHON ENVIRONMENT ----" -ForegroundColor Magenta

if ($env:VIRTUAL_ENV) {
    OK "Virtual environment active"
    INFO "VENV: $env:VIRTUAL_ENV"
} else {
    WARN "Virtual environment is not currently active"
}

$pythonVersion = python --version 2>&1

if ($LASTEXITCODE -eq 0) {
    OK "Python available"
    INFO "$pythonVersion"
} else {
    FAIL "Python command unavailable"
}

# ============================================================
# 3. PYTHON SYNTAX
# ============================================================

Write-Host ""
Write-Host "---- PYTHON SYNTAX ----" -ForegroundColor Magenta

$pyFiles = Get-ChildItem -Path "." -Recurse -Filter "*.py" -File |
    Where-Object {
        $_.FullName -notmatch "\\venv\\" -and
        $_.FullName -notmatch "\\__pycache__\\"
    }

foreach ($file in $pyFiles) {

    python -m py_compile "$($file.FullName)" 2>$null

    if ($LASTEXITCODE -eq 0) {
        OK "Syntax: $($file.FullName.Substring($root.Length + 1))"
    } else {
        FAIL "Syntax error: $($file.FullName.Substring($root.Length + 1))"
    }
}

# ============================================================
# 4. IMPORTANT FILES
# ============================================================

Write-Host ""
Write-Host "---- IMPORTANT SPIDEY FILES ----" -ForegroundColor Magenta

$importantFiles = @(
    "main.py",
    "spidey_web\index.html",
    "spidey_web\app.js",
    "spidey_web\run_spidey_hud_native.py"
)

foreach ($file in $importantFiles) {

    if (Test-Path $file) {

        $size = (Get-Item $file).Length

        if ($size -gt 0) {
            OK "$file ($size bytes)"
        } else {
            FAIL "$file is empty"
        }

    } else {
        FAIL "$file missing"
    }
}

# ============================================================
# 5. TYPED COMMAND BRIDGE
# ============================================================

Write-Host ""
Write-Host "---- TYPED COMMAND BRIDGE ----" -ForegroundColor Magenta

if (Test-Path ".\typed_command.txt") {

    INFO "typed_command.txt currently exists"

    $content = Get-Content ".\typed_command.txt" -Raw

    if ($content.Trim()) {
        WARN "typed_command.txt contains pending input: $($content.Trim())"
    } else {
        OK "typed_command.txt is empty"
    }

} else {
    OK "typed_command.txt does not currently exist (normal)"
}

$mainText = Get-Content ".\main.py" -Raw
$appText = Get-Content ".\spidey_web\app.js" -Raw
$hudText = Get-Content ".\spidey_web\run_spidey_hud_native.py" -Raw

if ($mainText -match "TYPED_COMMAND_FILE") {
    OK "main.py contains typed-command bridge"
} else {
    FAIL "main.py typed-command bridge missing"
}

if ($mainText -match "pop_typed_command") {
    OK "pop_typed_command() exists"
} else {
    FAIL "pop_typed_command() missing"
}

if ($mainText -match "TYPED COMMAND RECEIVED") {
    OK "Typed command listener active"
} else {
    WARN "Typed command listener marker not found"
}

if ($appText -match "/api/command") {
    OK "HUD sends commands to /api/command"
} else {
    FAIL "HUD /api/command endpoint wiring missing"
}

if ($appText -match "commandBox") {
    OK "HUD command input exists"
} else {
    FAIL "HUD command input not found"
}

if ($appText -match "Enter") {
    OK "HUD Enter-key handling exists"
} else {
    WARN "HUD Enter-key handler not detected"
}

if ($hudText -match "/api/command") {
    OK "HUD server has /api/command"
} else {
    FAIL "HUD server /api/command missing"
}

# ============================================================
# 6. HUD SERVER PORT
# ============================================================

Write-Host ""
Write-Host "---- HUD SERVER ----" -ForegroundColor Magenta

$portCheck = Get-NetTCPConnection -LocalPort 8765 -ErrorAction SilentlyContinue

if ($portCheck) {

    OK "Port 8765 is active"

    foreach ($conn in $portCheck) {
        INFO "State: $($conn.State) | PID: $($conn.OwningProcess)"
    }

} else {

    WARN "Port 8765 is not currently active"
    INFO "This is normal if SPIDEY is not running."
}

# ============================================================
# 7. HUD API TEST
# ============================================================

Write-Host ""
Write-Host "---- HUD API ----" -ForegroundColor Magenta

try {

    $response = Invoke-WebRequest `
        -Uri "http://127.0.0.1:8765/" `
        -UseBasicParsing `
        -TimeoutSec 3 `
        -ErrorAction Stop

    if ($response.StatusCode -eq 200) {
        OK "HUD server responds on http://127.0.0.1:8765/"
    } else {
        WARN "HUD returned HTTP $($response.StatusCode)"
    }

} catch {

    WARN "HUD server is not responding"
    INFO "Start SPIDEY first if you want a live HUD test."
}

# ============================================================
# 8. FRONTEND FILE REFERENCES
# ============================================================

Write-Host ""
Write-Host "---- HUD FRONTEND REFERENCES ----" -ForegroundColor Magenta

$indexText = Get-Content ".\spidey_web\index.html" -Raw

if ($indexText -match "app\.js") {
    OK "index.html loads app.js"
} else {
    FAIL "index.html does not reference app.js"
}

if ($indexText -match "<body") {
    OK "index.html contains body"
} else {
    FAIL "index.html appears malformed"
}

# ============================================================
# 9. REQUIRED PYTHON MODULES
# ============================================================

Write-Host ""
Write-Host "---- PYTHON DEPENDENCIES ----" -ForegroundColor Magenta

$modules = @(
    "numpy",
    "sounddevice",
    "keyboard",
    "requests"
)

foreach ($module in $modules) {

    python -c "import $module" 2>$null

    if ($LASTEXITCODE -eq 0) {
        OK "Python module: $module"
    } else {
        WARN "Python module missing/unavailable: $module"
    }
}

# ============================================================
# 10. MAIN PYTHON IMPORT TEST
# ============================================================

Write-Host ""
Write-Host "---- MAIN.PY IMPORT TEST ----" -ForegroundColor Magenta

python -c "import main" 2>$null

if ($LASTEXITCODE -eq 0) {
    OK "main.py imports successfully"
} else {
    FAIL "main.py import failed"
}

# ============================================================
# 11. BACKUPS / RECOVERY
# ============================================================

Write-Host ""
Write-Host "---- BACKUPS ----" -ForegroundColor Magenta

$backups = Get-ChildItem "." -Filter "main.py.before*" -File -ErrorAction SilentlyContinue

if ($backups) {

    foreach ($backup in $backups) {
        OK "Backup available: $($backup.Name)"
    }

} else {
    WARN "No main.py backup files found"
}

# ============================================================
# 12. DUPLICATE / TEMP FILE CHECK
# ============================================================

Write-Host ""
Write-Host "---- TEMP / DEBUG FILES ----" -ForegroundColor Magenta

$tempFiles = Get-ChildItem "." -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object {
        $_.FullName -notmatch "\\venv\\" -and
        $_.FullName -notmatch "\\__pycache__\\" -and
        $_.Name -match "^(debug|test|tmp|temp).*"
    }

if ($tempFiles) {

    foreach ($file in $tempFiles) {
        WARN "Possible temp/debug file: $($file.FullName.Substring($root.Length + 1))"
    }

} else {
    OK "No obvious temp/debug files detected"
}

# ============================================================
# 13. SPIDEY PROCESS CHECK
# ============================================================

Write-Host ""
Write-Host "---- SPIDEY PROCESS ----" -ForegroundColor Magenta

$spideyProcesses = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
    Where-Object {
        $_.CommandLine -match "main\.py"
    }

if ($spideyProcesses) {

    foreach ($process in $spideyProcesses) {
        OK "SPIDEY process running | PID: $($process.ProcessId)"
    }

} else {

    WARN "SPIDEY main.py process not detected"
    INFO "This is normal if SPIDEY is currently stopped."
}

# ============================================================
# 14. COMMAND ENGINE MARKERS
# ============================================================

Write-Host ""
Write-Host "---- COMMAND ENGINE ----" -ForegroundColor Magenta

$commandMarkers = @(
    "run_spidey",
    "listen",
    "listen_for_wake_word",
    "wait_for_space",
    "update_hud",
    "process_command"
)

foreach ($marker in $commandMarkers) {

    if ($mainText -match [regex]::Escape($marker)) {
        OK "Command engine marker: $marker"
    } else {
        WARN "Command engine marker not found: $marker"
    }
}

# ============================================================
# 15. PRODUCTIVITY FEATURE MARKERS
# ============================================================

Write-Host ""
Write-Host "---- PRODUCTIVITY FEATURES ----" -ForegroundColor Magenta

$features = @(
    "Meeting Notes",
    "Action Items",
    "Email Rewriter",
    "Presentation Outline",
    "LinkedIn Post",
    "Brainstorm",
    "Translation",
    "Study Notes"
)

foreach ($feature in $features) {

    $pattern = switch ($feature) {
        "Meeting Notes"       { "meeting|meeting notes|summar" }
        "Action Items"        { "action item|action items" }
        "Email Rewriter"      { "email|rewrite email" }
        "Presentation Outline"{ "presentation|outline" }
        "LinkedIn Post"       { "linkedin" }
        "Brainstorm"          { "brainstorm" }
        "Translation"         { "translat" }
        "Study Notes"         { "study notes|study" }
    }

    if ($mainText -match $pattern) {
        OK "$feature marker detected"
    } else {
        INFO "$feature not implemented yet"
    }
}

# ============================================================
# FINAL REPORT
# ============================================================

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "                    FINAL SPIDEY REPORT" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

if ($errors -eq 0) {

    Write-Host "                 SPIDEY CORE: HEALTHY" -ForegroundColor Green

} else {

    Write-Host "                 SPIDEY CORE: ISSUES FOUND" -ForegroundColor Red
}

Write-Host ""
Write-Host "Errors   : $errors" -ForegroundColor Red
Write-Host "Warnings : $warnings" -ForegroundColor Yellow
Write-Host ""

if ($errors -eq 0) {
    Write-Host "No critical structural problems detected." -ForegroundColor Green
}

Write-Host ""
Write-Host "NOTE: This check does NOT modify SPIDEY." -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
