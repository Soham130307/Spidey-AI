import subprocess

print("Playing JARVIS voice...")

subprocess.run(
    [
        "powershell",
        "-Command",
        "Start-Process '.\\jarvis_test.mp3' -Wait"
    ]
)

print("Finished.")