import subprocess
import os

text = "Hello Soham. This is Jarvis speaking directly through Windows."

command = """
Add-Type -AssemblyName System.Speech
$speaker = New-Object System.Speech.Synthesis.SpeechSynthesizer
$speaker.Rate = 0
$speaker.Volume = 100
$speaker.Speak($env:JARVIS_TEXT)
$speaker.Dispose()
"""

env = os.environ.copy()
env["JARVIS_TEXT"] = text

subprocess.run(
    ["powershell", "-NoProfile", "-Command", command],
    env=env
)

print("Speech test finished.")