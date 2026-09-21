from pathlib import Path

p = Path("main.py")
s = p.read_text(encoding="utf-8")

# Backup
Path("main_backup_before_ai_trace.py").write_text(s, encoding="utf-8")

# Add trace before Ollama call
old = '''            try:

                response = ollama.chat('''

new = '''            try:

                print("AI TRACE 1: ENTERED OLLAMA TRY")
                print("AI TRACE 2: USER INPUT =", repr(user_input))
                print("AI TRACE 3: MESSAGE COUNT =", len(messages))

                response = ollama.chat('''

if old not in s:
    raise SystemExit("OLLAMA START NOT FOUND")

s = s.replace(old, new, 1)

# Add trace after Ollama call
old = '''                reply = response[
                        "message"
                    ][
                        "content"
                    ]'''

new = '''                print("AI TRACE 4: OLLAMA RETURNED")
                print("AI TRACE 5: RESPONSE TYPE =", type(response).__name__)

                reply = response[
                        "message"
                    ][
                        "content"
                    ]

                print("AI TRACE 6: REPLY =", repr(reply))'''

if old not in s:
    raise SystemExit("REPLY BLOCK NOT FOUND")

s = s.replace(old, new, 1)

# Replace error handler
old = '''            except Exception as e:

                print(
                    "AI error:",
                    e
                )'''

new = '''            except Exception as e:

                import traceback
                print("AI TRACE ERROR")
                print("ERROR TYPE:", type(e).__name__)
                print("ERROR:", repr(e))
                traceback.print_exc()'''

if old not in s:
    raise SystemExit("ERROR BLOCK NOT FOUND")

s = s.replace(old, new, 1)

p.write_text(s, encoding="utf-8")

print("AI TRACE PATCH APPLIED")
print("BACKUP: main_backup_before_ai_trace.py")
