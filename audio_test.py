import subprocess
import os

file_path = os.path.abspath("jarvis_test.mp3")

print("Playing JARVIS voice...")

command = f'''
Add-Type -AssemblyName PresentationCore
$player = New-Object System.Windows.Media.MediaPlayer
$player.Open([Uri]::new("{file_path}"))
$player.Play()
Start-Sleep -Seconds 5
$player.Stop()
$player.Close()
'''

subprocess.run(
    ["powershell", "-NoProfile", "-Command", command],
    check=True
)

print("Finished.")